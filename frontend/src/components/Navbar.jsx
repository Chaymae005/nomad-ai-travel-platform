import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'

const API_URL = 'http://127.0.0.1:8000'

function Navbar({ estConnecte, email, onOuvrirAuth, onDeconnexion }) {
  const [destinationsOuvert, setDestinationsOuvert] = useState(false)
  const [continents, setContinents] = useState([])
  const location = useLocation()

  const surLaHome = location.pathname === '/'

  useEffect(() => {
    fetch(`${API_URL}/continents`)
      .then((r) => r.json())
      .then((data) => setContinents(Object.keys(data)))
      .catch(() => setContinents([]))
  }, [])

  const couleurTexte = surLaHome ? 'text-white' : 'text-gray-800'
  const couleurTexteAtténué = surLaHome ? 'text-white/80' : 'text-gray-500'
  const fondNavbar = surLaHome ? 'bg-white/10 backdrop-blur-md' : 'bg-white shadow-sm'

  return (
    <nav className={`fixed top-0 left-0 right-0 z-40 flex items-center justify-between px-8 py-4 transition-colors ${fondNavbar}`}>
      <Link to="/" className={`font-serif font-semibold text-lg tracking-tight ${surLaHome ? 'text-white drop-shadow' : 'text-gray-800'}`}>
        Nomad
      </Link>

      <div className={`hidden md:flex items-center gap-8 text-sm font-medium ${couleurTexte}`}>
        <div
          className="relative"
          onMouseEnter={() => setDestinationsOuvert(true)}
          onMouseLeave={() => setDestinationsOuvert(false)}
        >
          <button
            onClick={() => setDestinationsOuvert((o) => !o)}
            className="hover:opacity-70 transition"
          >
            Destinations
          </button>

          {destinationsOuvert && (
            <div className="absolute top-full left-0 mt-2 w-56 bg-white rounded-xl shadow-xl py-3 text-gray-700">
              {continents.map((continent) => (
                <Link
                  key={continent}
                  to={`/continent/${continent}`}
                  className="block px-5 py-2 text-sm hover:bg-gray-50"
                  onClick={() => setDestinationsOuvert(false)}
                >
                  {continent}
                </Link>
              ))}
            </div>
          )}
        </div>

        <Link to="/saisons" className="hover:opacity-70 transition">Saisons</Link>
        <Link to="/voyageurs" className="hover:opacity-70 transition">Voyageurs</Link>
      </div>

      {estConnecte ? (
        <div className="flex items-center gap-4">
          <Link
  to="/profil"
  className={`w-10 h-10 rounded-full border flex items-center justify-center transition ${
    surLaHome
      ? 'border-white/50 hover:bg-white/10'
      : 'border-gray-300 hover:bg-gray-50'
  }`}
  aria-label="Mon profil"
>
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={surLaHome ? 'white' : 'black'} strokeWidth="1.5">
    <circle cx="12" cy="8" r="4" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M4 20c0-4.4 3.6-8 8-8s8 3.6 8 8" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
</Link>
          <button
            onClick={onDeconnexion}
            className={`text-sm transition ${couleurTexteAtténué} hover:opacity-100`}
          >
            Déconnexion
          </button>
        </div>
      ) : (
        <button
          onClick={onOuvrirAuth}
          className={`px-4 py-2 text-sm rounded-full font-medium transition ${
            surLaHome ? 'bg-white text-gray-900 hover:bg-gray-100' : 'bg-gray-900 text-white hover:bg-gray-700'
          }`}
        >
          Connexion
        </button>
      )}
    </nav>
  )
}

export default Navbar