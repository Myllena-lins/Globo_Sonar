import { cn } from "@/lib/utils"; // Adjust the path based on your project structure

const baseGlass = cn(
    "relative overflow-hidden rounded-[24px] border border-white/30 backdrop-blur-[11px]",
    "shadow-[0_8px_32px_rgba(0,0,0,0.1),inset_0_1px_0_rgba(255,255,255,0.4),inset_0_-1px_0_rgba(255,255,255,0.1),inset_0_0_54px_27px_rgba(255,255,255,0.03)]",
    "bg-transparent"
);

export default baseGlass;