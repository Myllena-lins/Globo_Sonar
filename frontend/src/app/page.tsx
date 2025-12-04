"use client"

import {useEffect} from "react";
import {useRouter} from "next/navigation";
import {useMxfProcess} from "@/hooks/useMxfProcess";
import HeroSection from "@/components/layouts/hero-section";
import {TimelineSection} from "@/components/layouts/timeline-section";

export default function HomePage() {
    const router = useRouter();
    const {
        startProcess,
        status,
        progressStep,
        error,
        mp4Id,
        edlId
    } = useMxfProcess();

    useEffect(() => {
        if (status === "done" && mp4Id && edlId) {
            router.push(`/resultados/${mp4Id}/${edlId}`);
        }
    }, [status, mp4Id, edlId, router]);

    return (
        <div className="flex flex-col gap-24">
            <HeroSection
                processing={status === "running"}
                currentStep={progressStep}
                error={error}
                onClearError={() => window.location.reload()}
                onUpload={startProcess}
                steps={[
                    "Enviando arquivo MXF",
                    "Gerando EDL",
                    "Gerando Preview",
                ]}
            />
            <TimelineSection/>
        </div>
    )
}
