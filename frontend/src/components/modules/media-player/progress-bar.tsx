import React from "react"
import { Slider } from "../../ui/slider"
import { SegmentBar } from "./segment-bar"
import type { ProgressBarProps } from "@/types"

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  duration,
  isSeeking,
  isHovering,
  onSeek,
  onSeekStart,
  onSeekEnd,
  segments
}) => (
  <div className="relative w-full h-8 flex items-center">
    <div className={`z-30 absolute w-full h-2 top-1/2 left-0 -translate-y-1/2 pointer-events-none transition-opacity duration-200 ${isHovering ? 'opacity-100' : 'opacity-0'}`}>
      <SegmentBar segments={segments} duration={duration} />
    </div>
    <div className={`relative w-full z-10 transition-opacity duration-200 ${isHovering ? 'opacity-100' : 'opacity-0'}`}>
      <Slider
        value={[isSeeking ? value : value]}
        min={0}
        max={duration}
        step={0.01}
        onValueChange={v => onSeek(v[0])}
        onValueCommit={v => onSeekEnd(v[0])}
        onPointerDown={onSeekStart}
        className={"w-full h-2 z-10 bg-transparent"}
      />
    </div>
  </div>
)
