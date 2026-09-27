"use client";

import { useEffect, useRef, useState } from "react";

const MENU_ITEMS = [
  {
    label: "SpeedMyReading",
    href: "/speedmyreading",
  },
];

export function SiteMenu() {
  const [open, setOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };

    const onPointerDown = (event: MouseEvent) => {
      if (
        panelRef.current &&
        !panelRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("mousedown", onPointerDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("mousedown", onPointerDown);
    };
  }, [open]);

  return (
    <div className="site-menu" ref={panelRef}>
      <button
        type="button"
        className="menu-trigger"
        aria-expanded={open}
        aria-haspopup="true"
        aria-label="Open menu"
        onClick={() => setOpen((value) => !value)}
      >
        <span className="menu-line" />
        <span className="menu-line" />
        <span className="menu-line" />
      </button>

      {open && (
        <nav className="menu-panel" aria-label="Site navigation">
          <ul className="menu-list">
            {MENU_ITEMS.map((item) => (
              <li key={item.href}>
                <a className="menu-link" href={item.href}>
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      )}

      <style jsx>{`
        .site-menu {
          position: fixed;
          top: 1rem;
          right: 1rem;
          z-index: 50;
        }

        .menu-trigger {
          display: flex;
          flex-direction: column;
          justify-content: center;
          gap: 5px;
          width: 44px;
          height: 40px;
          padding: 0 10px;
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 8px;
          background: rgba(0, 0, 0, 0.55);
          backdrop-filter: blur(8px);
          cursor: pointer;
        }

        .menu-trigger:hover {
          background: rgba(0, 0, 0, 0.7);
        }

        .menu-line {
          display: block;
          height: 2px;
          width: 100%;
          background: #fff;
          border-radius: 1px;
        }

        .menu-panel {
          position: absolute;
          top: calc(100% + 0.5rem);
          right: 0;
          min-width: 220px;
          padding: 0.5rem;
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 10px;
          background: rgba(0, 0, 0, 0.78);
          backdrop-filter: blur(10px);
          box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
        }

        .menu-list {
          list-style: none;
          margin: 0;
          padding: 0;
        }

        .menu-link {
          display: block;
          padding: 0.65rem 0.75rem;
          color: #fff;
          text-decoration: none;
          font-size: 0.95rem;
          border-radius: 6px;
        }

        .menu-link:hover {
          background: rgba(255, 255, 255, 0.08);
        }
      `}</style>
    </div>
  );
}
