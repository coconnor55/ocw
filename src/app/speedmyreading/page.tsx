import type { Metadata } from "next";
import Image from "next/image";

export const metadata: Metadata = {
  title: "SpeedMyReading — Retired",
  description: "speedmyreading.com is available.",
};

const OCW_HOME = "https://oconnorworks.com";

export default function SpeedMyReadingRetiredPage() {
  return (
    <a className="retired" href={OCW_HOME}>
      <div className="retired-top">
        <h1 className="retired-title">Retired</h1>
        <Image
          src="/speedmyreading-home.png"
          alt="SpeedMyReading home screen"
          width={1024}
          height={768}
          className="retired-shot"
          style={{ width: "66.6667vw", height: "auto", aspectRatio: "4 / 3", objectFit: "contain" }}
          priority
        />
      </div>
      <div className="retired-bottom">
        <p className="retired-sub">speedmyreading.com is available</p>
      </div>
    </a>
  );
}
