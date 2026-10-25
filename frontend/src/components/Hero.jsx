import { useState, useEffect, useRef } from 'react'
import BarreRecherche from './BarreRecherche'

const VIDEOS = ['/videos/bigben.mp4', '/videos/waterfall.mp4', '/videos/sunset.mp4']
const DUREE_PAR_VIDEO_MS = 8000

function Hero() {
  const [indexActuel, setIndexActuel] = useState(0)
  const videoRefs = useRef([])

  useEffect(() => {
    const intervalle = setInterval(() => {
      setIndexActuel((precedent) => (precedent + 1) % VIDEOS.length)
    }, DUREE_PAR_VIDEO_MS)
    return () => clearInterval(intervalle)
  }, [])

  useEffect(() => {
    // Relance la lecture de la vidéo qui devient active
    const videoActive = videoRefs.current[indexActuel]
    if (videoActive) {
      videoActive.currentTime = 0
      videoActive.play().catch(() => {})
    }
  }, [indexActuel])

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {VIDEOS.map((src, index) => (
        <video
          key={src}
          ref={(el) => (videoRefs.current[index] = el)}
          autoPlay={index === 0}
          muted
          playsInline
          loop
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${
            index === indexActuel ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <source src={src} type="video/mp4" />
        </video>
      ))}

      <div className="absolute inset-0 bg-black/40" />

      <div className="relative z-10 h-full flex flex-col items-center justify-center text-center px-6">
        <h1 className="font-serif text-5xl md:text-7xl text-white mb-6 max-w-3xl leading-tight">
          Curated journeys to the world's most inspiring places
        </h1>
        <div className="mt-4">
          <BarreRecherche />
        </div>
      </div>
    </div>
  )
}

export default Hero