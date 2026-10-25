import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function ItemModal({ item, onFermer, outilsActifs, promptDomaine, couleurAccent }) {
  const [reponse, setReponse] = useState('')
  const [enChargement, setEnChargement] = useState(true)

  useEffect(() => {
    const poserQuestionAutomatique = async () => {
      setEnChargement(true)
      try {
        const res = await fetch(`${API_URL}/agent/ask`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: `Donne-moi une description riche et détaillée de : ${item.nom}. Sois descriptif, comme pour une brochure.`,
            history: [],
            outils_actifs: outilsActifs,
            prompt_domaine: promptDomaine,
          }),
        })
        const data = await res.json()
        setReponse(data.reponse)
      } catch {
        setReponse("Impossible de récupérer les informations pour le moment.")
      } finally {
        setEnChargement(false)
      }
    }
    poserQuestionAutomatique()
  }, [item.nom])

  return (
    <div className="fixed inset-0 z-50 bg-white overflow-y-auto">
      <button
        onClick={onFermer}
        className="fixed top-6 right-6 z-20 w-10 h-10 flex items-center justify-center bg-white shadow-md rounded-full text-gray-600 hover:bg-gray-50"
      >
        ✕
      </button>

      <div className="relative w-full h-[60vh]">
        <img src={item.image} alt={item.nom} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 px-10 md:px-16 pb-12">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] mb-3 text-white/80">
            À la une
          </p>
          <h2 className="font-serif text-4xl md:text-6xl text-white leading-tight max-w-3xl">
            {item.nom}
          </h2>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-8 py-14">
        {enChargement ? (
          <div className={"flex items-center gap-2 text-sm " + couleurAccent}>
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
            <span className="text-gray-400">Préparation du contenu...</span>
          </div>
        ) : (
          <p className="text-gray-600 leading-relaxed text-lg whitespace-pre-line font-light">
            {reponse}
          </p>
        )}
      </div>
    </div>
  )
}

export default ItemModal