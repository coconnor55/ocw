import Image from "next/image";

const OCW_HOME = "https://oconnorworks.com";

type RetiredPageProps = {
  imageSrc: string;
  imageAlt: string;
  imageWidth: number;
  imageHeight: number;
  subtitle: string;
};

export function RetiredPage({
  imageSrc,
  imageAlt,
  imageWidth,
  imageHeight,
  subtitle,
}: RetiredPageProps) {
  return (
    <a className="retired" href={OCW_HOME}>
      <div className="retired-top">
        <h1 className="retired-title">Retired</h1>
      </div>
      <div className="retired-media">
        <Image
          src={imageSrc}
          alt={imageAlt}
          width={imageWidth}
          height={imageHeight}
          className="retired-shot"
          priority
        />
      </div>
      <div className="retired-bottom">
        <p className="retired-sub">{subtitle}</p>
      </div>
    </a>
  );
}
