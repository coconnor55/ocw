import type { Metadata } from "next";
import { RetiredPage } from "../../components/RetiredPage";

export const metadata: Metadata = {
  title: "SpeedMyReading — Retired",
  description: "speedmyreading.com is available.",
};

export default function SpeedMyReadingRetiredPage() {
  return (
    <RetiredPage
      imageSrc="/speedmyreading-home.png"
      imageAlt="SpeedMyReading home screen"
      imageWidth={1024}
      imageHeight={768}
      subtitle="speedmyreading.com is available"
    />
  );
}
