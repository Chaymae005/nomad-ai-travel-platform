import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_URL = 'http://127.0.0.1:8000'

function BarreRecherche() {
  const [terme, setTerme] = useState('')
  const [enCours, setEnCours] = useState(false)
  const navigate = useNavigate()

  const gererRecherche = async () => {
    if (!terme.trim() || enCours) return
    setEnCours(true)
    try {
      const reponse = await fetch(`${API_URL}/recherche?q=${encodeURIComponent(terme)}`)
      if (!reponse.ok) throw new Error('introuvable')
      const data = await reponse.json()

      if (data.type === 'pays') {
        navigate(`/pays/${data.nom}`)
      } else if (data.type === 'ville') {
        navigate(`/ville/${data.nom}?pays=${encodeURIComponent(data.pays)}`)
      }
    } catch {
      alert(`Aucun résultat trouvé pour "${terme}".`)
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className="flex items-center gap-4 border border-white/70 bg-white/10 backdrop-blur-sm px-6 py-4 w-full max-w-xl">
      <input
        type="text"
        value={terme}
        onChange={(e) => setTerme(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && gererRecherche()}
        placeholder="Où souhaitez-vous voyager ?"
        disabled={enCours}
        className="flex-1 outline-none text-white placeholder-white/70 bg-transparent"
      />
      <button
        onClick={gererRecherche}
        disabled={enCours}
        className="text-white text-sm font-medium tracking-wide hover:opacity-70 transition disabled:opacity-50 whitespace-nowrap"
      >
        {enCours ? '...' : 'Rechercher'}
      </button>
    </div>
  )
}

export default BarreRecherche