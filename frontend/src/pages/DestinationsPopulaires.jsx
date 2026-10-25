// src/pages/DestinationsPopulaires.jsx
import { useState, useEffect } from 'react'
import CardSection from '../components/CardSection'
import { getImageUrl } from '../utils/imageHelper'

const API_URL = 'http://127.0.0.1:8000'

function DestinationsPopulaires() {
  const [destinations, setDestinations] = useState([])
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    fetch(`${API_URL}/destinations-populaires`)
      .then((r) => r.json())
      .then((data) => setDestinations(data.destinations || []))
      .finally(() => setChargement(false))
  }, [])

  return (
    <div className="pt-24 pb-16">
      <div className="px-6 max-w-6xl mx-auto mb-10">
        <h1 className="font-serif text-4xl text-gray-800 mb-2">Destinations populaires</h1>
        <p className="text-gray-500">Les destinations les plus recherchées du moment.</p>
      </div>

      {chargement ? (
        <p className="text-center text-gray-400 text-sm">Chargement...</p>
      ) : (
        <CardSection
          titre=""
          items={destinations.map((nom) => ({
            titre: nom,
            image: getImageUrl(nom, 'pays'),
          }))}
          couleurAccent="text-blue-600"
          onItemClick={(item) => { window.location.href = `/pays/${item.titre}` }}
        />
      )}
    </div>
  )
}

export default DestinationsPopulaires