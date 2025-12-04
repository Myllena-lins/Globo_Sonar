import type { AudioTrack } from '@/types/media'

export interface ResultSectionProps {
  edlFile: File | string
  tracks: AudioTrack[]
}