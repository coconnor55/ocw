import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SpeedMyReading — Retired",
  description: "This domain is available.",
};

const OCW_HOME = "https://oconnorworks.com";

export default function SpeedMyReadingRetiredPage() {
  return (
    <a className="retired" href={OCW_HOME}>
      <div className="retired-top">
        <h1 className="retired-title">Retired</h1>
      </div>
      <div className="retired-bottom">
        <p className="retired-sub">this domain is available</p>
      </div>
    </a>
  );
}
