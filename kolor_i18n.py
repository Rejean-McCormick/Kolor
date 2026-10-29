# -*- coding: utf-8 -*-
"""French/English UI strings. Persistent choice is separate from project state.

Translation affects the interface only: JSON IDs, source prompts, paths, and
export schemas are not translated, ensuring compatibility with older projects.
"""
from __future__ import annotations
import json
from pathlib import Path

LANGUAGES = ('fr', 'en')

EN = {
    'Kolor Studio • Personnages Kontexte': 'Kolor Studio • Kontexte Characters',
    'STUDIO · FABRIQUE DE PERSONNAGES': 'STUDIO · CHARACTER WORKSHOP',
    'Personnages de Kontexte': 'Kontexte Characters',
    'Rechercher un rôle': 'Search for a role',
    'Aucune planche importée\n\nCrée une planche ou importe une image carrée (1:1), sans taille imposée.': 'No sheet imported\n\nGenerate a sheet or import a square image (1:1), at any resolution.',
    'Choisis la meilleure pose pour Kolor et Kontexte': 'Select the best pose for Kolor and Kontexte',
    '1 · Principal': '1 · Main',
    '2 · Bonjour': '2 · Greeting',
    '3 · Accessoire': '3 · Accessory',
    '4 · Action': '4 · Action',
    '1. Créer une planche': '1. Create a sheet',
    'Copier le prompt du rôle': 'Copy role prompt',
    'Importer une planche PNG…': 'Import a PNG sheet…',
    'Préparer les 38 prompts': 'Prepare all 38 prompts',
    '2. Génération automatique (API)': '2. Automatic generation (API)',
    'Facultatif : frais API séparés de ChatGPT.': 'Optional: API fees are billed separately from ChatGPT.',
    'Clé API (non enregistrée)': 'API key (not saved)',
    'Modèle': 'Model',
    'Qualité': 'Quality',
    'Générer ce rôle (1 planche)': 'Generate this role (1 sheet)',
    'Générer les rôles manquants…': 'Generate missing roles…',
    'Arrêter après cette planche': 'Stop after current sheet',
    '3. Palettes et skin tones': '3. Palettes and skin tones',
    'Palette multicolore (base)': 'Multicolor palette (base)',
    'Carnation / skin tone': 'Skin tone',
    'Chaque case colorée est modifiable (sauf la peau).': 'Customize each color swatch (skin uses the separate skin tone menu).',
    'Peau': 'Skin', 'Cheveux': 'Hair', 'Haut': 'Top', 'Bas': 'Bottom',
    'Chaussures': 'Shoes', 'Objets': 'Accessories',
    'Traits : #000000 (fixe)  •  Fond : #FFFFFF (fixe)': 'Outlines: #000000 (locked)  •  Background: #FFFFFF (locked)',
    'Générer une combinaison multicolore': 'Generate multicolor combination',
    'Revenir aux couleurs de la palette': 'Reset custom colors to palette',
    'Voir les couleurs techniques d’origine': 'Show original technical colors',
    '4. Valider et exporter': '4. Review and export',
    'J’ai vérifié le personnage': 'I have reviewed this character',
    'Exporter pour Kolor / Kontexte': 'Export for Kolor / Kontexte',
    'Ouvrir le dossier du projet': 'Open project folder',
    'Aucune planche pour ce rôle\n\nCopie le prompt ou génère une planche.': 'No sheet for this role\n\nCopy the prompt or generate a sheet.',
    'Erreur d’ouverture de la planche': 'Could not open the sheet',
    'Découpage prêt · vérifie les six aplats et la cohérence visuelle.': 'Crops ready · review the six flat colors and visual consistency.',
    'Une planche = quatre variantes du même rôle, pas quatre rôles différents.': 'One sheet = four poses of the same character, not four different roles.',
    'Aperçu technique uniquement.': 'Viewing technical source colors only.',
    'Peau et vêtements indépendants. Noir et blanc fixes. Les PNG sources restent intacts.': 'Skin and clothing colors are independent. Black and white are locked. Source PNGs remain unchanged.',
    'Palette invalide': 'Invalid palette',
    'Couleur interdite': 'Color not allowed',
    'Couleur — {region}': 'Color — {region}',
    'Prompt copié : colle-le dans un outil de génération d’images.': 'Prompt copied: paste it into an image-generation tool.',
    'Prompts prêts': 'Prompts ready',
    'Importer la planche 2 × 2': 'Import 2 × 2 sheet',
    'Images': 'Images',
    'Ajustement du découpage': 'Crop adjustment',
    'Importation impossible': 'Import failed',
    'Importe d’abord une planche pour sélectionner une pose.': 'Import a sheet before selecting a pose.',
    'Rôle vérifié.': 'Role reviewed.',
    'Validation retirée.': 'Review status cleared.',
    'Terminé': 'All done',
    'Les 38 rôles ont déjà une planche.': 'All 38 roles already have a sheet.',
    'Confirmer la génération payante': 'Confirm paid generation',
    'Génération active': 'Generation running',
    'Une série est déjà en cours.': 'A batch is already running.',
    'Clé API manquante': 'Missing API key',
    'Entre une clé API OpenAI. Elle n’est pas sauvegardée.\n\nSinon, copie les prompts et importe les planches manuellement.': 'Enter an OpenAI API key. It will not be saved.\n\nAlternatively, copy the prompts and import the sheets manually.',
    'Arrêt demandé : fin de la planche en cours, puis arrêt.': 'Stop requested: will finish the current sheet, then stop.',
    'Série terminée. Vérifie les planches et sélectionne une pose par rôle.': 'Batch completed. Review the sheets and select one pose for each role.',
    'Aucune image': 'No images',
    'Importe ou génère au moins une planche.': 'Import or generate at least one sheet.',
    'Export impossible': 'Export failed',
    'Quitter Kolor Studio': 'Exit Kolor Studio',
    'Une génération est en cours. Quitter l’interrompra peut-être sans sauvegarder la planche active.\nQuitter ?': 'A generation is running. Exiting may interrupt it without saving the active sheet.\nExit anyway?',
    'Palette': 'Palette',
    'Personnage possiblement absent': 'Character may be missing',
    'Un personnage ou un trait touche le bord': 'A character or outline touches the edge',
    'Teintes techniques approximatives': 'Technical color regions may be inaccurate',
    'Côté impair : un pixel blanc a été ajouté à droite et en bas pour obtenir quatre cases égales, sans réduire ni rogner l’image.': 'Odd side length: one white pixel was added to the right and bottom to create four equal cells without scaling or cropping.',
    'Prêt — sélectionne un rôle pour commencer.': 'Ready — select a role to get started.',
    'Langue': 'Language',
    'Interface en français.': 'Interface in French.',
    'Interface in English.': 'Interface in English.',
}

ROLE_EN = {
 'architecte':'Architect','astronaute':'Astronaut','boulanger':'Baker','bucheron':'Lumberjack',
 'chevalier':'Knight','clown':'Clown','coiffeuse':'Hairdresser','comptable':'Accountant',
 'createur-jeux':'Video Game Creator','cuisinier':'Cook','danseur':'Dancer',
 'dresseur-animaux':'Animal Educator','ecrivain':'Writer','explorateur':'Explorer',
 'extraterrestre':'Alien','fermier':'Farmer','forgeron':'Blacksmith','inventeur':'Inventor',
 'jardinier':'Gardener','lecteur':'Reader','mecanicien':'Mechanic','menuisier':'Carpenter',
 'messager':'Messenger','metteur-en-scene':'Stage Director','mineur':'Miner','musicien':'Musician',
 'mystique':'Mystic','origamiste':'Origami Master','pecheur':'Fisherman',
 'peintre':'Painter','photographe':'Photographer','politicien':'Politician',
 'redacteur':'Editor','regisseur':'Stage Manager','scientifique':'Scientist',
 'sorciere':'Witch','traducteur':'Translator','veterinaire':'Veterinarian',
}

PALETTE_EN = {
 'technique':'Original technical colors','classique':'Classic','pastel':'Pastel','foret':'Forest',
 'ocean':'Ocean','soleil':'Sunshine','fete':'Celebration','automne':'Autumn','nuit':'Starry Night',
 'tropical':'Tropical','bonbon':'Candy','urbain':'Urban','arc-en-ciel':'Rainbow',
}
SKIN_EN = {
 'technique':'Technical yellow','porcelaine':'Porcelain','ivoire':'Ivory','clair':'Light',
 'dore':'Golden','beige':'Warm beige','cuivre':'Copper','caramel':'Caramel',
 'bronze':'Bronze','brun':'Brown','fonce':'Dark','ebene':'Ebony',
}

ACTION_EN = dict(zip(
 'adapter|additionner|aider|articuler|assembler|cadrer|calculer|cartographier|classer|classifier|colorier|communiquer|comparer|composer|compter|compter les temps|concevoir|confirmer|coordonner|corriger|créer une potion fictive|dessiner|diagnostiquer|diagnostiquer fictivement|documenter|déboguer|décoder|décrire des règles|délibérer|enseigner|expliquer|explorer|exposer|installer|interpréter|inviter|jongler|jouer|lire|livrer|mesurer|négocier|observer|organiser|planifier|plier|préparer des accessoires|préparer des recettes|présenter|raconter|reformuler|relire|remettre|rencontrer|rythmer|récolter|rédiger|réparer|répéter|semer|sélectionner|tester|traduire|vendre|voter|vérifier|écouter'.split('|'),
 'adapt|add|help|articulate|assemble|frame|calculate|map|sort|classify|color|communicate|compare|compose|count|keep time|design|confirm|coordinate|correct|create a pretend potion|draw|diagnose|pretend to diagnose|document|debug|decode|describe rules|deliberate|teach|explain|explore|present|install|interpret|invite|juggle|play|read|deliver|measure|negotiate|observe|organize|plan|fold|prepare props|prepare recipes|present|tell stories|rephrase|proofread|hand over|meet|set rhythm|harvest|write|repair|rehearse|sow|select|test|translate|sell|vote|check|listen'.split('|')
))

OBJECT_EN = dict(zip(
 'Klownkoins|accessoires|affiche|arbre|arrosoir|astronef de carton|balance|bouclier de papier|boussole|brouillon|cahier|cailloux|carnet|carte|carte stellaire|carton|chaises|chanson|chapeau|ciseaux de papier|conte|costume|croquis|dictionnaire|discours|dossier|décor|engrenage carton|enveloppe|facture|fiche espèce|filet fictif|fusée de papier|galerie|graines|grille|habitat|ingrédients fictifs|instrument|invitation|lampes factices|lettre|mandat|manuscrit|maquette|menu|message|mesure|mesures|micro factice|miroir|modèle|musique|métadonnées|métal fictif|ordre du jour|pain|palette|panier|papier|partition|peluche|personnage|photo|pinceau|plan|planche de carton|planning|plante|pot|potion fictive|prototype carton|pupitre|recette|registre|règle|schéma|scène|semences|symbole|séquence|tableau|texte|ticket|vélo fictif|étoile'.split('|'),
 'Klownkoins|accessories|poster|tree|watering can|cardboard spaceship|scale|paper shield|compass|draft|notebook|pebbles|notepad|map|star chart|cardboard|chairs|song|hat|paper scissors|story|costume|sketch|dictionary|speech|folder|stage scenery|cardboard gear|envelope|invoice|species card|pretend net|paper rocket|gallery|seeds|grid|habitat|pretend ingredients|instrument|invitation|pretend lights|letter|mandate|manuscript|model|menu|message|measurement|measurements|pretend microphone|mirror|model|music|metadata|pretend metal|agenda|bread|palette|basket|paper|sheet music|plush toy|character|photograph|paintbrush|blueprint|cardboard board|schedule|plant|pot|pretend potion|cardboard prototype|lectern|recipe|register|ruler|diagram|stage|seeds|symbol|sequence|board|text|ticket|pretend bicycle|star'.split('|')
))


def translate(text: str, lang: str='fr', **kwargs) -> str:
    """Translate a constant string, optionally applying named interpolation."""
    result=EN.get(text, text) if lang=='en' else text
    return result.format(**kwargs) if kwargs else result


def role_name(role, lang='fr'):
    return ROLE_EN.get(role['id'],role['nom']) if lang=='en' else role['nom']


def detail_name(text, kind, lang='fr'):
    if lang=='fr':return text
    return (ACTION_EN if kind=='action' else OBJECT_EN).get(text,text)


def preset_name(record, kind, lang='fr'):
    if lang=='fr':return record['nom']
    return (PALETTE_EN if kind=='palette' else SKIN_EN).get(record['id'], record['nom'])


def language_file(project:Path) -> Path:
    return Path(project)/'preferences.json'


def get_language(project:Path) -> str:
    try:
        lang=json.loads(language_file(project).read_text(encoding='utf-8')).get('language','fr')
        return lang if lang in LANGUAGES else 'fr'
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):return 'fr'


def set_language(project:Path, lang:str):
    if lang not in LANGUAGES:raise ValueError('Unsupported language: '+str(lang))
    f=language_file(project);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps({'language':lang},ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
