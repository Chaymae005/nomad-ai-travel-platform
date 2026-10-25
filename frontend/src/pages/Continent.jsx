// src/pages/Continent.jsx
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import CardSection from '../components/CardSection'
import { getImageUrl } from '../utils/imageHelper'

const API_URL = 'http://127.0.0.1:8000'

function Continent() {
  const { nom } = useParams()
  const navigate = useNavigate()
  const [pays, setPays] = useState([])
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    setChargement(true)
    fetch(`${API_URL}/continents/${encodeURIComponent(nom)}`)
      .then((r) => r.json())
      .then((data) => setPays(data.pays || []))
      .finally(() => setChargement(false))
  }, [nom])

  if (chargement) {
    return <div className="pt-32 text-center text-gray-400">Chargement...</div>
  }

  return (
    <div className="pt-24 px-6 max-w-6xl mx-auto pb-16">
      <h1 className="font-serif text-4xl text-gray-800 mb-2">{nom}</h1>
      <p className="text-gray-500 mb-10">{pays.length} destinations à découvrir</p>

      <CardSection
        titre=""
        items={pays.map((nomPays) => ({
          titre: nomPays,
          image: getImageUrl(nomPays, 'pays'),
        }))}
        couleurAccent="text-blue-600"
        onItemClick={(item) => navigate(`/pays/${item.titre}`)}
      />
    </div>
  )
}

export default Continent