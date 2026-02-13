import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Re:Kite - Spaced Repetition Learning",
  description: "Master concepts through spaced repetition learning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
