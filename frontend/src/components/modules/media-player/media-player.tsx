"use client"

import {useState, useRef, useEffect, useCallback} from "react"
import {cn} from "@/lib/utils"
import {ProgressBar} from "@/components/modules/media-player/progress-bar"
import {VideoControls} from "@/components/modules/media-player/video-controls"
import {MusicPopup} from "@/components/modules/media-player/music-popup"
import {LoadingOverlay} from "@/components/modules/media-player/loading-overlay"
import Hls from "hls.js";
import type {MediaPlayerProps} from "@/types"

export function MediaPlayer({videoSrc, segments, className}: MediaPlayerProps) {
    const videoRef = useRef<HTMLVideoElement>(null)
    const [isPlaying, setIsPlaying] = useState(false)
    const [currentTime, setCurrentTime] = useState(0)
    const [duration, setDuration] = useState(0)
    const [volume, setVolume] = useState(1)
    const [isMuted, setIsMuted] = useState(false)
    const [playbackRate, setPlaybackRate] = useState(1)
    const [skipEmptySegments, setSkipEmptySegments] = useState(false)
    const [currentSegmentIndex, setCurrentSegmentIndex] = useState<number>(-1)
    const [isFullscreen, setIsFullscreen] = useState(false)
    const [isHovering, setIsHovering] = useState(false)
    const [showPopup, setShowPopup] = useState(false)
    const [isSeeking, setIsSeeking] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const popupTimeoutRef = useRef<number | null>(null)
    const segmentTransitionRef = useRef(false)

    const handleNextSegment = useCallback(() => {
        const video = videoRef.current
        if (!video || segments.length === 0) return
        let nextIndex = currentSegmentIndex + 1
        while (nextIndex < segments.length && !segments[nextIndex].music) {
            nextIndex++
        }
        if (nextIndex < segments.length) {
            const nextSeg = segments[nextIndex]
            video.currentTime = nextSeg.startTime
            setCurrentSegmentIndex(nextIndex)
        } else {
            video.pause()
            setIsPlaying(false)
        }
    }, [currentSegmentIndex, segments])

    useEffect(() => {
        if (!videoSrc) return;

        const video = videoRef.current;
        if (!video) return;

        // sempre MP4
        video.src = videoSrc;

        const handleLoadedMetadata = () => {
            if (isFinite(video.duration)) {
                setDuration(video.duration);
            }
        };

        video.addEventListener("loadedmetadata", handleLoadedMetadata);

        return () => {
            video.removeEventListener("loadedmetadata", handleLoadedMetadata);
        };
    }, [videoSrc]);

    // Listeners fixos do vídeo
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const handleTimeUpdate = () => {
            const t = video.currentTime;
            setCurrentTime(t);

            // Atualiza segmento atual
            const newIndex = segments.findIndex(
                seg => t >= seg.startTime && t < seg.endTime
            );

            setCurrentSegmentIndex(newIndex);

            // Skip automático
            if (skipEmptySegments) {
                const seg = segments[newIndex];

                if ((!seg || !seg.music) && !segmentTransitionRef.current) {
                    segmentTransitionRef.current = true;

                    const next = segments.find(s => s.startTime > t && s.music);
                    if (next) {
                        video.currentTime = next.startTime;
                    } else {
                        video.pause();
                        setIsPlaying(false);
                    }

                    setTimeout(() => {
                        segmentTransitionRef.current = false;
                    }, 150);
                }
            }
        };

        const handleEnded = () => setIsPlaying(false);

        video.addEventListener("timeupdate", handleTimeUpdate);
        video.addEventListener("ended", handleEnded);

        return () => {
            video.removeEventListener("timeupdate", handleTimeUpdate);
            video.removeEventListener("ended", handleEnded);
        };
    }, [segments, skipEmptySegments]);

    useEffect(() => {
        if (popupTimeoutRef.current) {
            window.clearTimeout(popupTimeoutRef.current)
            popupTimeoutRef.current = null
        }
        const seg = segments[currentSegmentIndex]
        if (currentSegmentIndex !== -1 && seg?.music) {
            setShowPopup(true)
            popupTimeoutRef.current = window.setTimeout(() => {
                setShowPopup(false)
                popupTimeoutRef.current = null
            }, 3000)
        } else {
            setShowPopup(false)
        }
        return () => {
            if (popupTimeoutRef.current) {
                window.clearTimeout(popupTimeoutRef.current)
                popupTimeoutRef.current = null
            }
        }
    }, [currentSegmentIndex, segments])

    // Loading realmente baseado no readyState e buffer
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const interval = setInterval(() => {
            if (!isPlaying) {
                setIsLoading(false);
                return;
            }

            // readyState 4: have enough data to play
            if (video.readyState < 3) {
                setIsLoading(true);
            } else {
                setIsLoading(false);
            }
        }, 300);

        return () => clearInterval(interval);
    }, [isPlaying]);


    const togglePlay = () => {
        const video = videoRef.current
        if (!video) return
        if (isPlaying) {
            video.pause()
        } else {
            video.play().catch(() => {
            })
        }
        setIsPlaying(!isPlaying)
    }
    const handleVolumeChange = (value: number) => {
        const video = videoRef.current
        if (!video) return
        video.volume = value
        setVolume(value)
        setIsMuted(value === 0)
    }
    const toggleMute = () => {
        const video = videoRef.current
        if (!video) return
        if (isMuted) {
            video.volume = volume || 0.5
            setIsMuted(false)
        } else {
            video.volume = 0
            setIsMuted(true)
        }
    }
    const cyclePlaybackRate = () => {
        const rates = [0.5, 0.75, 1, 1.25, 1.5, 2]
        const currentIndex = rates.indexOf(playbackRate)
        const nextIndex = (currentIndex + 1) % rates.length
        const newRate = rates[nextIndex]
        if (videoRef.current) {
            videoRef.current.playbackRate = newRate
        }
        setPlaybackRate(newRate)
    }
    const toggleFullscreen = () => {
        const container = videoRef.current?.parentElement
        if (!container) return
        if (!isFullscreen) {
            if (container.requestFullscreen) {
                container.requestFullscreen()
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen()
            }
        }
        setIsFullscreen(!isFullscreen)
    }
    const formatTime = (time: number) => {
        if (!isFinite(time)) return "00:00"
        const minutes = Math.floor(time / 60)
        const seconds = Math.floor(time % 60)
        return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
    }
    const getSegmentProgress = () => {
        if (duration === 0) return []
        return segments.map((segment) => {
            const isActive = currentTime >= segment.startTime && currentTime < segment.endTime
            return {...segment, isActive}
        })
    }
    const segmentProgress = getSegmentProgress()
    const currentSegment = segments[currentSegmentIndex]
    const handleSeekStart = () => setIsSeeking(true)
    const handleSeekEnd = (value: number) => {
        setIsSeeking(false)
        const video = videoRef.current
        if (!video) return
        if (isFinite(value)) {
            video.currentTime = value
            setCurrentTime(value)
        }
    }
    const handleSeekChange = (value: number) => {
        setCurrentTime(value)
    }
    return (
        <div
            className={cn("relative overflow-hidden rounded-3xl border border-white/20 backdrop-blur-[11px] w-full", className)}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={() => setIsHovering(false)}>
            <div className="relative bg-black/85 flex items-center justify-center">
                <video ref={videoRef} src={videoSrc} crossOrigin="anonymous"/>
                {isLoading && <LoadingOverlay/>}
                <MusicPopup show={showPopup} music={currentSegment?.music} author={currentSegment?.author}
                            genre={currentSegment?.genre}/>
                <div className="absolute left-4 right-4 bottom-24 flex items-center">
                    <ProgressBar
                        value={isSeeking ? currentTime : currentTime}
                        duration={duration}
                        isSeeking={isSeeking}
                        isHovering={isHovering}
                        onSeek={handleSeekChange}
                        onSeekStart={handleSeekStart}
                        onSeekEnd={handleSeekEnd}
                        segments={segmentProgress}
                    />
                </div>
                <div className={cn(
                    "absolute left-4 right-4 bottom-4 p-3 rounded-xl flex items-center",
                    "transition-opacity duration-300",
                    isHovering ? "opacity-100" : "opacity-0",
                    "bg-background/10 backdrop-blur-md",
                )}>
                    <VideoControls
                        isPlaying={isPlaying}
                        isMuted={isMuted}
                        volume={volume}
                        playbackRate={playbackRate}
                        skipEmptySegments={skipEmptySegments}
                        onPlayPause={togglePlay}
                        onMute={toggleMute}
                        onVolumeChange={handleVolumeChange}
                        onNext={handleNextSegment}
                        onSkipToggle={setSkipEmptySegments}
                        onRateChange={cyclePlaybackRate}
                        onFullscreen={toggleFullscreen}
                        currentTime={currentTime}
                        duration={duration}
                        formatTime={formatTime}
                    />
                </div>
            </div>
        </div>
    )
}
