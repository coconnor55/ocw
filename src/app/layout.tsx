import type { Metadata } from "next";
import "./globals.css";
import { SiteMenu } from "@/components/SiteMenu";

export const metadata: Metadata = {
  title: "O'Connor Works",
  description: "O'Connor Works — software and reading tools.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <SiteMenu />
        {children}
      </body>
    </html>
  );
}
