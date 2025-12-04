import type {BaseComponent, Tone} from '@/types/base'

export interface HeroSectionProps extends BaseComponent {
    processing: boolean
    currentStep: number | null
    steps: string[]
    error: any
    onClearError: () => void
    onUpload: (formData: FormData) => Promise<void>;
}

export interface FileDropzoneProps extends BaseComponent {
    onUpload: (formData: FormData) => Promise<void>;
    tone?: Tone
}

export interface TextBoxProps extends BaseComponent {
    text: string
    fileName?: string
    title?: string
}

export interface ProcessingTimelineProps extends BaseComponent {
    steps: string[]
    currentStep: number
}

export interface VideoControlsProps {
    isPlaying: boolean
    isMuted: boolean
    volume: number
    playbackRate: number
    skipEmptySegments: boolean
    onPlayPause: () => void
    onMute: () => void
    onVolumeChange: (value: number) => void
    onNext: () => void
    onSkipToggle: (checked: boolean) => void
    onRateChange: () => void
    onFullscreen: () => void
    currentTime: number
    duration: number
    formatTime: (t: number) => string
}

export interface PlayPauseButtonProps extends BaseComponent {
    isPlaying: boolean
    onToggle: () => void
}

export interface VolumeControlProps extends BaseComponent {
    isMuted: boolean
    volume: number
    onMute: () => void
    onVolumeChange: (value: number) => void
}

export interface SkipSectionProps extends BaseComponent {
    onNext: () => void
    skipEmptySegments: boolean
    onSkipToggle: (checked: boolean) => void
}

export interface RateButtonProps extends BaseComponent {
    rate: number
    onClick: () => void
}

export interface FullscreenButtonProps extends BaseComponent {
    onClick: () => void
}
