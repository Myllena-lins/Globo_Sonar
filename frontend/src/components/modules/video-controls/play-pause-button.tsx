import React from "react"
import { Button } from "../../ui/button"
import { Play, Pause } from "lucide-react"
import { cn } from "@/lib/utils"
import type { PlayPauseButtonProps } from "@/types"

export const PlayPauseButton: React.FC<PlayPauseButtonProps> = ({ isPlaying, onToggle, className }) => (
  <Button
    variant="glass"
    size="icon"
    onClick={onToggle}
    className={className ?? cn("rounded-full hover:bg-white/20 text-xs text-white px-3 py-1.5")}
  >
    {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 ml-0.5" />}
  </Button>
)
