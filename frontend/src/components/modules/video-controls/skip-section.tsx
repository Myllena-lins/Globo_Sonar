import React from "react"
import { Button } from "../../ui/button"
import { SkipForward } from "lucide-react"
import { Switch } from "../../ui/switch"
import { cn } from "@/lib/utils"
import baseGlass from "@/styles/baseGlass"
import type { SkipSectionProps } from "@/types"

export const SkipSection: React.FC<SkipSectionProps> = ({ onNext, skipEmptySegments, onSkipToggle, className }) => (
  <div className={className ?? cn(baseGlass, "flex items-center px-3 py-1.5")}>
    <Button variant="ghost" size="icon" onClick={onNext} className="h-8 w-8 rounded-full hover:bg-white/20 text-white p-0">
      <SkipForward className="h-4 w-4" />
    </Button>
    <div className="flex items-center gap-4 ml-3">
      <span className="text-xs text-white/90 whitespace-nowrap">Pular trechos sem música</span>
      <Switch checked={skipEmptySegments} onCheckedChange={onSkipToggle} />
    </div>
  </div>
)
