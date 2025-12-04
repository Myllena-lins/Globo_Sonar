import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:border-ring relative overflow-hidden",
    {
        variants: {
            variant: {
                default:
                    "bg-primary text-primary-foreground hover:bg-primary/90",
                destructive:
                    "bg-destructive text-white hover:bg-destructive/90",
                outline:
                    "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50",
                secondary:
                    "bg-secondary text-secondary-foreground hover:bg-secondary/80",
                ghost:
                    "hover:bg-accent",
                link: "text-primary underline-offset-4 hover:underline",

                glass:
                    "bg-white/20 border border-white/30 backdrop-blur-[11px] shadow-[0_8px_32px_rgba(0,0,0,0.1),inset_0_1px_0_rgba(255,255,255,0.4),inset_0_-1px_0_rgba(255,255,255,0.1),inset_0_0_54px_27px_rgba(255,255,255,0.10)] hover:bg-white/30 transition-all duration-300",
            },
            tone: {
                neutral: "",
                muted: "bg-transparent",
                primary: "bg-gradient-to-r from-primary/60 to-bg-background/40 hover:from-primary/60 hover:to-bg-background/60",
                secondary: "bg-gradient-to-r from-secondary/60 to-bg-background/40 hover:from-secondary/60 hover:to-bg-background/60",
            },
            size: {
                default: "h-10 px-6 rounded-[24px]",
                sm: "h-8 px-4 rounded-[20px]",
                lg: "h-12 px-8 rounded-[28px]",
                icon: "size-10 rounded-full",
            },
        },
        compoundVariants: [
            {
                variant: "glass",
                tone: "primary",
                class: "text-white hover:shadow-primary/60",
            },
            {
                variant: "glass",
                tone: "secondary",
                class: "text-white hover:shadow-secondary/60",
            },
        ],
        defaultVariants: {
            variant: "default",
            size: "default",
            tone: "neutral",
        },
    }
);

function Button({
                    className,
                    variant,
                    size,
                    tone,
                    asChild = false,
                    ...props
                }: React.ComponentProps<"button"> &
    VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
}) {
    const Comp = asChild ? Slot : "button";
    return (
        <Comp
            data-slot="button"
            className={cn(buttonVariants({ variant, size, tone, className }))}
            {...props}
        />
    );
}

export { Button, buttonVariants };
