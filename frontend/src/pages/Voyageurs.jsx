// pages/Voyageurs.jsx
import DestinationsParCategorie from '../components/DestinationsParCategorie'
import { INTROS_PROFILS } from '../constants/textesCategories'

function Voyageurs() {
  return (
    <div className="pt-24">
      <DestinationsParCategorie
        endpoint="voyageurs"
        titre="Voyager selon vos envies"
        categories={[
          { valeur: 'famille', label: 'Famille' },
          { valeur: 'couple', label: 'Couple' },
          { valeur: 'amis', label: 'Entre amis' },
          { valeur: 'solo', label: 'Solo' },
        ]}
        intros={INTROS_PROFILS}
      />
    </div>
  )
}

export default Voyageurs