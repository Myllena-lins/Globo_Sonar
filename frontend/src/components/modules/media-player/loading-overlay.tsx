import React from "react"

export const LoadingOverlay: React.FC = () => (
  <div className="absolute inset-0 flex items-center justify-center z-50 pointer-events-none">
    <div className="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin" />
  </div>
)

