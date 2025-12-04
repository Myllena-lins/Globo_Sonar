import React from "react"
import { Button } from "../../ui/button"
import { Volume2, VolumeX } from "lucide-react"
import { Slider } from "../../ui/slider"
import { cn } from "@/lib/utils"
import baseGlass from "@/styles/baseGlass"
import type { VolumeControlProps } from "@/types"

export const VolumeControl: React.FC<VolumeControlProps> = ({ isMuted, volume, onMute, onVolumeChange, className }) => (
  <div className={className ?? cn(baseGlass, "flex items-center px-3 py-1.5 gap-2")}>
    <Button variant="ghost" size="icon" onClick={onMute} className="h-8 w-8 rounded-full hover:bg-white/20 text-white p-0">
      {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
    </Button>
    <div className="w-32">
      <Slider
        value={[isMuted ? 0 : volume]}
        onValueChange={val => onVolumeChange(Number(val[0]))}
        min={0}
        max={1}
        step={0.01}
        aria-label="Volume"
        className="h-2"
      />
    </div>
  </div>
)
