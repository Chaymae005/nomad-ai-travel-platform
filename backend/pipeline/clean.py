"""
pipeline/clean.py

Nettoie le wikitext brut récupéré dans data/raw/ :
- découpe chaque page en sections (Comprendre, Climat, Villes...)
- retire les balises/templates wikitext de chaque section
- ne garde que les sections utiles à un agent de voyage
- sauvegarde le résultat structuré dans data/processed/

Certaines sections utiles (ex: Climat) apparaissent parfois en titre
niveau 2 (==) autonome, et parfois imbriquées en niveau 3 (===) à
l'intérieur d'une autre section (ex: sous "Comprendre"). Ce script
détecte les deux cas pour ne jamais perdre ce contenu ni le
mal-catégoriser.

Ce script ne fait AUCUN appel réseau — il retravaille uniquement
ce qui a déjà été récupéré par extract_wikivoyage.py.
"""

import json
import re
from pathlib import Path

import mwparserfromhell

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Sections qu'on garde pour le RAG (en minuscules, sans accents pour la comparaison).
# Tout le reste (Travailler, Volontariat, Apprendre, formalités de visa détaillées...)
# est écarté : hors sujet pour un agent d'infos touristiques générales.
SECTIONS_A_GARDER = {
    "introduction",   # le texte avant le premier titre de section
    "comprendre",
    "geographie",
    "climat",
    "histoire",
    "villes",
    "autres destinations",
    "securite",
    "sante",
    "respecter",
}

# Regroupe chaque section en catégorie plus large, utilisée ensuite
# pour filtrer les recherches RAG par thème (tourisme, histoire, général...)
CATEGORIE_PAR_SECTION = {
    "introduction": "general",
    "comprendre": "general",
    "geographie": "general",
    "histoire": "histoire",
    "climat": "tourisme",
    "villes": "tourisme",
    "autres destinations": "tourisme",
    "securite": "tourisme",
    "sante": "tourisme",
    "respecter": "tourisme",
}

# Titre niveau 2 (== Nom ==) ou niveau 3 (=== Nom ===), capturé avec son niveau
PATTERN_TITRE = re.compile(r"^(={2,3})\s*([^=].*?[^=])\s*\1\s*$", re.MULTILINE)


def enlever_accents(texte: str) -> str:
    """Simplifie une chaîne pour la comparaison (Sécurité -> securite)."""
    remplacements = str.maketrans("éèêëàâäùûüôöîïç", "eeeeaaauuuooiic")
    return texte.lower().translate(remplacements)


def decouper_en_sections(wikitext: str) -> dict:
    """
    Découpe le wikitext en un dictionnaire {nom_section: contenu}, en
    traitant à la fois les titres niveau 2 (==) et niveau 3 (===) dans
    un seul passage cohérent, pour ne jamais perdre de contenu imbriqué.

    Le contenu avant le premier titre est mis sous la clé "introduction".

    Chaque section (niveau 2 ou niveau 3) reçoit comme contenu tout le
    texte jusqu'au PROCHAIN titre de niveau 2 OU 3 rencontré, peu importe
    lequel des deux vient en premier. Ça veut dire qu'une section niveau 2
    qui contient des sous-titres niveau 3 aura un contenu "propre"
    (sans ses sous-sections, qui sont extraites séparément) -- ce qui
    évite la dilution/mauvaise catégorisation qu'on avait avant.

    En cas de nom de section dupliqué dans le document (ex: deux
    "Climat" à des endroits différents), on garde la version la plus
    longue plutôt que d'écraser silencieusement.
    """
    tous_les_titres = list(PATTERN_TITRE.finditer(wikitext))

    sections = {}

    debut_intro = tous_les_titres[0].start() if tous_les_titres else len(wikitext)
    sections["introduction"] = wikitext[:debut_intro].strip()

    for i, match in enumerate(tous_les_titres):
        nom_section = match.group(2).strip()
        debut_contenu = match.end()
        fin_contenu = tous_les_titres[i + 1].start() if i + 1 < len(tous_les_titres) else len(wikitext)
        contenu = wikitext[debut_contenu:fin_contenu].strip()

        if not contenu:
            continue

        if nom_section not in sections or len(contenu) > len(sections[nom_section]):
            sections[nom_section] = contenu

    return sections


def extraire_descriptions_templates(texte_brut: str) -> str:
    """
    strip_code() supprime les templates ENTIÈREMENT, y compris le texte
    utile caché dans leurs paramètres (ex: {{Ville|nom=Bangkok|description=
    La capitale animée...}}). Cette fonction récupère ce texte avant qu'il
    ne soit perdu, en particulier pour les templates Ville et Représentation
    diplomatique qui contiennent souvent une vraie description en prose.
    """
    try:
        parsed = mwparserfromhell.parse(texte_brut)
    except Exception:
        return ""

    phrases = []

    for template in parsed.filter_templates():
        nom_lieu = ""
        try:
            if template.has("nom"):
                nom_lieu = template.get("nom").value.strip_code().strip()
        except Exception:
            nom_lieu = ""

        try:
            if template.has("description"):
                description = template.get("description").value.strip_code().strip()
                if description:
                    phrases.append(f"{nom_lieu} : {description}" if nom_lieu else description)
        except Exception:
            continue

    return "\n".join(phrases)


def nettoyer_wikitext(texte_brut: str) -> str:
    """
    Retire les balises/templates wikitext d'un morceau de texte et
    retourne du texte lisible en langage naturel, en récupérant au
    passage le texte utile caché dans les templates (ex: descriptions
    de villes) qui serait sinon perdu.
    """
    descriptions_templates = extraire_descriptions_templates(texte_brut)

    try:
        parsed = mwparserfromhell.parse(texte_brut)
        texte_general = parsed.strip_code()
    except Exception:
        texte_general = texte_brut

    texte_complet = texte_general + "\n" + descriptions_templates

    texte_complet = re.sub(r"\n{3,}", "\n\n", texte_complet)
    texte_complet = re.sub(r"[ \t]+", " ", texte_complet)
    return texte_complet.strip()


def traiter_pays(raw_data: dict) -> dict:
    """
    Prend le contenu brut d'un pays (issu de data/raw/) et retourne
    une version nettoyée et filtrée, prête pour le chunking.
    """
    if not raw_data.get("wikitext"):
        return {
            "slug": raw_data["slug"],
            "country": raw_data["country"],
            "sections": [],
            "error": "Pas de wikitext disponible (échec de l'extraction)",
        }

    sections_brutes = decouper_en_sections(raw_data["wikitext"])

    sections_propres = []
    for nom_section, contenu_brut in sections_brutes.items():
        nom_normalise = enlever_accents(nom_section)

        if nom_normalise not in SECTIONS_A_GARDER:
            continue

        texte_propre = nettoyer_wikitext(contenu_brut)

        if len(texte_propre) < 30:
            continue

        sections_propres.append({
            "section": nom_section,
            "category": CATEGORIE_PAR_SECTION.get(nom_normalise, "general"),
            "text": texte_propre,
        })

    return {
        "slug": raw_data["slug"],
        "country": raw_data["country"],
        "lang": raw_data.get("lang"),
        "sections": sections_propres,
    }


def main():
    fichiers_raw = sorted(RAW_DIR.glob("*.json"))
    print(f"Nettoyage de {len(fichiers_raw)} fichiers depuis {RAW_DIR}/\n")

    for fichier in fichiers_raw:
        with open(fichier, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        resultat = traiter_pays(raw_data)

        out_path = PROCESSED_DIR / f"{resultat['slug']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(resultat, f, ensure_ascii=False, indent=2)

        n_sections = len(resultat["sections"])
        noms_sections = ", ".join(s["section"] for s in resultat["sections"])
        print(f"→ {resultat['slug']} : {n_sections} sections conservées ({noms_sections})")

    print("\nNettoyage terminé.")


if __name__ == "__main__":
    main()