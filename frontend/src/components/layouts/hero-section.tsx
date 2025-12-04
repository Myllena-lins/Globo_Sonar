"use client"

import {FileDropzone} from "@/components/modules/hero-container/file-dropzone"
import {ProcessingTimeline} from "@/components/modules/hero-container/processing-timeline"
import BouncingDots from "@/components/ui/bouncing-dots"
import {Button} from "@/components/ui/button"
import {cn} from "@/lib/utils"
import baseGlass from "@/styles/baseGlass"
import {HeroSectionProps} from "@/types";

export default function HeroSection({
                                        processing,
                                        currentStep,
                                        steps,
                                        error,
                                        onClearError,
                                        onUpload
                                    }: HeroSectionProps) {

    const isProcessingView = processing && currentStep !== null;

    if (isProcessingView) {
        return (
            <div className="container mx-auto px-6">
                <div className="flex items-center gap-4 mb-6">
                    <h1 className="text-4xl">
                        <strong>Aguarde</strong>, estamos trabalhando nisso
                        <BouncingDots/>
                    </h1>
                </div>

                <ProcessingTimeline currentStep={Math.max(0, currentStep ?? 0)} steps={steps}/>
            </div>
        )
    }

    return (
        <div className="flex flex-col gap-24">
            <div className="container mx-auto px-6">

                <h1 className="mb-6 text-4xl">
                    <strong>Gerador de EDL</strong> e <strong>Identificador</strong> de trilhas sonoras
                </h1>

                {error && (
                    <div className={cn(
                        baseGlass,
                        "mt-4 p-4 border-destructive/50 bg-destructive/10 flex flex-col justify-center"
                    )}>
                        <p><strong>Erro:</strong> {error.message}</p>
                        <Button
                            onClick={onClearError}
                            variant="glass"
                            size="sm"
                            className="flex items-center gap-2 text-sm mt-2 max-w-24"
                        >
                            Fechar
                        </Button>
                    </div>
                )}

                <FileDropzone onUpload={onUpload}/>

                <div className="mt-6">
                    <p className="text-sm text-end">
                        Identifique trilhas sonoras em seus vídeos e gere EDLs de forma rápida e fácil. Faça upload dos seus arquivos e deixe o resto conosco!
                    </p>
                </div>

            </div>
        </div>
    )
}