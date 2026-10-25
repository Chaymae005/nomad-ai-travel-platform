import { handleImageError } from '../utils/imageHelper'

function PlatformHero({ imageUrl, titre, sousTitre }) {
  return (
    <div className="relative w-full h-[70vh] overflow-hidden">
      <img
        src={imageUrl}
        alt={titre}
        onError={(e) => handleImageError(e)}
        className="absolute inset-0 w-full h-full object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />

      <div className="relative z-10 h-full flex flex-col items-start justify-end px-10 pb-16 max-w-2xl">
        <h1 className="text-3xl md:text-5xl font-bold text-white mb-3 leading-tight">
          {titre}
        </h1>
        <p className="text-base md:text-lg text-gray-100">
          {sousTitre}
        </p>
      </div>
    </div>
  )
}

export default PlatformHero