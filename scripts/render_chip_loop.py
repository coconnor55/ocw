#!/usr/bin/env python3
"""Render the OCW hero with a live chip-die window.

The die plays a 7-second seamless loop: steampunk factory plate plus
steam, belt travel, and electrical pulses. Writes a high-res MP4 and GIF.
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
HERO_PATH = ROOT / "public" / "ocw-hero.png"
FACTORY_PATH = (
    Path.home()
    / ".cursor/projects/Users-clintoconnor-Documents-GitHub-ocw/assets/factory-die.png"
)
OUT_MP4 = ROOT / "public" / "ocw-chip-loop.mp4"
OUT_GIF = ROOT / "public" / "ocw-chip-loop.gif"

SCALE = 2
FPS = 30
DURATION = 7.0
FRAMES = int(FPS * DURATION)
GIF_FPS = 15
GIF_SCALE = 1440  # square px

# Chip-die window on the 1024 source, just inside the central pin rows.
DIE = (368, 314, 656, 664)  # x0, y0, x1, y1
BEZEL = 11  # source px


def load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)


def logo_alpha(hero: np.ndarray, die: tuple[int, int, int, int]) -> np.ndarray:
    """Soft mask of the wordmark and wave inside the die only."""
    x0, y0, x1, y1 = die
    region = hero[y0:y1, x0:x1].astype(np.float32)
    r, g, b = region[:, :, 0], region[:, :, 1], region[:, :, 2]
    white = np.clip((np.minimum(np.minimum(r, g), b) - 145.0) / 70.0, 0, 1)
    cyan_score = np.minimum(g, b) - r
    cyan = np.clip((cyan_score - 35.0) / 70.0, 0, 1)
    cyan *= np.clip((np.maximum(g, b) - 100.0) / 40.0, 0, 1)
    return np.maximum(white, cyan)


def upscale(img: Image.Image, scale: int) -> Image.Image:
    return img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS)


def polyline_lengths(points: list[tuple[float, float]]) -> tuple[list[float], float]:
    lengths = [0.0]
    total = 0.0
    for i in range(1, len(points)):
        dx = points[i][0] - points[i - 1][0]
        dy = points[i][1] - points[i - 1][1]
        total += math.hypot(dx, dy)
        lengths.append(total)
    return lengths, total


def point_along(points: list[tuple[float, float]], lengths: list[float], total: float, u: float) -> tuple[float, float]:
    if total <= 0:
        return points[0]
    dist = (u % 1.0) * total
    for i in range(1, len(points)):
        if lengths[i] >= dist:
            span = lengths[i] - lengths[i - 1]
            t = 0 if span == 0 else (dist - lengths[i - 1]) / span
            x = points[i - 1][0] + (points[i][0] - points[i - 1][0]) * t
            y = points[i - 1][1] + (points[i][1] - points[i - 1][1]) * t
            return x, y
    return points[-1]


# Factory-space paths (0–1). Tuned to the generated plate: belts, bus bars, tube runs.
BELT_PATHS = [
    [(0.46, 0.02), (0.47, 0.18), (0.44, 0.34)],
    [(0.18, 0.22), (0.34, 0.30), (0.48, 0.26)],
    [(0.62, 0.58), (0.78, 0.62), (0.92, 0.55)],
    [(0.08, 0.72), (0.22, 0.80), (0.40, 0.86)],
]
PULSE_PATHS = [
    [(0.08, 0.18), (0.28, 0.16), (0.48, 0.20), (0.70, 0.14), (0.92, 0.18)],
    [(0.12, 0.78), (0.30, 0.62), (0.48, 0.48), (0.66, 0.40), (0.88, 0.32)],
    [(0.50, 0.08), (0.52, 0.28), (0.49, 0.48), (0.54, 0.70), (0.50, 0.94)],
    [(0.72, 0.22), (0.80, 0.36), (0.74, 0.52), (0.86, 0.68), (0.78, 0.88)],
    [(0.20, 0.42), (0.32, 0.50), (0.28, 0.66), (0.18, 0.84)],
    [(0.60, 0.30), (0.74, 0.42), (0.90, 0.48)],
]
GEAR_CENTERS = [
    (0.22, 0.58, 0.10, 2),
    (0.30, 0.78, 0.07, 3),
    (0.16, 0.74, 0.05, -2),
    (0.83, 0.46, 0.08, 2),
    (0.78, 0.70, 0.06, -3),
    (0.40, 0.84, 0.045, 4),
]


def make_puff(diameter: int) -> np.ndarray:
    img = Image.new("L", (diameter, diameter), 0)
    draw = ImageDraw.Draw(img)
    pad = max(2, int(diameter * 0.32))
    draw.ellipse((pad, pad, diameter - 1 - pad, diameter - 1 - pad), fill=255)
    blurred = img.filter(ImageFilter.GaussianBlur(radius=diameter * 0.22))
    return np.asarray(blurred, dtype=np.float32) / 255.0


def stamp(canvas: np.ndarray, sprite: np.ndarray, cx: int, cy: int, alpha: float) -> None:
    h, w = canvas.shape
    sh, sw = sprite.shape
    x0, y0 = cx - sw // 2, cy - sh // 2
    x1, y1 = x0 + sw, y0 + sh
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x0 >= x1 or y0 >= y1:
        return
    patch = sprite[sy0 : sy0 + (y1 - y0), sx0 : sx0 + (x1 - x0)] * alpha
    canvas[y0:y1, x0:x1] = np.maximum(canvas[y0:y1, x0:x1], patch)


PUFFS = {size: make_puff(size) for size in (18, 28, 42, 64)}


def build_factory_frame(factory: Image.Image, size: tuple[int, int], t: float) -> np.ndarray:
    """Return an RGB frame of the factory sized to the die interior."""
    width, height = size
    margin = 18
    zoom = factory.resize((width + margin * 2, height + margin * 2), Image.Resampling.LANCZOS)
    ox = int(margin + 7 * math.sin(2 * math.pi * t / DURATION))
    oy = int(margin + 5 * math.sin(4 * math.pi * t / DURATION))
    crop = zoom.crop((ox, oy, ox + width, oy + height))
    base = np.asarray(crop, dtype=np.float32)

    # Tube / arc throb already in the plate, pushed so the right side "thinks".
    beat = 0.5 + 0.5 * math.sin(2 * math.pi * 4 * t / DURATION)
    beat2 = 0.5 + 0.5 * math.sin(2 * math.pi * 2 * t / DURATION + 1.2)
    yy = np.linspace(0, 1, height, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, width, dtype=np.float32)[None, :]
    energy = (0.08 + 0.22 * beat) * np.clip((xx - 0.45) * 1.6, 0, 1)
    energy = energy + (0.05 + 0.12 * beat2) * np.exp(
        -((xx - 0.5) ** 2 + (yy - 0.45) ** 2) / 0.08
    )
    base[:, :, 1] += energy * 28
    base[:, :, 2] += energy * 46

    glow = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(glow)
    core = Image.new("RGB", (width, height), (0, 0, 0))
    core_draw = ImageDraw.Draw(core)

    def to_px(pt: tuple[float, float]) -> tuple[int, int]:
        return int(pt[0] * (width - 1)), int(pt[1] * (height - 1))

    for index, path in enumerate(PULSE_PATHS):
        lengths, total = polyline_lengths(path)
        speed = 1 + (index % 3)  # integer laps per loop
        head = (speed * t / DURATION + index * 0.17) % 1.0
        tail_steps = 14
        for step in range(tail_steps):
            u = head - step * 0.012 * (1.2 if index % 2 == 0 else 0.8)
            x, y = to_px(point_along(path, lengths, total, u))
            fade = 1 - step / tail_steps
            radius = int(2 + fade * (7 if step < 3 else 4))
            color = (
                int(180 * fade),
                int(245 * fade),
                255,
            )
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
            if step < 4:
                core_draw.ellipse(
                    (x - 2, y - 2, x + 2, y + 2),
                    fill=(255, 255, 255),
                )
        # fork spark near the head
        hx, hy = to_px(point_along(path, lengths, total, head))
        spark = 0.5 + 0.5 * math.sin(2 * math.pi * (6 * t / DURATION + index))
        if spark > 0.55:
            draw.line(
                (hx, hy, hx + int(18 * spark), hy - int(10 * spark)),
                fill=(120, 220, 255),
                width=2,
            )

    for index, path in enumerate(BELT_PATHS):
        lengths, total = polyline_lengths(path)
        laps = 2 + index % 2
        for dash in range(8):
            u = (laps * t / DURATION + dash / 8 + index * 0.05) % 1.0
            x, y = to_px(point_along(path, lengths, total, u))
            x2, y2 = to_px(point_along(path, lengths, total, u + 0.025))
            draw.line((x, y, x2, y2), fill=(90, 62, 28), width=4)
            core_draw.line((x, y, x2, y2), fill=(214, 170, 90), width=2)

    for cx, cy, radius, turns in GEAR_CENTERS:
        x, y = to_px((cx, cy))
        rad = int(radius * width)
        angle = 2 * math.pi * turns * t / DURATION
        x2 = int(x + math.cos(angle) * rad)
        y2 = int(y + math.sin(angle) * rad)
        core_draw.line((x, y, x2, y2), fill=(255, 226, 170), width=2)
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 210, 120))

    glow_np = np.asarray(glow.filter(ImageFilter.GaussianBlur(radius=5)), dtype=np.float32)
    core_np = np.asarray(core.filter(ImageFilter.GaussianBlur(radius=1)), dtype=np.float32)
    base += glow_np * (0.85 + 0.35 * beat)
    base += core_np * 0.95

    steam_a = np.zeros((height, width), dtype=np.float32)
    rng = np.random.default_rng(7)
    for i in range(36):
        px = float(rng.random())
        py0 = float(rng.random())
        size_key = (18, 28, 42, 64)[i % 4]
        sprite = PUFFS[size_key]
        speed = 0.55 + (i % 5) * 0.12
        y = (py0 - speed * t / DURATION) % 1.0
        x = (px + 0.02 * math.sin(2 * math.pi * (t / DURATION + i))) % 1.0
        stamp(steam_a, sprite, int(x * width), int(y * height), 0.10 + (i % 4) * 0.035)
    base = base * (1 - steam_a[:, :, None] * 0.65) + 235 * steam_a[:, :, None]

    # Recessed vignette so the die reads as a cavity, not a sticker.
    vx = np.abs(xx - 0.5) * 2
    vy = np.abs(yy - 0.5) * 2
    vignette = np.clip(1 - 0.45 * np.maximum(vx, vy) ** 2, 0.55, 1)
    base *= vignette[:, :, None]
    return np.clip(base, 0, 255).astype(np.uint8)


def metal_bezel(width: int, height: int) -> Image.Image:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=10, fill=(8, 10, 12, 255))
    inset = 3
    draw.rounded_rectangle(
        (inset, inset, width - 1 - inset, height - 1 - inset),
        radius=8,
        outline=(150, 214, 230, 180),
        width=2,
    )
    draw.rounded_rectangle(
        (inset + 3, inset + 3, width - 4 - inset, height - 4 - inset),
        radius=6,
        outline=(40, 48, 54, 255),
        width=4,
    )
    return img


def compose_frame(hero: np.ndarray, alpha: np.ndarray, factory_frame: np.ndarray, die: tuple[int, int, int, int], bezel_px: int) -> np.ndarray:
    frame = hero.copy()
    x0, y0, x1, y1 = die
    bezel = metal_bezel(x1 - x0, y1 - y0)
    bezel_np = np.asarray(bezel, dtype=np.float32)
    ba = bezel_np[:, :, 3:4] / 255.0
    region = frame[y0:y1, x0:x1].astype(np.float32)
    region = region * (1 - ba) + bezel_np[:, :, :3] * ba
    ix0, iy0 = bezel_px, bezel_px
    ix1, iy1 = (x1 - x0) - bezel_px, (y1 - y0) - bezel_px
    inner = region[iy0:iy1, ix0:ix1]
    fact = factory_frame
    if fact.shape[0] != inner.shape[0] or fact.shape[1] != inner.shape[1]:
        fact = np.asarray(
            Image.fromarray(factory_frame).resize((inner.shape[1], inner.shape[0]), Image.Resampling.LANCZOS),
            dtype=np.uint8,
        )
    inner[:] = fact
    a = alpha[:, :, None]
    src = hero[y0 + iy0 : y0 + iy1, x0 + ix0 : x0 + ix1].astype(np.float32)
    inner[:] = (inner.astype(np.float32) * (1 - a) + src * a).astype(np.uint8)
    region[iy0:iy1, ix0:ix1] = inner
    frame[y0:y1, x0:x1] = np.clip(region, 0, 255).astype(np.uint8)
    return frame


def render(preview: bool) -> None:
    hero_src = Image.open(HERO_PATH).convert("RGB")
    hero_img = upscale(hero_src, SCALE)
    hero = np.asarray(hero_img, dtype=np.uint8)
    die = tuple(v * SCALE for v in DIE)
    bezel_px = BEZEL * SCALE
    alpha_src = logo_alpha(np.asarray(hero_src, dtype=np.uint8), DIE)
    alpha_src = alpha_src[BEZEL:-BEZEL, BEZEL:-BEZEL]
    alpha_img = Image.fromarray((alpha_src * 255).astype(np.uint8), mode="L")
    inner_w = (DIE[2] - DIE[0] - 2 * BEZEL) * SCALE
    inner_h = (DIE[3] - DIE[1] - 2 * BEZEL) * SCALE
    alpha_img = alpha_img.resize((inner_w, inner_h), Image.Resampling.LANCZOS)
    alpha = np.asarray(alpha_img, dtype=np.float32) / 255.0

    factory = Image.open(FACTORY_PATH).convert("RGB")

    if preview:
        frame = compose_frame(
            hero,
            alpha,
            build_factory_frame(factory, (inner_w, inner_h), 1.6),
            die,
            bezel_px,
        )
        Image.fromarray(frame).save(ROOT / "preview-chip-frame.png", quality=95)
        print("wrote preview-chip-frame.png")
        return

    OUT_MP4.parent.mkdir(parents=True, exist_ok=True)
    mp4 = subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{hero.shape[1]}x{hero.shape[0]}",
            "-r",
            str(FPS),
            "-i",
            "-",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "16",
            "-preset",
            "medium",
            "-movflags",
            "+faststart",
            str(OUT_MP4),
        ],
        stdin=subprocess.PIPE,
    )
    gif_frames = ROOT / ".chip-gif-frames"
    if gif_frames.exists():
        for old in gif_frames.glob("*.png"):
            old.unlink()
    gif_frames.mkdir(exist_ok=True)

    gif_index = 0
    step = FPS // GIF_FPS
    for i in range(FRAMES):
        t = i / FPS
        factory_frame = build_factory_frame(factory, (inner_w, inner_h), t)
        frame = compose_frame(hero, alpha, factory_frame, die, bezel_px)
        assert mp4.stdin is not None
        mp4.stdin.write(frame.tobytes())
        if i % step == 0:
            gif = Image.fromarray(frame).resize((GIF_SCALE, GIF_SCALE), Image.Resampling.LANCZOS)
            gif.save(gif_frames / f"{gif_index:04d}.png")
            gif_index += 1
        if i % 30 == 0:
            print(f"frame {i}/{FRAMES}", flush=True)

    assert mp4.stdin is not None
    mp4.stdin.close()
    if mp4.wait() != 0:
        sys.exit("ffmpeg mp4 failed")

    gif_cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(GIF_FPS),
        "-i",
        str(gif_frames / "%04d.png"),
        "-filter_complex",
        "[0:v]split[a][b];[a]palettegen=stats_mode=diff:max_colors=256[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle",
        "-loop",
        "0",
        str(OUT_GIF),
    ]
    if subprocess.call(gif_cmd) != 0:
        sys.exit("ffmpeg gif failed")
    for old in gif_frames.glob("*.png"):
        old.unlink()
    gif_frames.rmdir()
    print("wrote", OUT_MP4)
    print("wrote", OUT_GIF)


if __name__ == "__main__":
    render(preview="--preview" in sys.argv)
