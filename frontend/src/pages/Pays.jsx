import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import PlatformHero from '../components/PlatformHero'
import WeatherWidget from '../components/WeatherWidget'
import CardSection from '../components/CardSection'
import BoutonFavori from '../components/BoutonFavori'
import { getImageUrl } from '../utils/imageHelper'

const API_URL = 'http://127.0.0.1:8000'

const STYLE_SAISON = {
  ideal: { icone: '🟢', label: 'Idéal', couleur: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  bon: { icone: '🔵', label: 'Bon', couleur: 'bg-blue-50 text-blue-700 border-blue-200' },
  moyen: { icone: '🟠', label: 'Moyen', couleur: 'bg-amber-50 text-amber-700 border-amber-200' },
  deconseille: { icone: '🔴', label: 'Déconseillé', couleur: 'bg-rose-50 text-rose-700 border-rose-200' },
}

const ICONES_SAISON = { printemps: '🌸', ete: '☀️', automne: '🍂', hiver: '❄️' }
const LABELS_SAISON = { printemps: 'Printemps', ete: 'Été', automne: 'Automne', hiver: 'Hiver' }

function Pays() {
  const { nom } = useParams()
  const [donnees, setDonnees] = useState(null)
  const [saisons, setSaisons] = useState(null)
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    setChargement(true)
    setDonnees(null)
    setSaisons(null)

    fetch(`${API_URL}/pays/${encodeURIComponent(nom)}`)
      .then((r) => r.json())
      .then((data) => setDonnees(data))
      .finally(() => setChargement(false))

    fetch(`${API_URL}/pays/${encodeURIComponent(nom)}/saisons`)
      .then((r) => r.json())
      .then((data) => { if (!data.error) setSaisons(data) })
  }, [nom])

  if (chargement) {
    return <div className="pt-32 text-center text-gray-400">Chargement...</div>
  }

  if (!donnees || donnees.error) {
    return <div className="pt-32 text-center text-gray-400">Aucune information disponible pour {nom}.</div>
  }

  const imageLocale = getImageUrl(donnees.nom || nom, 'pays')

  return (
    <div>
      <div className="relative">
        <PlatformHero
          imageUrl={imageLocale}
          titre={donnees.nom}
          sousTitre={donnees.region}
        />
        <div className="absolute top-24 right-6 z-50">
          <BoutonFavori nom={donnees.nom} typeDestination="pays" />
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-14">

        {/* ===== MÉTÉO DE LA CAPITALE ===== */}
        {donnees.capitale && (
          <div className="mb-10">
            <WeatherWidget ville={donnees.capitale} couleurAccent="text-emerald-600" />
          </div>
        )}

        {/* ===== PRÉSENTATION UNIFIÉE ===== */}
        {donnees.presentation && (
          <div className="mb-12 bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
            <h2 className="font-serif text-2xl text-gray-800 mb-4">
              À la découverte de {donnees.nom}
            </h2>
            <p className="font-serif text-lg text-gray-700 leading-relaxed whitespace-pre-line">
              {donnees.presentation}
            </p>
          </div>
        )}

        {/* ===== INFOS CLÉS ===== */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-gray-100 mb-14 rounded-xl overflow-hidden shadow-sm">
          {[
            { label: 'Capitale', valeur: donnees.capitale },
            { label: 'Langues', valeur: donnees.langues?.join(', ') },
            { label: 'Devise', valeur: donnees.devises?.join(', ') },
            { label: 'Fuseau horaire', valeur: donnees.fuseau_horaire },
          ].map((item) => (
            <div key={item.label} className="bg-white p-4">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">{item.label}</p>
              <p className="text-sm font-medium text-gray-800">{item.valeur || '—'}</p>
            </div>
          ))}
        </div>

        {/* ===== MEILLEURE PÉRIODE (SAISONS) ===== */}
        {saisons && (
          <div className="mb-14">
            <h2 className="font-serif text-2xl text-gray-800 mb-1">Meilleure période pour voyager</h2>
            <p className="text-sm text-gray-400 mb-6">Basé sur le climat et l'affluence touristique</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {['printemps', 'ete', 'automne', 'hiver'].map((saison) => {
                const info = saisons[saison]
                if (!info) return null
                const style = STYLE_SAISON[info.recommandation] || STYLE_SAISON.moyen

                return (
                  <div key={saison} className={`rounded-xl border p-5 ${style.couleur}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-serif text-lg flex items-center gap-2">
                        <span className="text-xl">{ICONES_SAISON[saison]}</span>
                        {LABELS_SAISON[saison]}
                      </span>
                      <span className="text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded-full bg-white/60">
                        {style.label}
                      </span>
                    </div>
                    <p className="text-sm leading-relaxed opacity-90">{info.justification}</p>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* ===== VILLES POPULAIRES ===== */}
      {donnees.villes_populaires?.length > 0 && (
        <div className="max-w-5xl mx-auto px-6 mb-16">
          <CardSection
            titre="Villes populaires"
            items={donnees.villes_populaires.map((ville) => ({
              titre: ville,
              image: getImageUrl(ville, 'ville', donnees.nom),
            }))}
            couleurAccent="text-emerald-600"
            onItemClick={(item) => { window.location.href = `/ville/${item.titre}?pays=${encodeURIComponent(donnees.nom)}` }}
          />
        </div>
      )}
    </div>
  )
}

export default Pays