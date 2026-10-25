import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { handleImageError } from '../utils/imageHelper'

function SectionTeaser({ images, eyebrow, titre, description, lien, texteLien = 'Voir plus', inverse = false }) {
  const [visible, setVisible] = useState(false)
  const [indexActuel, setIndexActuel] = useState(0)
  const ref = useRef(null)

  useEffect(() => {
    const observateur = new IntersectionObserver(
      ([entree]) => { if (entree.isIntersecting) setVisible(true) },
      { threshold: 0.2 }
    )
    if (ref.current) observateur.observe(ref.current)
    return () => observateur.disconnect()
  }, [])

  useEffect(() => {
    if (images.length <= 1) return
    const intervalle = setInterval(() => {
      setIndexActuel((precedent) => (precedent + 1) % images.length)
    }, 3500)
    return () => clearInterval(intervalle)
  }, [images.length])

  return (
    <div className="max-w-6xl mx-auto px-6 py-20">
      <div
        ref={ref}
        className={`flex flex-col ${inverse ? 'md:flex-row-reverse' : 'md:flex-row'} items-center gap-10 md:gap-16`}
      >
        <div className="w-full md:w-2/5 relative h-72 md:h-96 overflow-hidden rounded-sm">
          {images.map((src, index) => (
            <img
              key={src}
              src={src}
              alt={titre}
              onError={(e) => handleImageError(e)}
              className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${
                index === indexActuel ? 'opacity-100' : 'opacity-0'
              }`}
            />
          ))}
        </div>

        <div className="w-full md:w-3/5">
          <div
            className={`transition-all duration-700 ease-out ${
              visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
            }`}
          >
            <p className="text-xs font-medium uppercase tracking-[0.25em] text-gray-400 mb-4">
              {eyebrow}
            </p>
            <h2 className="font-serif text-3xl md:text-4xl text-gray-800 mb-5 leading-tight">
              {titre}
            </h2>
            <p className="text-gray-500 leading-relaxed mb-8 max-w-md">
              {description}
            </p>
            <Link
              to={lien}
              className="inline-block text-sm font-medium text-gray-900 border-b border-gray-900 pb-1 hover:opacity-60 transition"
            >
              {texteLien} →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SectionTeaser