import { useState, useEffect } from 'react'
import { fetchAvecAuth } from '../utils/api'
import CarteFavoris from '../components/CarteFavoris'
import { getImageUrl, handleImageError } from '../utils/imageHelper'

function Profil({ utilisateur }) {
  const [favoris, setFavoris] = useState([])
  const [recommandations, setRecommandations] = useState([])
  const [pointsCarte, setPointsCarte] = useState([])
  const [chargement, setChargement] = useState(true)

  const chargerTout = () => {
    setChargement(true)

    Promise.all([
      fetchAvecAuth('/user/favoris').then((r) => r.json()),
      fetchAvecAuth('/user/recommandations').then((r) => r.json()),
      fetchAvecAuth('/user/favoris/carte').then((r) => r.json()),
    ])
      .then(([f, rec, carte]) => {
        setFavoris(f)
        setRecommandations(rec.recommandations || [])
        setPointsCarte(carte.points || [])
      })
      .finally(() => setChargement(false))
  }

  useEffect(() => {
    if (utilisateur) chargerTout()
  }, [utilisateur])

  const supprimerFavori = (id) => {
    fetchAvecAuth(`/user/favoris/${id}`, {
      method: 'DELETE',
    }).then(() => chargerTout())
  }

  if (!utilisateur) {
    return (
      <div className="pt-32 text-center text-gray-400">
        Connectez-vous pour accéder à votre profil.
      </div>
    )
  }

  if (chargement) {
    return (
      <div className="pt-32 text-center text-gray-400">
        Chargement...
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#f7f8f7] pt-24 px-6 pb-16">

      <div className="max-w-7xl mx-auto">

        {/* =====================================================
            HEADER / WELCOME
        ====================================================== */}
        <div className="mb-8">
          <p className="text-sm text-gray-400 mb-1">Welcome back,</p>
          <h1 className="text-2xl font-semibold text-gray-800">{utilisateur.nom} !</h1>
        </div>


        {/* =====================================================
            MAIN CONTENT
        ====================================================== */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">


          {/* =================================================
              LEFT : FAVORITES + RECOMMENDATIONS
          ================================================== */}
          <div className="lg:col-span-2 space-y-8">


            {/* =================================================
                FAVORIS
            ================================================== */}
            <section>

              <div className="flex items-center justify-between mb-4">

                <div>
                  <h2 className="text-xl font-semibold text-gray-800">
                    Mes destinations favorites
                  </h2>

                  <p className="text-sm text-gray-400 mt-1">
                    Les endroits que vous souhaitez découvrir
                  </p>
                </div>

              </div>


              {favoris.length === 0 ? (

                <div className="bg-white rounded-2xl border border-gray-100 p-8 text-center">
                  <div className="text-4xl mb-3">
                    ❤️
                  </div>

                  <p className="text-gray-500">
                    Vous n'avez pas encore ajouté de destination.
                  </p>

                  <p className="text-sm text-gray-400 mt-1">
                    Explorez nos destinations et ajoutez vos coups de cœur.
                  </p>
                </div>

              ) : (

                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">

                  {favoris.map((f) => (

                    <div
                      key={f.id}
                      onClick={() => {
                        window.location.href =
                          `/${f.type_destination}/${f.nom}`
                      }}
                      className="group bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm hover:shadow-md transition cursor-pointer"
                    >

                      {/* Image */}
                      <div className="relative h-44 overflow-hidden">

                        <img
                          src={getImageUrl(f.nom, f.type_destination)}
                          alt={f.nom}
                          onError={(e) => handleImageError(e)}
                          className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                        />

                        {/* Heart */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            supprimerFavori(f.id)
                          }}
                          className="absolute top-3 right-3 w-9 h-9 rounded-full bg-white/90 backdrop-blur flex items-center justify-center text-red-500 shadow-sm hover:bg-white transition"
                        >
                          ♥
                        </button>

                      </div>


                      {/* Information */}
                      <div className="p-4">

                        <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">
                          {f.type_destination || 'Destination'}
                        </p>

                        <h3 className="font-semibold text-gray-800 text-lg">
                          {f.nom}
                        </h3>

                        <div className="mt-3">
                          <span className="text-xs text-gray-400">
                            Découvrir →
                          </span>
                        </div>

                      </div>

                    </div>

                  ))}

                </div>

              )}

            </section>


            {/* =================================================
                RECOMMANDATIONS
            ================================================== */}
            <section>

              <div className="flex items-center justify-between mb-4">

                <div>
                  <h2 className="text-xl font-semibold text-gray-800">
                    Recommandé pour vous
                  </h2>

                  <p className="text-sm text-gray-400 mt-1">
                    Des destinations qui pourraient vous plaire
                  </p>
                </div>

              </div>


              {recommandations.length === 0 ? (

                <div className="bg-white rounded-2xl border border-gray-100 p-6">
                  <p className="text-sm text-gray-400">
                    Ajoutez quelques destinations à vos favoris pour recevoir
                    des recommandations personnalisées.
                  </p>
                </div>

              ) : (

                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">

                  {recommandations.map((r, index) => (

                    <div
                      key={r.pays}
                      onClick={() => {
                        window.location.href = `/pays/${r.pays}`
                      }}
                      className={`flex items-center gap-4 p-4 cursor-pointer hover:bg-gray-50 transition ${
                        index !== recommandations.length - 1
                          ? 'border-b border-gray-100'
                          : ''
                      }`}
                    >

                      {/* Image */}
                      <div className="w-20 h-16 rounded-xl overflow-hidden flex-shrink-0">

                        <img
                          src={getImageUrl(r.pays, 'pays')}
                          alt={r.pays}
                          onError={(e) => handleImageError(e)}
                          className="w-full h-full object-cover"
                        />

                      </div>


                      {/* Text */}
                      <div className="flex-1 min-w-0">

                        <h3 className="font-medium text-gray-800">
                          {r.pays}
                        </h3>

                        <p className="text-xs text-gray-400 mt-1">
                          Une destination sélectionnée pour vous
                        </p>

                      </div>


                      {/* Arrow */}
                      <div className="text-gray-300">
                        →
                      </div>

                    </div>

                  ))}

                </div>

              )}

            </section>

          </div>


          {/* =================================================
              RIGHT : MAP
          ================================================== */}
          <div>

            <div className="mb-4">
              <h2 className="text-xl font-semibold text-gray-800">
                Mes destinations
              </h2>
            </div>


            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">

              <div className="h-[400px]">

                <CarteFavoris points={pointsCarte} />

              </div>

            </div>

          </div>

        </div>

      </div>

    </div>
  )
}

export default Profil