export async function getMxfStatus(id: string) {
    const resp = await fetch(`${process.env.NEXT_PUBLIC_MXF_TO_MP4_URL}/v1/mxf/${id}`);

    if (!resp.ok) {
        throw new Error("Erro ao consultar status");
    }

    return resp.json();
}
export async function getMxfEdlStatus(id: number) {
    const resp = await fetch(`${process.env.NEXT_PUBLIC_MXF_TO_EDL_URL}/v1/mxf/${id}`);

    if (!resp.ok) {
        throw new Error("Erro ao consultar status");
    }

    return resp.json();
}

export async function uploadMxf(formData: FormData) {
    const resp = await fetch(`${process.env.NEXT_PUBLIC_MXF_TO_MP4_URL}/v1/mxf/upload`, {
        method: "POST",
        body: formData
    });

    if (!resp.ok) {
        throw new Error("Falha ao enviar arquivo.");
    }

    return resp.json();
}
export async function uploadEdlMxf(formData: FormData) {
    const resp = await fetch(`${process.env.NEXT_PUBLIC_MXF_TO_EDL_URL}/v1/mxf`, {
        method: "POST",
        body: formData
    });

    if (!resp.ok) {
        throw new Error("Falha ao enviar arquivo.");
    }

    return resp.json();
}

export async function downloadEdl(id: number) {
    const resp = await fetch(`${process.env.NEXT_PUBLIC_MXF_TO_EDL_URL}/v1/edl/${id}/download`);

    if (!resp.ok) {
        throw new Error("Falha ao obter arquivo.");
    }

    const fileText = await resp.text();

    return { edl_text: fileText };
}
