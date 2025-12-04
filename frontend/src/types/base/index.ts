import { PLAYBACK_RATES } from '@/types'

export interface BaseComponent {
  className?: string
  children?: React.ReactNode
}

export interface TimeRange {
  startTime: number
  endTime: number
}

export type Tone = 'neutral' | 'gold' | 'magenta'

export type PlaybackRate = typeof PLAYBACK_RATES[number]

export interface MediaState {
  isPlaying: boolean
  isMuted: boolean
  volume: number
  playbackRate: PlaybackRate
  currentTime: number
  duration: number
}

export interface MediaControls {
  onPlayPause: () => void
  onMute: () => void
  onVolumeChange: (value: number) => void
  onSeek: (time: number) => void
  onRateChange: () => void
}
