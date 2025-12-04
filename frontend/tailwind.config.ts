import type { Config } from "tailwindcss";

export default {
    theme: {
        extend: {
            fontFamily: {
                sans: ["var(--font-sans)", "system-ui", "sans-serif"],
                mono: ["var(--font-mono)", "monospace"],
            },
        },
    },
} satisfies Config;
