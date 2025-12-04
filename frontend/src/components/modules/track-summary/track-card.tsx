"use client"

import React from "react"
import {User, Disc} from "lucide-react"
import type {TrackCardProps} from "@/types"
import Image from "next/image"
import {TrackOccurrences} from "@/components/modules/track-summary/track-occurrences"
import {cn} from "@/lib/utils";
import baseGlass from "@/styles/baseGlass";


export function TrackCard({track}: TrackCardProps) {
    const hasMultipleOccurrences = track.occurrences.length > 1

    return (
        <div className={"rounded-xl mb-4"}>
            <div className="flex gap-4 mb-4">
                {track.imageUrl ? (
                    <Image
                        src={track.imageUrl}
                        alt={track.album}
                        className="h-full rounded-lg object-cover"
                    />
                ) : (
                    <div
                        className="flex w-32 h-32 border border-white/60 rounded-xl bg-muted text-muted-foreground items-center justify-center">
                        <Disc className="w-8 h-8 "/>
                    </div>
                )}

                <div className="flex-1">
                    <div className="flex items-start justify-between">
                        <div>
                            <h3 className="text-lg font-semibold mb-1">{track.name}</h3>
                            <p className="text-sm  mb-2">
                                {track.album}, {track.year}
                            </p>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-4 text-sm mb-2">
                        <div className="flex items-center gap-1 ">
                            <User className="w-4 h-4"/>
                            <span>{track.authors.join(", ")}</span>
                        </div>
                    </div>

                    <div className="flex gap-2 mb-3 flex-wrap">
                        {track.genres.map((genre, i) => (
                            <div className="text-xs flex flex-col gap-2" key={i}>
                                <strong>Gêneros:</strong>
                                <span
                                    key={i}
                                    className={cn(baseGlass, "flex items-center justify-center px-3 py-1 rounded-full")}
                                >
                                {genre}
                            </span>
                            </div>
                        ))}
                    </div>

                    <div className="flex gap-4 text-xs mb-2">
                        <span><strong>ISRC:</strong> {track.isrc}</span>
                        <span><strong>GMUSIC:</strong> {track.gmusic}</span>
                    </div>
                </div>
            </div>
            {track.occurrences.length > 0 && <TrackOccurrences
                occurrences={track.occurrences}
                hasMultiple={hasMultipleOccurrences}
            />}
        </div>
    )
}
