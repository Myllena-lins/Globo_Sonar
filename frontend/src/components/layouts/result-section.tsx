import * as React from "react";
import EdlExportBox from "@/components/modules/edl-box/edl-export-box";
import { TracksSummary } from "@/components/modules/track-summary/tracks-summary";
import type { ResultSectionProps } from "@/types";

export function ResultSection({ edlFile, tracks }: ResultSectionProps) {
    const edlText = typeof edlFile === "string" ? edlFile : edlFile.name;

    return (
        <section className="bg-background py-20 relative overflow-hidden">
            <div className="container mx-auto px-6">

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    <div className="flex flex-col lg:col-span-2">
                        <div className="mb-5">
                            <p className="text-muted-foreground text-sm uppercase tracking-wider">
                                RESULTADOS
                            </p>
                            <h2 className="text-3xl font-bold">
                                {typeof edlFile === "string" ? "Relatório de Análise" : edlFile.name}
                            </h2>
                        </div>
                        <EdlExportBox
                            text={edlText}
                            fileName="projeto.edl"
                            title="EDL"
                        />
                    </div>

                    <div>
                        <TracksSummary tracks={tracks} />
                    </div>
                </div>
            </div>
        </section>
    );
}
