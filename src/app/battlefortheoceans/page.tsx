import type { Metadata } from "next";
import { RetiredPage } from "../../components/RetiredPage";

export const metadata: Metadata = {
  title: "Battle for the Oceans — Retired",
  description: "battlefortheoceans.com is available.",
};

export default function BattleForTheOceansRetiredPage() {
  return (
    <RetiredPage
      imageSrc="/battlefortheoceans-retired.jpg"
      imageAlt="Battle for the Oceans poster"
      imageWidth={832}
      imageHeight={1109}
      subtitle="battlefortheoceans.com is available"
    />
  );
}
