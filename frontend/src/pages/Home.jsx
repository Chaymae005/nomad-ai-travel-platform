import Hero from '../components/Hero'
import SectionTeaser from '../components/SectionTeaser'

const genererImages = (dossier, nombre) =>
  Array.from({ length: nombre }, (_, i) => `/teaser/${dossier}/${i + 1}.jpg`)

function Home() {
  return (
    <div>
      <Hero />

      <SectionTeaser
        images={genererImages('populaire', 4)}
        eyebrow="Explorer"
        titre="Destinations populaires"
        description="Du Japon au Maroc, découvrez les destinations les plus recherchées du moment, choisies pour leur richesse culturelle et leur diversité."
        lien="/destinations-populaires"
      />

      <SectionTeaser
        images={genererImages('season', 4)}
        eyebrow="Quand partir"
        titre="By Season"
        description="Chaque saison révèle un visage différent du monde. Trouvez la période idéale pour votre prochaine destination."
        lien="/saisons"
        inverse
      />

      <SectionTeaser
        images={genererImages('voyageur', 4)}
        eyebrow="Pour qui voyagez-vous"
        titre="By Traveler"
        description="Famille, couple, entre amis ou en solo — chaque voyage a ses propres besoins. Trouvez les destinations qui vous correspondent."
        lien="/voyageurs"
      />
    </div>
  )
}

export default Home