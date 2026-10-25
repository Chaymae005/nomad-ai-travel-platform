import { useState } from 'react'
import Card from './Card'

function CardSection({ titre, items, couleurAccent, onItemClick }) {
  const [afficherTout, setAfficherTout] = useState(false)
  const itemsAffiches = afficherTout ? items : items.slice(0, 6)

  return (
    <div className="mb-12 px-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-serif text-2xl font-semibold text-gray-800">{titre}</h3>
        {items.length > 6 && (
          <button
            onClick={() => setAfficherTout(!afficherTout)}
            className={"text-sm font-medium " + couleurAccent}
          >
            {afficherTout ? 'Réduire' : 'Afficher tout'}
          </button>
        )}
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {itemsAffiches.map((item, index) => (
          <Card
            key={index}
            titre={item.titre}
            sousTitre={item.sousTitre}
            description={item.description}
            image={item.image}
            couleurAccent={couleurAccent}
            onClick={() => { if (onItemClick) onItemClick(item) }}
          />
        ))}
      </div>
    </div>
  )
}

export default CardSection