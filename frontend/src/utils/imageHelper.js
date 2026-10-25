// src/utils/imageHelper.js

/**
 * Normalise un nom (enlève les accents, minuscules, espaces/tirets en underscores)
 */
export function normaliserNom(nom) {
  if (!nom) return ''
  return nom
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/['’]/g, '')
    .replace(/[\s-]+/g, '_')
}

// Correspondance complète français / anglais / alias vers le fichier exact dans public/images
const PAYS_VERS_IMAGE = {
  // Noms français
  'france': 'france.jpg',
  'espagne': 'spain.jpg',
  'italie': 'italy.jpg',
  'japon': 'japan.jpg',
  'maroc': 'morocco.jpg',
  'grece': 'greece.jpg',
  'thailande': 'thailand.jpg',
  'egypte': 'egypt.jpg',
  'turquie': 'turkey.jpg',
  'inde': 'india.jpg',
  'chine': 'china.jpg',
  'indonesie': 'indonesia.jpg',
  'bresil': 'brazil.jpg',
  'australie': 'australia.jpg',
  'etats_unis': 'united_states.jpg',
  'allemagne': 'germany.jpg',
  'royaume_uni': 'united_kingdom.jpg',
  'suisse': 'switzerland.jpg',
  'pays_bas': 'netherlands.jpg',
  'autriche': 'austria.jpg',
  'croatie': 'croatia.jpg',
  'islande': 'iceland.jpg',
  'portugal': 'portugal.jpg',
  'vietnam': 'vietnam.jpg',
  'coree_du_sud': 'south_korea.jpg',
  'mexique': 'mexico.jpg',
  'perou': 'peru.jpg',
  'afrique_du_sud': 'south_africa.jpg',
  'canada': 'canada.jpg',
  'argentine': 'argentina.jpg',
  'chili': 'chile.jpg',
  'colombie': 'colombia.jpg',
  'nouvelle_zelande': 'new_zealand.jpg',
  'fidji': 'fiji.jpg',
  'tunisie': 'tunisia.jpg',
  'tanzanie': 'tanzania.jpg',
  'senegal': 'senegal.jpg',
  'namibie': 'namibia.jpg',
  'cambodge': 'cambodia.jpg',
  'sri_lanka': 'sri_lanka.jpg',
  'philippines': 'philippines.jpg',
  'emirats_arabes_unis': 'united_arab_emirates.jpg',
  'russie': 'russia.jpg',

  // Noms anglais
  'spain': 'spain.jpg',
  'italy': 'italy.jpg',
  'japan': 'japan.jpg',
  'morocco': 'morocco.jpg',
  'greece': 'greece.jpg',
  'thailand': 'thailand.jpg',
  'egypt': 'egypt.jpg',
  'turkey': 'turkey.jpg',
  'india': 'india.jpg',
  'china': 'china.jpg',
  'indonesia': 'indonesia.jpg',
  'brazil': 'brazil.jpg',
  'australia': 'australia.jpg',
  'united_states': 'united_states.jpg',
  'usa': 'united_states.jpg',
  'germany': 'germany.jpg',
  'united_kingdom': 'united_kingdom.jpg',
  'uk': 'united_kingdom.jpg',
  'switzerland': 'switzerland.jpg',
  'netherlands': 'netherlands.jpg',
  'austria': 'austria.jpg',
  'croatia': 'croatia.jpg',
  'iceland': 'iceland.jpg',
  'south_korea': 'south_korea.jpg',
  'mexico': 'mexico.jpg',
  'peru': 'peru.jpg',
  'south_africa': 'south_africa.jpg',
  'argentina': 'argentina.jpg',
  'chile': 'chile.jpg',
  'colombia': 'colombia.jpg',
  'new_zealand': 'new_zealand.jpg',
  'fiji': 'fiji.jpg',
  'tunisia': 'tunisia.jpg',
  'tanzania': 'tanzania.jpg',
  'namibia': 'namibia.jpg',
  'cambodia': 'cambodia.jpg',
  'united_arab_emirates': 'united_arab_emirates.jpg',
  'uae': 'united_arab_emirates.jpg',
  'russia': 'russia.jpg',
}

// Villes avec cas particuliers d'orthographe
const VILLES_VERS_IMAGE = {
  'bangkok': 'bangkok.jpg',
  'bankok': 'bangkok.jpg',
  'chiang_mai': 'chiang_mai.jpg',
  'athenes': 'athenes.jpg',
  'fes': 'fes.jpg',
  'pekin': 'pekin.jpg',
  'seville': 'seville.jpg',
  'sao_paulo': 'sao_paulo.jpg',
  'xian': 'xi_an.jpg',
  'xi_an': 'xi_an.jpg',
  'le_caire': 'le_caire.jpg',
  'louxor': 'louxor.jpg',
  'alexandrie': 'alexandrie.jpg',
  'rio_de_janeiro': 'rio_de_janeiro.jpg',
  'new_york': 'new_york.jpg',
  'los_angeles': 'los_angeles.jpg',
  'san_francisco': 'san_francisco.jpg',
  'saint_petersbourg': 'saint-petersbourg.jpg',
}

/**
 * Résout le chemin de l'image locale (/images/...) pour n'importe quelle destination
 * (pays ou ville).
 *
 * @param {string} nom - Nom de la destination (ex: "Espagne", "Tokyo", "Bangkok", "Maroc")
 * @param {string} [type='pays'] - 'pays' ou 'ville'
 * @param {string} [paysParent=null] - Pays parent optionnel pour fallback
 * @returns {string} - Chemin d'image garanti dans /images/
 */
export function getImageUrl(nom, type = 'pays', paysParent = null) {
  if (!nom) return '/images/voyage.jpg'

  const cle = normaliserNom(nom)

  // 1. Si type ville spécifié
  if (type === 'ville') {
    if (VILLES_VERS_IMAGE[cle]) {
      return `/images/${VILLES_VERS_IMAGE[cle]}`
    }
    if (cle) {
      return `/images/${cle}.jpg`
    }
    if (paysParent) {
      return getImageUrl(paysParent, 'pays')
    }
  }

  // 2. Si pays
  if (PAYS_VERS_IMAGE[cle]) {
    return `/images/${PAYS_VERS_IMAGE[cle]}`
  }

  // 3. Recherche dans les villes si non trouvé dans pays
  if (VILLES_VERS_IMAGE[cle]) {
    return `/images/${VILLES_VERS_IMAGE[cle]}`
  }

  // 4. Nom direct normalisé
  if (cle) {
    return `/images/${cle}.jpg`
  }

  return '/images/voyage.jpg'
}

/**
 * Gestionnaire d'erreur onError pour les balises <img>
 */
export function handleImageError(e, fallback = '/images/voyage.jpg') {
  if (e?.currentTarget && !e.currentTarget.getAttribute('data-error-handled')) {
    e.currentTarget.setAttribute('data-error-handled', 'true')
    e.currentTarget.src = fallback
  }
}
