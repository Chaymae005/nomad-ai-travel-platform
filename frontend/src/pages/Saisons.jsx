// pages/Saisons.jsx
import DestinationsParCategorie from '../components/DestinationsParCategorie'
import { INTROS_SAISONS } from '../constants/textesCategories'

function Saisons() {
  return (
    <div className="pt-24">
      <DestinationsParCategorie
        endpoint="saisons"
        titre="Voyager selon la saison"
        categories={[
          { valeur: 'printemps', label: 'Printemps' },
          { valeur: 'ete', label: 'Été' },
          { valeur: 'automne', label: 'Automne' },
          { valeur: 'hiver', label: 'Hiver' },
        ]}
        intros={INTROS_SAISONS}
      />
    </div>
  )
}

export default Saisons