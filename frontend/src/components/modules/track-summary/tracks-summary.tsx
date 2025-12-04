"use client"

import {useState} from "react"
import type {TracksSummaryProps} from "@/types"
import {TrackCard} from "./track-card"
import TrackSeparator from "./track-separator"
import baseGlass from "@/styles/baseGlass"
import {cn} from "@/lib/utils"
import {BsMusicNote} from "react-icons/bs";
import {Button} from "@/components/ui/button";
import {BiDetail} from "react-icons/bi";

export function TracksSummary({tracks}: TracksSummaryProps) {

    return (
        <div>
            <div className="w-full flex justify-between">
                <Button
                    variant={"glass"}
                    tone={"primary"}
                    className={"font-normal py-6 mb-6 gap-2 w-full rounded-xl"}
                    onClick={() => {
                    }}>
                    <BsMusicNote/>
                    <h2>Músicas Identificadas <span
                        className="text-sm">•</span> {tracks.length}</h2>
                </Button>
            </div>

            <div className={cn(baseGlass, "rounded-xl p-6")}>
                <div className="space-y-4">

                    {tracks.length === 0 && (
                        <p>Nennhuma música identificada.</p>
                    )}

                    {tracks.length > 0 &&
                        tracks.map((track, index) => (
                            <div key={index}>
                                <TrackCard track={track}/>
                                <TrackSeparator/>
                            </div>
                        ))
                    }
                </div>
            </div>
        </div>
    )
}
