import type { TimeRange, MediaState, MediaControls } from '@/types/base'

export interface VideoSegment extends TimeRange {
  id: string
  music?: string
  author?: string
  year?: string
  genre?: string
  color?: string
  isActive?: boolean
}

export interface AudioTrack {
  name: string
  album: string
  year: string
  authors: string[]
  genres: string[]
  isrc: string
  gmusic: string
  occurrences: TimeRange[]
  imageUrl?: string
}

export interface TrackCardProps {
  track: AudioTrack
}

export interface TracksSummaryProps {
  tracks: AudioTrack[]
}

export interface TrackOccurrencesProps {
  occurrences: TimeRange[]
  hasMultiple: boolean
}


export interface MediaPlayerProps {
  videoSrc: string
  segments: VideoSegment[]
  className?: string
}

export interface MediaPlayerState extends MediaState {
  skipEmptySegments: boolean
  currentSegmentIndex: number
  isFullscreen: boolean
  isHovering: boolean
  isSeeking: boolean
  isLoading: boolean
}

export interface MediaPlayerControls extends MediaControls {
  onNext: () => void
  onSkipToggle: (checked: boolean) => void
  onFullscreen: () => void
  onSeekStart: () => void
  onSeekEnd: (time: number) => void
}

export interface SegmentMarker extends TimeRange {
  id: string
  color?: string
  isActive?: boolean
}

export interface ProgressBarProps {
  value: number
  duration: number
  isSeeking: boolean
  isHovering: boolean
  onSeek: (time: number) => void
  onSeekStart: () => void
  onSeekEnd: (time: number) => void
  segments: VideoSegment[]
}

export interface SegmentBarProps {
  segments: SegmentMarker[]
  duration: number
}
