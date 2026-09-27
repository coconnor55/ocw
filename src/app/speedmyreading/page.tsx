import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "SpeedMyReading — Retired",
  description: "This domain is available.",
};

export default function SpeedMyReadingRetiredPage() {
  return (
    <main className="retired">
      <div className="retired-top">
        <h1 className="retired-title">Retired</h1>
      </div>
      <div className="retired-bottom">
        <p className="retired-sub">this domain is available</p>
      </div>
    </main>
  );
}
