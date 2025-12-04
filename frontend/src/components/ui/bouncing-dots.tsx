import { motion } from "framer-motion";

const BouncingDots = () => {
    const dotVariants = {
        start: { y: "0%" },
        end: { y: "-100%" },
    };

    const dotTransition = {
        duration: 0.5,
        repeat: Infinity,
        repeatType: "reverse" as const,
        ease: "easeInOut" as const,
    };

    return (
        <span
            className="inline-flex items-end ml-1"
            style={{ position: "relative" }}
        >
      {[0, 0.15, 0.3].map((delay, i) => (
          <motion.span
              key={i}
              variants={dotVariants}
              initial="start"
              animate="end"
              transition={{ ...dotTransition, delay }}
              className="w-[5px] h-[5px] rounded-full bg-foreground mx-[2px]"
          />
      ))}
    </span>
    );
};

export default BouncingDots;
