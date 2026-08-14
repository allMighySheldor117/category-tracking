import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Codon Category Tracking",
  description: "Analysis workspace for codon mutation category tracking.",
};

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

