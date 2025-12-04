"use client"

import * as React from "react"
import { useDropzone } from "react-dropzone"
import { cn } from "@/lib/utils"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { UploadCloud, FileX, CheckCircle2 } from "lucide-react"
import baseGlass from "@/styles/baseGlass"
import type { FileDropzoneProps } from "@/types"

export function FileDropzone({
                                 onUpload,
                                 className,
                             }: FileDropzoneProps) {
    const [file, setFile] = React.useState<File | null>(null)
    const [error, setError] = React.useState<string | null>(null)
    const [uploading, setUploading] = React.useState(false)

    const onDrop = React.useCallback(
        (acceptedFiles: File[]) => {
            const selected = acceptedFiles[0]
            if (selected && selected.name.endsWith(".mxf")) {
                setFile(selected)
                setError(null)
            } else {
                setError("Apenas arquivos .mxf são permitidos.")
            }
        },
        []
    )

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        accept: { "application/octet-stream": [".mxf"] },
        multiple: false,
        onDrop,
    })

    async function handleUpload() {
        if (!file) return
        const formData = new FormData()
        formData.append("file", file)

        try {
            setUploading(true)
            await onUpload(formData)
            setFile(null)
        } catch (e) {
            console.error(e)
            setError("Falha no upload.")
        } finally {
            setUploading(false)
        }
    }

    const glassStyle = cn(baseGlass,
        "transition-all duration-300 ease-out cursor-pointer",
        isDragActive && "bg-white/30 border-white/40 shadow-[0_0_20px_rgba(255,255,255,0.2)]",
        "hover:bg-white/10",
        error && "border-destructive/50 bg-destructive/10",
        className
    )

    return (
        <Card {...getRootProps()} className={cn("border-none shadow-none bg-transparent", className)}>
            <CardContent
                className={cn(
                    glassStyle,
                    "flex flex-col items-center justify-center py-32 px-8 text-center space-y-3"
                )}
            >
                <input {...getInputProps()} />

                {file ? (
                    <>
                        <CheckCircle2 className="size-10 drop-shadow-[0_0_10px_rgba(34,197,94,0.4)]" />
                        <p className="text-sm">
                            Arquivo selecionado: <strong>{file.name}</strong>
                        </p>

                        <div className="flex gap-3 mt-3">
                            <Button
                                variant="glass"
                                tone="primary"
                                disabled={uploading}
                                onClick={(e) => {
                                    e.stopPropagation()
                                    handleUpload()
                                }}
                            >
                                {uploading ? "Enviando..." : "Enviar"}
                            </Button>

                            <Button
                                variant="glass"
                                tone="secondary"
                                onClick={(e) => {
                                    e.stopPropagation()
                                    setFile(null)
                                }}
                            >
                                Remover
                            </Button>
                        </div>
                    </>
                ) : isDragActive ? (
                    <>
                        <UploadCloud className="size-10 drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]" />
                        <p className="text-sm font-medium">
                            Solte o arquivo <strong>.mxf</strong> aqui
                        </p>
                    </>
                ) : (
                    <>
                        <UploadCloud className="size-10" />
                        <p className="text-sm">
                            Arraste um arquivo <strong>.mxf</strong> ou clique para selecionar
                        </p>
                    </>
                )}

                {error && (
                    <div className="flex items-center gap-2 text-destructive text-sm mt-2">
                        <FileX className="size-4" />
                        {error}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
