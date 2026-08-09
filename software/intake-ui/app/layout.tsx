import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

const description =
  "Private, participant-controlled credential review with evidence-based reports, technical detail, and document drafting.";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host");
  const protocol =
    requestHeaders.get("x-forwarded-proto") ??
    (host?.startsWith("localhost") ? "http" : "https");
  const baseUrl = new URL(`${protocol}://${host ?? "localhost:3000"}`);
  const socialImage = new URL("/og-v5.png", baseUrl).toString();

  return {
    metadataBase: baseUrl,
    title: {
      default: "PIA participant review",
      template: "%s · PIA intake",
    },
    description,
    openGraph: {
      title: "PIA participant review and document update",
      description,
      images: [{ url: socialImage, width: 1536, height: 1024 }],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: "PIA participant review and document update",
      description,
      images: [socialImage],
    },
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
