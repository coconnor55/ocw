import Image from "next/image";

export default function HomePage() {
  return (
    <main className="hero">
      <Image
        src="/ocw-hero-2.webp"
        alt="O'Connor Works"
        fill
        priority
        className="hero-image"
        sizes="100vw"
      />
    </main>
  );
}
