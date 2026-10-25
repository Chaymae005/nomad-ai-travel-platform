import BoutonFavori from './BoutonFavori'
import { getImageUrl, handleImageError } from '../utils/imageHelper'

function Card({ titre, sousTitre, description, image, couleurAccent, onClick, favori = true }) {
  const sourceImage = image || getImageUrl(titre)

  return (
    <div
      onClick={onClick}
      className="relative aspect-[3/4] overflow-hidden bg-white shadow-sm hover:shadow-lg transition cursor-pointer group"
    >
      <img
        src={sourceImage}
        alt={titre}
        onError={(e) => handleImageError(e)}
        className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition duration-500"
      />

      {favori && (
        <div className="absolute top-3 right-3 z-10" onClick={(e) => e.stopPropagation()}>
          <BoutonFavori nom={titre} typeDestination="pays" />
        </div>
      )}

      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/5 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 p-5">
        <h4 className="font-serif text-white text-xl leading-tight">{titre}</h4>
        {sousTitre && <p className={`text-sm mt-1 ${couleurAccent || 'text-white/80'}`}>{sousTitre}</p>}
      </div>

      {description && (
        <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition duration-300 flex flex-col justify-end p-6">
          <h4 className="font-serif text-white text-xl mb-2">{titre}</h4>
          <p className="text-white/80 text-sm leading-relaxed line-clamp-4 mb-3">{description}</p>
          <span className="text-white text-sm font-medium underline underline-offset-2">Voir plus →</span>
        </div>
      )}
    </div>
  )
}

export default Card