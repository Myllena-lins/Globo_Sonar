"use client"

import React, {useState, useId} from "react"
import {ChevronDown, Clock} from "lucide-react"
import type {TrackOccurrencesProps} from "@/types"
import {cn} from "@/lib/utils"
import baseGlass from "@/styles/baseGlass"
import {Button} from "../../ui/button"

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

export function TrackOccurrences({occurrences, hasMultiple}: TrackOccurrencesProps) {
    const [isOpen, setIsOpen] = useState(false)
    const id = useId()

    if (!hasMultiple) {
        const occurrence = occurrences[0]
        return (
            <div className={"w-full"}>

                <Button
                    variant="glass"
                    tone="secondary"
                    className={cn("px-4 h-8 z-20 flex items-center gap-2 w-full justify-between text-sm font-normal")}>
                    <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4"/>
                        <span>Timestamp: </span>
                    </div>
                    <span>{formatTime(occurrence.startTime)} - {formatTime(occurrence.endTime)}</span>
                </Button>
            </div>
        )
    }

    return (
        <div className={("w-full")}>
            <Button
                onClick={() => setIsOpen(!isOpen)}
                aria-expanded={isOpen}
                aria-controls={`occurrences-panel-${id}`}
                variant="glass"
                tone="primary"
                className={cn("px-4 h-8 z-20 w-full flex items-center justify-between duration-[0]")}
            >
                <div className="flex items-center gap-2 text-sm">
                    <Clock className="text-primary w-4 h-4"/>
                    <div className="flex gap-1">
                        <p>Ocorrências</p>
                        <span>•</span>
                        <span>{occurrences.length}</span>
                    </div>
                </div>
                <ChevronDown
                    className={cn(
                        "w-4 h-4 transition-transform",
                        isOpen && "rotate-180"
                    )}
                />
            </Button>

            <div
                id={`occurrences-panel-${id}`}
                role="region"
                aria-hidden={!isOpen}
                className={cn(
                    "transition-all duration-300 ease-out overflow-hidden",
                    isOpen ? "max-h-80 opacity-100" : "max-h-0 opacity-0"
                )}
            >
                <div className="pt-2 space-y-2 z-10">
                    {occurrences.map((occurrence, index) => (
                        <div
                            key={index}
                            className="flex items-center gap-2 p-2 rounded-2xl bg-primary/5 text-sm"
                        >
                            <Clock className="w-4 h-4 text-muted-foreground"/>
                            <span className="text-muted-foreground">
                {formatTime(occurrence.startTime)} • {formatTime(occurrence.endTime)}
              </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
