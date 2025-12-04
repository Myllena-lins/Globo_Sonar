import React from "react"
import { PlayPauseButton } from "../video-controls/play-pause-button"
import { VolumeControl } from "../video-controls/volume-control"
import { SkipSection } from "../video-controls/skip-section"
import { RateButton } from "../video-controls/rate-button"
import { FullscreenButton } from "../video-controls/fullscreen-button"
import {cn} from "@/lib/utils";
import baseGlass from "@/styles/baseGlass";
import type { VideoControlsProps } from "@/types";

export const VideoControls: React.FC<VideoControlsProps> = ({
    isPlaying,
    isMuted,
    volume,
    playbackRate,
    skipEmptySegments,
    onPlayPause,
    onMute,
    onVolumeChange,
    onNext,
    onSkipToggle,
    onRateChange,
    onFullscreen,
    currentTime,
    duration,
    formatTime
}) => {
    return (
        <div className="flex items-center gap-4 w-full">
            <PlayPauseButton isPlaying={isPlaying} onToggle={onPlayPause} className={cn(baseGlass, "rounded-full hover:bg-white/20 text-xs text-white px-3 py-1.5")}/>

            <div className="text-sm text-white/90 font-mono min-w-[100px]">
                {formatTime(currentTime)} / <span className="text-white/40">{formatTime(duration)}</span>
            </div>

            <VolumeControl isMuted={isMuted} volume={volume} onMute={onMute} onVolumeChange={onVolumeChange} className={cn(baseGlass, "flex items-center px-3 py-1.5 gap-2")}/>

            <div className="flex-1" />

            <SkipSection onNext={onNext} skipEmptySegments={skipEmptySegments} onSkipToggle={onSkipToggle} className={cn(baseGlass, "flex items-center px-3 py-1.5")}/>

            <RateButton rate={playbackRate} onClick={onRateChange} className={cn(baseGlass, "rounded-full hover:bg-white/20 text-xs text-white px-3 py-1.5")}/>

            <FullscreenButton onClick={onFullscreen} className={cn(baseGlass, "rounded-full hover:bg-white/20 text-xs text-white px-3 py-1.5")}/>
        </div>
    )
}
