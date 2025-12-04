import React from "react"
import type { SegmentBarProps } from "@/types"

export const SegmentBar: React.FC<SegmentBarProps> = ({ segments, duration }) => (
  <>
    {segments.map(segment => {
      const leftPct = (segment.startTime / duration) * 100
      const widthPct = ((segment.endTime - segment.startTime) / duration) * 100
      return (
        <div
          key={segment.id}
          className="absolute top-0 h-full rounded"
          style={{
            left: `${leftPct}%`,
            width: `${widthPct}%`,
            backgroundColor: segment.color,
            opacity: segment.isActive ? 1 : 0.4,
            zIndex: 20
          }}
        />
      )
    })}
  </>
)

