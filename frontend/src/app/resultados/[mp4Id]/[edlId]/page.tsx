import ResultClient from "@/app/resultados/[mp4Id]/[edlId]/result-client";

export default function ResultPage({ params }: { params: { mp4Id: string; edlId: string } }) {
    return <ResultClient mp4Id={params.mp4Id} edlId={params.edlId} />;
}
