"use client"

import React, {useState, useCallback} from 'react';
import { Copy, Download, Check } from 'lucide-react';
import type { TextBoxProps } from "@/types";
import baseGlass from "@/styles/baseGlass";
import { cn } from "@/lib/utils";

const EdlExportBox: React.FC<TextBoxProps> = ({
    text,
    fileName = 'relatorio.txt',
    title = 'EDL'
}) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = useCallback(async () => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Falha ao copiar:', err);
        }
    }, [text]);

    const handleDownload = useCallback(() => {
        const blob = new Blob([text], {type: 'text/plain;charset=utf-8'});
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, [text, fileName]);

    return (
        <div className={cn(baseGlass, "rounded-xl overflow-hidden")}>
            <div className="flex justify-between items-center p-4 border-b border-white/10">
                <h3 className="text-lg font-semibold">{title}</h3>
                <div className="flex gap-2">
                    <button
                        onClick={handleCopy}
                        className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                        title="Copiar"
                    >
                        {copied ? (
                            <Check className="w-5 h-5 text-green-500" />
                        ) : (
                            <Copy className="w-5 h-5" />
                        )}
                    </button>
                    <button
                        onClick={handleDownload}
                        className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                        title="Baixar"
                    >
                        <Download className="w-5 h-5" />
                    </button>
                </div>
            </div>
            <pre className="p-4 overflow-auto text-sm font-mono">
                {text}
            </pre>
        </div>
    );
};

export default EdlExportBox;