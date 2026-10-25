import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import BoutonFavori from './BoutonFavori'
import { getImageUrl, handleImageError } from '../utils/imageHelper'

const API_URL = 'http://127.0.0.1:8000'

function DestinationsParCategorie({ endpoint, categories, intros, titre }) {
  const [categorieActive, setCategorieActive] = useState(categories[0].valeur)
  const [destinations, setDestinations] = useState([])
  const [chargement, setChargement] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    setChargement(true)
    fetch(`${API_URL}/${endpoint}/${categorieActive}`)
      .then((r) => r.json())
      .then((data) => setDestinations(data.destinations || []))
      .finally(() => setChargement(false))
  }, [categorieActive, endpoint])

  return (
    <section className="px-6 py-16 max-w-6xl mx-auto">
      <h2 className="font-serif text-3xl text-gray-800 mb-6">{titre}</h2>

      <div className="flex gap-3 mb-6 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat.valeur}
            onClick={() => setCategorieActive(cat.valeur)}
            className={`px-5 py-2 text-sm font-medium transition ${
              categorieActive === cat.valeur
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <p className="text-gray-500 max-w-2xl mb-8 leading-relaxed">
        {intros[categorieActive]}
      </p>

      {chargement ? (
        <p className="text-gray-400 text-sm">Chargement...</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-5">
          {destinations.map((dest) => (
            <div key={dest.pays} className="relative">
              <button
                onClick={() => navigate(`/pays/${dest.pays}`)}
                className="relative aspect-[4/5] overflow-hidden group text-left w-full"
              >
                <img
                  src={getImageUrl(dest.pays, 'pays')}
                  alt={dest.pays}
                  onError={(e) => handleImageError(e)}
                  className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-4">
                  <p className="text-white font-medium text-base">{dest.pays}</p>
                  <p className="text-white/70 text-sm mt-0.5 line-clamp-2">{dest.justification}</p>
                </div>
              </button>

              <div className="absolute top-3 right-3 z-10" onClick={(e) => e.stopPropagation()}>
                <BoutonFavori nom={dest.pays} typeDestination="pays" />
              </div>
            </div>
          ))}
        </div>
      )}

      {!chargement && destinations.length === 0 && (
        <p className="text-gray-400 text-sm">Aucune destination disponible pour cette catégorie pour le moment.</p>
      )}
    </section>
  )
}

export default DestinationsParCategorie