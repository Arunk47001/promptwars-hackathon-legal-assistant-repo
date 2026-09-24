import type { Metadata } from "next";
import { IBM_Plex_Mono, Noto_Sans_Kannada, Public_Sans, Source_Serif_4 } from "next/font/google";
import "./globals.css";
import TopNav from "@/components/TopNav";
import Footer from "@/components/Footer";
import { LanguageProvider } from "@/components/LanguageProvider";

const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
});

const publicSans = Public_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
  display: "swap",
});

const notoSansKannada = Noto_Sans_Kannada({
  subsets: ["kannada"],
  variable: "--font-kannada",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Namma Nyaya",
  description: "GenAI legal companion for Bengaluru — rental agreements and offer letters",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${sourceSerif.variable} ${publicSans.variable} ${plexMono.variable} ${notoSansKannada.variable}`}
    >
      <body>
        <LanguageProvider>
          <TopNav />
          {children}
          <Footer />
        </LanguageProvider>
      </body>
    </html>
  );
}
