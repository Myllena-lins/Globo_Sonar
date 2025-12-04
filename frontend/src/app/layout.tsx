import type {Metadata} from "next";
import "@/styles/globals.css";
import {fontSans, fontMono} from "@/lib/fonts";
import Header from "@/components/shared/header";
import {ThemeProvider} from "next-themes";
import {Footer} from "@/components/shared/footer";
import React from "react";
import {DynamicBreadcrumb} from "@/components/shared/dynamic-breadcrumb";
import {FluidGradientBackground} from "@/components/shared/background-svg";

export const metadata: Metadata = {
    title: "Sonar",
    description: "Um identificador de trilhas e gerador de EDL baseado em IA",
};

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="pt-BR" suppressHydrationWarning>
        <body
            className={`${fontSans.variable} ${fontMono.variable} font-sans bg-background text-foreground antialiased`}
        >

        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange

        >
            <div className="min-h-screen flex flex-col justify-between">
                <FluidGradientBackground/>
                <div className="container mx-auto px-6">
                    <Header/>
                    <DynamicBreadcrumb/>
                </div>
                <main>
                    {children}
                </main>
                <Footer/>
            </div>
        </ThemeProvider>
        </body>
        </html>
    );
}