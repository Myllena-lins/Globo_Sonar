import { useCallback, useEffect, useRef, useState } from "react";
import {
    uploadMxf,
    uploadEdlMxf,
    getMxfStatus,
    getMxfEdlStatus
} from "@/services/mxfService";

type GlobalStatus = "idle" | "running" | "done" | "error";

export function useMxfProcess() {
    const [mp4Id, setMp4Id] = useState<string | null>(null);
    const [edlId, setEdlId] = useState<number | null>(null);

    const [status, setStatus] = useState<GlobalStatus>("idle");
    const [progressStep, setProgressStep] = useState<number>(0);
    const [error, setError] = useState<any>(null);

    const mp4LastStatus = useRef<string | null>(null);
    const edlLastStatus = useRef<string | null>(null);

    const increaseStep = () =>
        setProgressStep(prev => prev + 1);

    const startProcess = useCallback(async (formData: FormData) => {
        try {
            setError(null);
            setStatus("running");
            setProgressStep(0);

            const mp4Resp = await uploadMxf(formData);
            const edlResp = await uploadEdlMxf(formData);

            setMp4Id(mp4Resp.processId);
            setEdlId(edlResp.id);

        } catch (err: any) {
            setError(err);
            setStatus("error");
        }
    }, []);

    useEffect(() => {
        if (!mp4Id || status !== "running") return;

        const interval = setInterval(async () => {
            try {
                const resp = await getMxfStatus(mp4Id);

                if (resp.status !== mp4LastStatus.current) {
                    mp4LastStatus.current = resp.status;
                    increaseStep();
                }

                if (resp.status === "completed") {
                    clearInterval(interval);
                }

            } catch (err) {
                setError(err);
                setStatus("error");
                clearInterval(interval);
            }
        }, 1500);

        return () => clearInterval(interval);
    }, [mp4Id, status]);

    useEffect(() => {
        if (!edlId || status !== "running") return;

        const interval = setInterval(async () => {
            try {
                const resp = await getMxfEdlStatus(edlId);

                if (resp.status !== edlLastStatus.current) {
                    edlLastStatus.current = resp.status;
                    increaseStep();
                }

                if (resp.status === "processed") {
                    clearInterval(interval);
                    setStatus("done");
                }

            } catch (err) {
                setError(err);
                setStatus("error");
                clearInterval(interval);
            }
        }, 1500);

        return () => clearInterval(interval);
    }, [edlId, status]);

    return {
        status,
        progressStep,
        error,
        startProcess,
        mp4Id,
        edlId,
    };
}
