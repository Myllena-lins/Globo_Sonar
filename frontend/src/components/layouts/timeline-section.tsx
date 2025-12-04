"use client";

import {useRef, useEffect, useState} from "react";
import {useInView, motion, useScroll, useTransform} from "framer-motion";
import {FileText, Mic, Music, Waves} from "lucide-react";

function TimelineItem({
                          icon: Icon,
                          title,
                          description,
                          highlight,
                          align = "left",
                          index
                      }: {
    icon: React.ComponentType<{ className?: string }>;
    title: string;
    description: string;
    highlight: string;
    align?: "left" | "right";
    index: number;
}) {
    const ref = useRef(null);
    const isInView = useInView(ref, {
        once: false,
        margin: "-150px 0px"
    });
    const [hasAnimated, setHasAnimated] = useState(false);

    useEffect(() => {
        if (isInView && !hasAnimated) {
            const timer = setTimeout(() => {
                setHasAnimated(true);
            }, index * 200);
            return () => clearTimeout(timer);
        }
    }, [isInView, hasAnimated, index]);

    const isRight = align === "right";

    return (
        <motion.div
            ref={ref}
            className={`
        relative flex items-start gap-6
        flex-col sm:flex-row
        ${isRight ? "md:flex-row-reverse md:text-right" : "md:text-left"}
      `}
            initial={{opacity: 0, y: 50}}
            animate={hasAnimated ? {opacity: 1, y: 0} : {opacity: 0, y: 50}}
            transition={{duration: 0.8, delay: index * 0.2}}
        >
            <div className="relative z-10 flex-shrink-0">
                <motion.div
                    className={`
            w-10 h-10 rounded-full border-2 flex items-center justify-center
            ${hasAnimated ? "bg-accent/20 border-primary" : "bg-accent/20 border-muted"}
          `}
                    whileHover={{scale: 1.1}}
                    transition={{type: "spring", stiffness: 400, damping: 10}}
                >
                    <Icon
                        className={`
              w-5 h-5 transition-colors duration-500
              ${hasAnimated ? "text-primary" : "text-muted"}
            `}
                    />
                </motion.div>
            </div>

            <div
                className={`
          flex-1 w-full md:max-w-2xl pt-1
          ${isRight ? "md:text-right" : "text-left"}
        `}
            >
                <motion.h3
                    className="text-xl font-bold mb-3"
                    initial={{opacity: 0, x: isRight ? 30 : -30}}
                    animate={hasAnimated ? {opacity: 1, x: 0} : {opacity: 0, x: isRight ? 30 : -30}}
                    transition={{duration: 0.6, delay: index * 0.2 + 0.3}}
                >
                    {title}
                </motion.h3>

                <motion.p
                    className="text-muted-foreground text-sm leading-relaxed mb-4"
                    initial={{opacity: 0, x: isRight ? 30 : -30}}
                    animate={hasAnimated ? {opacity: 1, x: 0} : {opacity: 0, x: isRight ? 30 : -30}}
                    transition={{duration: 0.6, delay: index * 0.2 + 0.4}}
                >
                    {description}
                </motion.p>

                <motion.div
                    className="bg-muted/10 border border-border rounded-lg p-4"
                    initial={{opacity: 0, x: isRight ? 30 : -30}}
                    animate={hasAnimated ? {opacity: 1, x: 0} : {opacity: 0, x: isRight ? 30 : -30}}
                    transition={{duration: 0.6, delay: index * 0.2 + 0.5}}
                >
                    <p className="text-muted-foreground text-sm">
            <span className="text-primary font-semibold">
              {align === "left" ? "Como é feito:" : "Benefício:"}
            </span>{" "}
                        {highlight}
                    </p>
                </motion.div>
            </div>
        </motion.div>
    );
}


function ProgressLine() {
    const sectionRef = useRef<HTMLDivElement>(null);
    const {scrollYProgress} = useScroll({
        target: sectionRef,
        offset: ["start end", "end start"]
    });

    const height = useTransform(scrollYProgress, [0, 0.6], ["0%", "100%"]);

    return (
        <div ref={sectionRef} className="absolute left-[19px] top-0 bottom-0 w-[2px] overflow-hidden">
            <motion.div
                className="w-full bg-gradient-to-b from-accent/60 to-accent/10"
                style={{height}}
                transition={{duration: 0.5}}
            />
        </div>
    );
}

export function TimelineSection() {
    const timelineItems = [
        {
            icon: Waves,
            title: "Extração de áudio por camadas",
            description: "Nosso sistema analisa o MXF enviado e organiza o áudio em diferentes camadas (faixas de locução, música, efeitos, etc.). Isso permite que cada elemento do som seja tratado individualmente, facilitando tanto a identificação para a geração dos relatórios técnicos.",
            highlight: "usamos algoritmos de análise espectral e de mixagem para separar automaticamente os canais, preservando a qualidade original e mantendo os timecodes sincronizados.",
            align: "left" as const
        },
        {
            icon: Mic,
            title: "Separação de áudio e voz",
            description: "Distinguir voz de outros sons é essencial para revisar diálogos, legendagem ou dublagem. Nosso sistema aplica modelos de processamento de áudio que identificam e isolam falas humanas, separando-as de ruídos, músicas ou ambientes.",
            highlight: "a inteligência artificial ganha clareza no contexto falado, economiza tempo em tarefas repetitivas e garante maior precisão no retorno técnico.",
            align: "right" as const
        },
        {
            icon: Music,
            title: "Identificação de jingles, músicas e efeitos sonoros",
            description: "Além de separar as camadas, o sistema reconhece automaticamente trechos de música, jingles de marcas e efeitos sonoros. Isso garante maior controle de direitos autorais, facilita a catalogação e acelera a localização de trechos específicos em projetos extensos.",
            highlight: "utilizamos bancos de referência e técnicas de fingerprinting de áudio para identificar padrões sonoros mesmo quando estão sobrepostos a outros elementos.",
            align: "left" as const
        },
        {
            icon: FileText,
            title: "Geração de EDL",
            description: "Além de separar as camadas, o sistema reconhece automaticamente trechos de música, jingles de marcas e efeitos sonoros. Isso garante maior controle de direitos autorais, facilita a catalogação e acelera a localização de trechos específicos em projetos extensos.",
            highlight: "utilizamos bancos de referência e técnicas de fingerprinting de áudio para identificar padrões sonoros mesmo quando estão sobrepostos a outros elementos.",
            align: "right" as const
        }
    ];

    return (
        <section className="bg-background py-20 relative overflow-hidden">
            <div className="absolute bottom-0 right-0 w-[500px] h-[500px]">
                <div
                    className="absolute inset-0 bg-gradient-to-tl from-accent/20 via-accent/10 to-transparent blur-[120px] rounded-full dark:from-accent/20 dark:via-accent/10"/>
            </div>

            <div className="container mx-auto px-6 relative z-10">
                <div className="mb-16">
                    <p className="text-muted-foreground text-sm uppercase tracking-wider mb-2">
                        ENTENDA MAIS
                    </p>
                    <h2 className="text-3xl md:text-4xl">
                        <strong>Automatizando</strong> processos com <strong>algoritmos e fingerprint</strong>
                    </h2>
                </div>

                <div className="relative">
                    <ProgressLine/>

                    <div className="absolute left-[19px] top-0 bottom-0 w-[2px] bg-muted/30"/>

                    <div className="space-y-24">
                        {timelineItems.map((item, index) => (
                            <TimelineItem
                                key={index}
                                icon={item.icon}
                                title={item.title}
                                description={item.description}
                                highlight={item.highlight}
                                align={item.align}
                                index={index}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}