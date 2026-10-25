import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function BoutonFavori({ nom, typeDestination }) {
  const [estFavori, setEstFavori] = useState(false)
  const [favoriId, setFavoriId] = useState(null)
  const [enCours, setEnCours] = useState(false)

  const token = localStorage.getItem('token')

  useEffect(() => {
    if (!token) return
    fetch(`${API_URL}/user/favoris/verifier?nom=${encodeURIComponent(nom)}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (r.status === 401) {
          localStorage.removeItem('token')
          return null
        }
        return r.json()
      })
      .then((data) => {
        if (!data) return
        setEstFavori(data.est_favori)
        setFavoriId(data.favori_id)
      })
      .catch(() => {})
  }, [nom, token])

  const gererClic = () => {
    if (!token) {
      alert('Connectez-vous pour ajouter des favoris.')
      return
    }
    if (enCours) return
    setEnCours(true)

    if (estFavori) {
      fetch(`${API_URL}/user/favoris/${favoriId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(() => {
          setEstFavori(false)
          setFavoriId(null)
        })
        .finally(() => setEnCours(false))
    } else {
      fetch(`${API_URL}/user/favoris`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ type_destination: typeDestination, nom }),
      })
        .then((r) => r.json())
        .then((data) => {
          setEstFavori(true)
          setFavoriId(data.id)
        })
        .finally(() => setEnCours(false))
    }
  }

  return (
    <button
      onClick={gererClic}
      disabled={enCours}
      className="w-10 h-10 flex items-center justify-center bg-white/90 hover:bg-white transition disabled:opacity-50"
      aria-label="Ajouter aux favoris"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill={estFavori ? '#ef4444' : 'none'} stroke={estFavori ? '#ef4444' : 'black'} strokeWidth="1.5">
        <path d="M12 21s-6.7-4.35-9.3-8.1C.8 10.1 1.4 6.6 4.3 5.1c2.2-1.1 4.7-.3 6 1.6l1.7 2.4 1.7-2.4c1.3-1.9 3.8-2.7 6-1.6 2.9 1.5 3.5 5 1.6 7.8C18.7 16.65 12 21 12 21z" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  )
}

export default BoutonFavori