import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import PlatformHero from '../components/PlatformHero'
import WeatherWidget from '../components/WeatherWidget'
import BoutonFavori from '../components/BoutonFavori'
import { getImageUrl } from '../utils/imageHelper'

const API_URL = 'http://127.0.0.1:8000'

function Ville() {
  const { nom } = useParams()
  const [searchParams] = useSearchParams()
  const pays = searchParams.get('pays') || ''

  const [donnees, setDonnees] = useState(null)
  const [restaurants, setRestaurants] = useState(null)
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    if (!pays) return
    setChargement(true)
    setDonnees(null)
    setRestaurants(null)

    fetch(`${API_URL}/ville/${encodeURIComponent(nom)}?pays=${encodeURIComponent(pays)}`)
      .then((r) => r.json())
      .then((data) => setDonnees(data))
      .finally(() => setChargement(false))

    fetch(`${API_URL}/ville/${encodeURIComponent(nom)}/restaurants?pays=${encodeURIComponent(pays)}`)
      .then((r) => r.json())
      .then((data) => { if (!data.error) setRestaurants(data.suggestions) })
  }, [nom, pays])

  if (chargement) {
    return <div className="pt-32 text-center text-gray-400">Chargement...</div>
  }

  if (!donnees || donnees.error) {
    return <div className="pt-32 text-center text-gray-400">Aucune information disponible pour {nom}.</div>
  }

  const imageHero = getImageUrl(donnees.nom || nom, 'ville', donnees.pays || pays)

  return (
    <div>
      <div className="relative">
        <PlatformHero
          imageUrl={imageHero}
          titre={donnees.nom}
          sousTitre={donnees.pays}
        />
        <div className="absolute top-24 right-6 z-50">
          <BoutonFavori nom={donnees.nom} typeDestination="ville" />
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-12">
        {donnees.presentation && (
          <div className="mb-10">
            <h2 className="font-serif text-2xl text-gray-800 mb-3">Présentation</h2>
            <p className="text-gray-600 leading-relaxed whitespace-pre-line">{donnees.presentation}</p>
          </div>
        )}

        {donnees.attractions && (
          <div className="mb-10">
            <h2 className="font-serif text-2xl text-gray-800 mb-3">Attractions incontournables</h2>
            <p className="text-gray-600 leading-relaxed whitespace-pre-line">{donnees.attractions}</p>
          </div>
        )}

        {donnees.quartiers && (
          <div className="mb-10">
            <h2 className="font-serif text-2xl text-gray-800 mb-3">Quartiers à visiter</h2>
            <p className="text-gray-600 leading-relaxed whitespace-pre-line">{donnees.quartiers}</p>
          </div>
        )}

        {donnees.meteo && (
          <div className="mb-10">
            <WeatherWidget ville={donnees.nom} couleurAccent="text-blue-600" />
          </div>
        )}

        {restaurants && restaurants.length > 0 && (
          <div className="mb-10">
            <h2 className="font-serif text-2xl text-gray-800 mb-4">À goûter sur place</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {restaurants.map((s, i) => (
                <div key={i} className="bg-white rounded-2xl shadow-sm p-4">
                  <p className="text-sm font-semibold text-gray-800 mb-1">{s.nom}</p>
                  <p className="text-xs text-gray-500 leading-relaxed">{s.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Ville