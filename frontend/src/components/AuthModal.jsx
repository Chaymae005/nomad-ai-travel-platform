import { useState } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function AuthModal({ onFermer, onConnexionReussie }) {
  const [mode, setMode] = useState('login') // 'login' ou 'register'
  const [nom, setNom] = useState('')
  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [erreur, setErreur] = useState('')
  const [enChargement, setEnChargement] = useState(false)

  const gererSoumission = async (e) => {
    e.preventDefault()
    setErreur('')
    setEnChargement(true)

    const route = mode === 'login' ? '/auth/login' : '/auth/register'
    const body =
      mode === 'register'
        ? { nom, email, mot_de_passe: motDePasse }
        : { email, mot_de_passe: motDePasse }

    try {
      const reponse = await fetch(`${API_URL}${route}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const data = await reponse.json()

      if (!reponse.ok) {
        setErreur(data.detail || 'Une erreur est survenue.')
        return
      }

      localStorage.setItem('token', data.token)
      onConnexionReussie(data)
    } catch {
      setErreur('Impossible de contacter le serveur.')
    } finally {
      setEnChargement(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center px-6">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 relative">
        <button
          onClick={onFermer}
          className="absolute top-5 right-5 text-gray-400 hover:text-gray-700 text-lg"
        >
          ✕
        </button>

        <h2 className="font-serif text-2xl text-gray-800 mb-1">
          {mode === 'login' ? 'Connexion' : 'Créer un compte'}
        </h2>
        <p className="text-sm text-gray-400 mb-6">
          {mode === 'login' ? "Ravis de vous revoir." : 'Rejoignez-nous en quelques secondes.'}
        </p>

        <form onSubmit={gererSoumission} className="space-y-4">
          {mode === 'register' && (
            <div>
              <label className="block text-sm text-gray-600 mb-1">Nom</label>
              <input
                type="text"
                value={nom}
                onChange={(e) => setNom(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-gray-400 transition"
              />
            </div>
          )}

          <div>
            <label className="block text-sm text-gray-600 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-gray-400 transition"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Mot de passe</label>
            <input
              type="password"
              value={motDePasse}
              onChange={(e) => setMotDePasse(e.target.value)}
              required
              minLength={6}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl outline-none focus:border-gray-400 transition"
            />
          </div>

          {erreur && <p className="text-sm text-red-500">{erreur}</p>}

          <button
            type="submit"
            disabled={enChargement}
            className="w-full py-3 bg-gray-900 text-white rounded-xl font-medium hover:bg-gray-700 transition disabled:opacity-50"
          >
            {enChargement ? '...' : mode === 'login' ? 'Se connecter' : "S'inscrire"}
          </button>
        </form>

        <p className="text-sm text-gray-400 text-center mt-6">
          {mode === 'login' ? "Pas encore de compte ? " : 'Déjà un compte ? '}
          <button
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
            className="text-gray-800 font-medium hover:underline"
          >
            {mode === 'login' ? "S'inscrire" : 'Se connecter'}
          </button>
        </p>
      </div>
    </div>
  )
}

export default AuthModal