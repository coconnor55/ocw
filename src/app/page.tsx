import Image from "next/image";

export default function HomePage() {
  return (
    <main className="hero">
      <Image
        src="/ocw-hero.png"
        alt="O'Connor Works"
        fill
        priority
        className="hero-image"
        sizes="100vw"
      />
    </main>
  );
}
