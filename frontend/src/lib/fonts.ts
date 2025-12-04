import { Ubuntu, Ubuntu_Mono } from "next/font/google";

export const fontSans = Ubuntu({
    subsets: ["latin"],
    weight: ["400", "500", "700"],
    variable: "--font-sans",
    display: "swap",
});

export const fontMono = Ubuntu_Mono({
    subsets: ["latin"],
    weight: ["400", "700"],
    variable: "--font-mono",
    display: "swap",
});
