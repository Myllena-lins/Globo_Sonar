"use client";

import {useEffect, useState} from "react";
import {ResultSection} from "@/components/layouts/result-section";
import {MediaPlayer} from "@/components/modules/media-player/media-player";
import {
    getMxfStatus,
    getMxfEdlStatus,
    downloadEdl
} from "@/services/mxfService";
import {VideoSegment} from "@/types";


const generateRandomColorHexCode = () =>
    `#${Math.floor(Math.random() * 16777215).toString(16)}`;

const timeStringToSeconds = (time: string): number => {
    const [h, m, s] = time.split(":");
    return (
        parseInt(h) * 3600 +
        parseInt(m) * 60 +
        parseFloat(s.replace(",", "."))
    );
};

const mapTracksToSegments = (tracks: any[]): VideoSegment[] => {
    const segments: VideoSegment[] = [];

    tracks.forEach((track) => {
        track.occurrences.forEach((occ: any, index: number) => {
            segments.push({
                id: `${track.id}-${index}`,
                music: track.name,
                author: track.authors?.[0] || "Desconhecido",
                genre: track.genres?.[0] || "Indefinido",
                year: track.year || undefined,
                startTime: timeStringToSeconds(occ.start_time),
                endTime: timeStringToSeconds(occ.end_time),
                color: generateRandomColorHexCode(),
            });
        });
    });

    return segments;
};


export default function ResultClient({mp4Id, edlId}: { mp4Id: string; edlId: string }) {

    const [videoUrl, setVideoUrl] = useState<string | null>(null);
    const [tracks, setTracks] = useState([]);
    const [edlText, setEdlText] = useState("Edl não disponível.");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            const mp4Resp = await getMxfStatus(mp4Id);
            setVideoUrl(mp4Resp.readUrl);

            const edlResp = await getMxfEdlStatus(Number(edlId));
            setTracks(edlResp.audio_tracks || []);
            
            const edlTExt = await downloadEdl(Number(edlResp.edl_id));
            setEdlText(edlTExt.edl_text || "Edl não disponível.");

            setLoading(false);
        }

        load();
    }, [mp4Id, edlId]);

    if (loading) {
        return (
            <div className="container mx-auto p-12">
                <h1 className="text-3xl">Carregando resultados…</h1>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-18">
            <div className="container mx-auto px-6">
                <MediaPlayer videoSrc={videoUrl!} segments={mapTracksToSegments(tracks)}/>
            </div>

            <ResultSection
                edlFile={edlText}
                tracks={tracks}
            />
        </div>
    );
}
