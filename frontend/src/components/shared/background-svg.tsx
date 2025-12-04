"use client";

import {motion} from "framer-motion";
import {useTheme} from "next-themes";
import {useEffect, useRef} from "react";
import {useState} from 'react';

export function FluidGradientBackground() {
    const {resolvedTheme} = useTheme();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const isDark = mounted ? resolvedTheme === "dark" : true;
    const containerRef = useRef<HTMLDivElement>(null);


    return (
        <motion.div
            ref={containerRef}
            className="fixed inset-0 -z-10 overflow-hidden"
            initial={{opacity: 0}}
            animate={{opacity: 1}}
            transition={{duration: 1.5, ease: "easeOut"}}
        >
            <motion.div
                className="absolute inset-0"
                style={{
                    transformStyle: "preserve-3d",
                }}
            >
                <motion.svg
                    width="100%"
                    height="100%"
                    viewBox="0 0 1920 1319"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    preserveAspectRatio="xMidYMid slice"
                    className="absolute inset-0 w-full h-full"
                >
                    <defs>
                        <filter id="fluid-blur">
                            <feGaussianBlur stdDeviation="100" result="blur">
                                <animate
                                    attributeName="stdDeviation"
                                    values="90;110;90"
                                    dur="4s"
                                    repeatCount="indefinite"
                                />
                            </feGaussianBlur>
                        </filter>

                        <linearGradient
                            id="fluid-gradient"
                            x1="-129"
                            y1="151.5"
                            x2="1793.5"
                            y2="1228"
                            gradientUnits="userSpaceOnUse"
                        >
                            <motion.stop
                                stopColor={mounted ? (isDark ? "#DB2777" : "#2563EB") : "#DB2777"}
                                offset="0%"
                                animate={mounted ? {
                                    stopColor: isDark
                                        ? ["#DB2777", "#361423", "#DB2777"]
                                        : ["#2563EB", "#a9c5f6", "#2563EB"]
                                } : undefined}
                                transition={{
                                    duration: 6,
                                    repeat: mounted ? Infinity : 0,
                                    ease: "easeInOut"
                                }}
                            />
                            <motion.stop
                                stopColor={mounted ? (isDark ? "#F59E0B" : "#06B6D4") : "#F59E0B"}
                                offset="84.6227%"
                                animate={mounted ? {
                                    stopColor: isDark
                                        ? ["#F59E0B", "#33280f", "#F59E0B"]
                                        : ["#06B6D4", "#b9f6ff", "#06B6D4"]
                                } : undefined}
                                transition={{
                                    duration: 8,
                                    repeat: mounted ? Infinity : 0,
                                    ease: "easeInOut",
                                    delay: 1
                                }}
                            />
                        </linearGradient>
                    </defs>

                    <g filter="url(#fluid-blur)">
                        <motion.path
                            d="M1880.5 525.5C1971.98 12.7196 3186.5 1287.5 1984.5 1100C782.5 912.5 -988 800 -67.5 719C853 638 -18.1142 0.5 9.5 0.5C1390.5 753.5 1789.02 1038.28 1880.5 525.5Z"
                            fill="url(#fluid-gradient)"
                            initial={{pathLength: 0, opacity: 0}}
                            animate={{
                                pathLength: 1,
                                opacity: 1,
                                scale: [1, 1.02, 1]
                            }}
                            transition={{
                                pathLength: {duration: 3, ease: "easeInOut"},
                                opacity: {duration: 2},
                                scale: {
                                    duration: 10,
                                    repeat: Infinity,
                                    ease: "easeInOut"
                                }
                            }}
                        />
                    </g>

                    <filter id="noiseFilter">
                        <feTurbulence
                            type="fractalNoise"
                            baseFrequency="0.65"
                            numOctaves="3"
                            stitchTiles="stitch"
                        >
                            <animate
                                attributeName="baseFrequency"
                                values="0.65;0.68;0.65"
                                dur="12s"
                                repeatCount="indefinite"
                            />
                        </feTurbulence>
                        <feColorMatrix type="saturate" values="0"/>
                        <feBlend in="SourceGraphic" mode="soft-light" result="noise"/>
                    </filter>

                    <motion.rect
                        width="100%"
                        height="100%"
                        filter="url(#noiseFilter)"
                        opacity={mounted ? (isDark ? 0.03 : 0.02) : 0.03}
                        animate={mounted ? {
                            opacity: isDark ? [0.03, 0.06, 0.03] : [0.02, 0.04, 0.02]
                        } : undefined}
                        transition={{
                            duration: 5,
                            repeat: mounted ? Infinity : 0,
                            ease: "easeInOut"
                        }}
                    />
                </motion.svg>
            </motion.div>


            {mounted && <GlassBubbles isDark={isDark}/>}
        </motion.div>
    );
}

function GlassBubbles({isDark}: { isDark: boolean }) {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return null;

    const bubbleConfigs = Array.from({length: 12}, (_, i) => ({
        id: i,
        size: Math.random() * 35 + 25,
        left: Math.random() * 100,
        top: Math.random() * 100,
        duration: Math.random() * 20 + 20,
        delay: Math.random() * 3,
        opacity: Math.random() * 0.2 + 0.1,
    }));

    return (
        <div className="absolute inset-0 overflow-hidden">
            {bubbleConfigs.map((bubble) => (
                <motion.div
                    key={bubble.id}
                    className={`
                        absolute rounded-full backdrop-blur-md
                        ${isDark
                        ? "bg-gradient-to-br from-pink-500/55 to-yellow-400/60 border border-pink-400/70"
                        : "bg-gradient-to-br from-blue-500/55 to-cyan-400/80 border border-blue-400/40"
                    }
                    `}
                    style={{
                        width: bubble.size,
                        height: bubble.size,
                        left: `${bubble.left}%`,
                        top: `${bubble.top}%`,
                        opacity: bubble.opacity,
                        boxShadow: `
                            inset 0 2px 6px ${isDark ? 'rgba(219, 39, 119, 0.25)' : 'rgba(59, 130, 246, 0.25)'},
                            inset 0 -2px 4px ${isDark ? 'rgba(245, 158, 11, 0.15)' : 'rgba(6, 182, 212, 0.15)'},
                            0 4px 10px ${isDark ? 'rgba(219, 39, 119, 0.1)' : 'rgba(37, 99, 235, 0.1)'}
                        `,
                    }}
                    animate={{
                        y: [0, -60, -100, -80, -20, 0],
                        x: [0, 15, -10, 8, -3, 0],
                        scale: [1, 1.05, 1.08, 1.05, 0.95, 1],
                        opacity: [
                            bubble.opacity,
                            bubble.opacity * 1.3,
                            bubble.opacity * 0.7,
                            bubble.opacity * 1.1,
                            bubble.opacity * 0.9,
                            bubble.opacity
                        ],
                        rotate: [0, 3, -2, 1, -1, 0],
                    }}
                    transition={{
                        duration: bubble.duration,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: bubble.delay,
                        times: [0, 0.2, 0.4, 0.6, 0.8, 1],
                    }}
                />
            ))}

            {Array.from({length: 8}).map((_, i) => (
                <motion.div
                    key={`small-${i}`}
                    className={`
                        absolute rounded-full backdrop-blur-sm
                        ${isDark
                        ? "bg-yellow-400/8 border border-yellow-300/10"
                        : "bg-cyan-400/30 border border-cyan-300/60"
                    }
                    `}
                    style={{
                        width: Math.random() * 12 + 6,
                        height: Math.random() * 12 + 6,
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                        opacity: Math.random() * 0.3 + 0.1,
                    }}
                    animate={{
                        y: [0, -50, -80, -40, 0],
                        x: [0, 8, -5, 3, 0],
                        scale: [1, 1.03, 1.05, 1.03, 1],
                    }}
                    transition={{
                        duration: Math.random() * 15 + 15,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: Math.random() * 5,
                    }}
                />
            ))}
        </div>
    );
}