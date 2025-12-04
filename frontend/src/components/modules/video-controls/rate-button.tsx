import React from "react"
import { Button } from "../../ui/button"
import { cn } from "@/lib/utils"
import baseGlass from "@/styles/baseGlass"
import type { RateButtonProps } from "@/types"

export const RateButton: React.FC<RateButtonProps> = ({ rate, onClick, className }) => (
  <Button
    variant="glass"
    size="icon"
    onClick={onClick}
    className={className ?? cn(baseGlass, "rounded-full hover:bg-white/20 text-xs text-white px-3 py-1.5")}
  >
    {rate}x
  </Button>
)
