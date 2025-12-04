import React from "react"
import { Music } from "lucide-react"

interface MusicPopupProps {
  show: boolean
  music?: string
  author?: string
  genre?: string
}

export const MusicPopup: React.FC<MusicPopupProps> = ({ show, music, author, genre }) => (
  <div className={`absolute top-4 right-4 px-4 py-3 rounded-2xl border border-white/30 backdrop-blur-md bg-gray-900/40 z-20 shadow-lg transition-all duration-300 ease-out ${show && music ? "opacity-100 translate-y-0 pointer-events-auto" : "opacity-0 -translate-y-2 pointer-events-none"}`}>
    <div className="flex items-start gap-3">
      <div className="p-2 rounded-full bg-white/10">
        <Music className="h-4 w-4 text-white" />
      </div>
      <div className="space-y-0.5">
        <p className="text-sm font-semibold text-white">{music}</p>
        <p className="text-xs text-white/70">{author}</p>
        <p className="text-xs text-white/50">{genre}</p>
      </div>
    </div>
  </div>
)

