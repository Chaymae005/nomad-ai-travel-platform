import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import AgentChatBox from './components/AgentChatBox'
import AuthModal from './components/AuthModal'
import Home from './pages/Home'
import Continent from './pages/Continent'
import Pays from './pages/Pays'
import Ville from './pages/Ville'
import Profil from './pages/Profil'
import Saisons from './pages/Saisons'
import Voyageurs from './pages/Voyageurs'
import DestinationsPopulaires from './pages/DestinationsPopulaires'

function App() {
  const [utilisateur, setUtilisateur] = useState(null)
  const [authModalOuvert, setAuthModalOuvert] = useState(false)
  const [chargementSession, setChargementSession] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setChargementSession(false)
      return
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      setUtilisateur({ email: payload.sub, nom: payload.nom })
    } catch {
      localStorage.removeItem('token')
    } finally {
      setChargementSession(false)
    }
  }, [])

  const gererConnexionReussie = (donneesUtilisateur) => {
    setUtilisateur(donneesUtilisateur)
    setAuthModalOuvert(false)
  }

  const gererDeconnexion = () => {
    setUtilisateur(null)
    localStorage.removeItem('token')
  }

  if (chargementSession) {
    return null
  }

  return (
    <BrowserRouter>
      <Navbar
        estConnecte={!!utilisateur}
        email={utilisateur?.email}
        onOuvrirAuth={() => setAuthModalOuvert(true)}
        onDeconnexion={gererDeconnexion}
      />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/continent/:nom" element={<Continent />} />
        <Route path="/pays/:nom" element={<Pays />} />
        <Route path="/ville/:nom" element={<Ville />} />
        <Route path="/profil" element={<Profil utilisateur={utilisateur} />} />
        <Route path="/saisons" element={<Saisons />} />
        <Route path="/voyageurs" element={<Voyageurs />} />
        <Route path="/destinations-populaires" element={<DestinationsPopulaires />} />
      </Routes>

      <AgentChatBox />

      {authModalOuvert && (
        <AuthModal
          onFermer={() => setAuthModalOuvert(false)}
          onConnexionReussie={gererConnexionReussie}
        />
      )}
    </BrowserRouter>
  )
}

export default App