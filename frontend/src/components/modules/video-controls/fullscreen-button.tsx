import React from "react"
import { Button } from "../../ui/button"
import { Maximize } from "lucide-react"
import { cn } from "@/lib/utils"
import baseGlass from "@/styles/baseGlass"
import type { FullscreenButtonProps } from "@/types"

export const FullscreenButton: React.FC<FullscreenButtonProps> = ({ onClick }) => (
  <Button
    variant="glass"
    size="icon"
    onClick={onClick}
    className={cn(baseGlass, "rounded-full hover:bg-white/20 text-xs text-white px-3 py-1.5")}
  >
    <Maximize className="h-4 w-4" />
  </Button>
)

