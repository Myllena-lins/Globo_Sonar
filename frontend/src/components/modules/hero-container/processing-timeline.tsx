"use client";

import { motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import baseGlass from "@/styles/baseGlass";
import type { ProcessingTimelineProps } from "@/types";

export function ProcessingTimeline({
    steps,
    currentStep,
}: ProcessingTimelineProps) {



    return (
        <Card className={cn(baseGlass, "py-32")}>
            <CardContent>
                <div className="flex justify-center gap-24">
                    {steps.map((label, index) => {
                        const isActive = index === currentStep;
                        const isDone = index < currentStep;

                        return (
                            <div
                                key={index}
                                className="flex flex-col items-center"
                            >
                                <motion.div
                                    className={cn(
                                        "w-12 h-12 rounded-full flex items-center justify-center relative z-10",
                                        "border border-white/30 backdrop-blur-[11px]",
                                        "shadow-[0_8px_32px_rgba(0,0,0,0.1),inset_0_1px_0_rgba(255,255,255,0.4),inset_0_-1px_0_rgba(255,255,255,0.1),inset_0_0_54px_27px_rgba(255,255,255,0.03)]",
                                        isActive
                                            ? "bg-gradient-to-br from-primary/40 to-secondary/20"
                                            : isDone
                                                ? "bg-gradient-to-br from-primary/40 to-secondary/20"
                                                : "bg-gradient-to-br from-white/15 to-white/5"
                                    )}
                                    animate={
                                        isActive
                                            ? { scale: [1, 1.1, 1] }
                                            : { scale: 1 }
                                    }
                                    transition={
                                        isActive
                                            ? { repeat: Infinity, duration: 1.5, ease: "easeInOut" }
                                            : { duration: 0.4 }
                                    }
                                >
                                    {isDone ? (
                                        <Check className="w-5 h-5 text-primary drop-shadow-[0_0_8px_rgba(233,196,106,0.6)]" />
                                    ) : isActive ? (
                                        <Loader2 className="w-5 h-5 text-secondary animate-spin drop-shadow-[0_0_8px_rgba(231,111,81,0.6)]" />
                                    ) : (
                                        <div className="w-2.5 h-2.5 rounded-full bg-white/40" />
                                    )}
                                </motion.div>

                                <span className="text-sm text-center mt-2">
                                    {label}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}