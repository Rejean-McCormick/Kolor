# Kolor Studio — générateur et découpeur des 38 personnages Kontexte

Application de **production pour les adultes**. La version enfant **Kolor** reste séparée.

## Démarrer sur Windows

1. Installer Python 3.11+ pour Windows si nécessaire.
2. Décompresser le dossier (ne pas lancer directement depuis le ZIP).
3. Double-cliquer sur `INSTALLER_ET_LANCER.bat`. Seule bibliothèque nécessaire : **Pillow**.
4. Sélectionner un rôle. Le logo et la couleur de marque `#1E6864` sont conservés.

## Deux façons de créer les planches

**Sans API :** cliquer sur **Copier le prompt du rôle**, le coller dans ChatGPT ou dans son outil d'images, enregistrer le résultat PNG, puis cliquer sur **Importer une planche PNG**. Le bouton **Préparer les 38 prompts** crée les fichiers texte dans `projet/prompts/`.

**Avec l'API OpenAI :** entrer une clé API dans l'application (ou définir `OPENAI_API_KEY`), sélectionner le modèle et la qualité puis **Générer ce rôle** ou **Générer les rôles manquants**. Le modèle par défaut est `gpt-image-2.5-flare`, une option rapide. Générer tous les rôles nécessite jusqu'à **38 appels API facturés séparément** de l'abonnement ChatGPT. L'application demande confirmation avant le lot. Les appels sont séquentiels, résistent à quelques erreurs transitoires et peuvent être interrompus **après la planche en cours**. La clé n'est pas enregistrée dans le projet.

## Ce que produit une génération

- 1 planche **carrée (rapport 1:1)**, à la résolution choisie par l’outil d’image, avec quadrillage virtuel 2×2.
- 4 variantes carrées de **même taille : chaque quart fait 50 % du côté**, sans résolution imposée (principal / bonjour / accessoire / action).
- Une marge blanche d’au moins **6,25 % du côté de chaque quart** est demandée dans le prompt; elle est aussi appliquée proportionnellement lors du recentrage.
- L’import conserve la résolution native d’une planche carrée. Pour un côté impair, 1 pixel blanc est ajouté à droite et en bas; une image rectangulaire est refusée plutôt que déformée.
- Les appels API demandent `size=auto` et un **rapport 1:1 dans le prompt**, sans imposer de nombre de pixels. Comme le format de sortie est décidé par le modèle, vérifier que la planche produite est bien carrée.
- Chaque personnage isolé sur **fond blanc**, contours noirs épais, sans paysage.
- Six **codes techniques** : peau `#FFFF00`, cheveux `#FF0000`, haut `#00FF00`, bas `#0000FF`, chaussures `#FF00FF`, accessoires `#00FFFF`. Le noir et le blanc ne sont pas des couleurs de remplissage.
- Les codes techniques peuvent maintenant être recolorés dans **Kolor Studio**, avec les palettes et les carnations naturelles. Le code de l’autre application Kolor (et ses éventuels réglages HSV) n’a pas été fourni ici.

**Attention :** les modèles d'image ne respectent pas toujours à la lettre les codes HEX, la disposition ou l'uniformité d'un personnage. Après le découpage, vérifier visuellement les quatre poses et contrôler la palette. La détection des teintes approximatives est **indicative**; ce n'est pas une garantie de conformité des pixels. Le programme ne prétend pas générer des images sans accès réseau/API.

## Export pour Kontexte / Ekole

1. Choisir un personnage dans la liste.
2. Cliquer sur une des **4 poses**; la première est recommandée comme pose canonique.
3. Cocher **J'ai vérifié le personnage** après inspection.
4. Cliquer sur **Exporter pour Kolor / Kontexte**.

Le logiciel conserve toujours la planche et les quatre variantes à leur résolution native, mais n’exporte **qu’une image canonique par rôle** :

**Compatibilité :** les sorties Kontexte / Ekole historiques ont encore des dimensions fixes. **Seul cet export final** adapte la pose retenue à 512 × 512 pixels; cela ne contraint pas la génération ou l’import.

- `projet/exports/images/roles/sorciere.png`, `.../fermier.png`, etc. (`512×512`)
- `projet/exports/planches_ekole/roles-01.png` à `roles-05.png` (`2048×1024`) selon les plans historiques présents dans `plans/`
- `projet/exports/manifest.json` avec les identifiants `role-sorciere`, `role-fermier`, etc., et le statut `pret` ou `a_verifier`.

L'export **ne modifie pas** les sources Kontexte ou les anciens manifestes/catalogues. Les zones manquantes dans les planches réassemblées sont laissées blanches. Les champs `a_verifier` doivent être confirmés humainement avant publication. Les 5 plans de `apercus.zip` sont **repris à l'identique**, sans inventer de nouvelles correspondances.

## Dossiers

- `data/roles.json` : 38 rôles provenant de `znapshot_Kontexte_10281944.zip`, actions et objets inclus.
- `plans/roles-01.json` à `roles-05.json` : métadonnées issues de `apercus.zip`.
- `projet/planches/` : toutes les planches sources générées/importées.
- `projet/variantes/` : les 4 variantes de chaque rôle.
- `projet/prompts/` : les prompts prêts à copier.
- `projet/exports/` : images et manifestes pour intégration.

## Pourquoi un rôle par planche ?

Le découpeur historique prévoyait 8 rôles différents sur une planche `4×2`. Pour **mieux conserver l'identité d'un personnage entre plusieurs poses**, Kolor Studio utilise **1 rôle par planche**, en `2×2`. Il recompose ensuite les mêmes planches de 8 rôles attendues par le catalogue historique. Cette méthode exige 38 planches plutôt que 5, mais donne 4 variantes cohérentes du personnage de chaque rôle : la rapidité est une réduction du nombre de générations **par variante** (38 plutôt que 152), non une garantie de temps d'exécution global inférieur à cinq planches.

## Tests

Depuis le dossier extrait :
`py -m unittest discover -s tests -v`

Ces tests emploient uniquement des images factices; ils ne consomment aucun crédit API.

## Traitement d'un dossier entier sans interface graphique

Si des planches ont déjà été téléchargées, nomme-les `sorciere.png`, `fermier.png`, etc., avec les identifiants du dossier `data/roles.json`, puis utilise :

`py Kolor_Studio_CLI.py importer-dossier "C:\mes_planches"`

`py Kolor_Studio_CLI.py exporter`

Le mode CLI ignore les rôles déjà présents (sauf `--ecraser`) et préserve les validations précédentes tant qu'on ne réimporte pas une planche. L'export produit aussi `projet/exports/apercu_roles.jpg`, une planche de contrôle des 38 rôles, avec le statut de validation. 

## Lot intégré — 38 personnages (source.zip)

Cette distribution contient déjà **38 planches PNG importées** depuis les images fournies, en noms d'identifiants standardisés, et **152 poses** découpées automatiquement.

- `projet/planches/<id>.png` : planches carrées originales 1254×1254, classées par rôle ; leur nombre de pixels n'a pas été imposé par les prompts.
- `projet/variantes/<id>/01.png` à `04.png` : quatre poses carrées de 627×627, isolées/recentrées par Kolor Studio.
- `projet/etat.json` : les 38 rôles sont importés, la première pose est sélectionnée par défaut et **aucun rôle n'est marqué comme vérifié**.
- `projet/exports/images/roles/<id>.png` : 38 images individuelles compatibles avec l'ancien catalogue.
- `projet/exports/planches_ekole/roles-01.png` à `roles-05.png` : cinq planches du catalogue historique.
- `projet/exports/manifest.json` : 38 rôles au statut **`a_verifier`**.

**Pour démarrer**, lancer `INSTALLER_ET_LANCER.bat` : les 38 rôles apparaissent déjà dans le logiciel. Cliquer sur chaque rôle pour contrôler l'identité, l'isolation, les accessoires et les couleurs, sélectionner la meilleure pose, cocher **J'ai vérifié le personnage**, puis cliquer **Exporter pour Kolor / Kontexte** pour actualiser les sorties.

Si vous souhaitez installer les fichiers d'origine renommés dans `C:\mycode\Ekole\Kolor\source`, utiliser l'archive distincte `Kolor_source_standardise.zip`. Il est conseillé de sauvegarder l'ancien dossier `source`, puis de **remplacer** son contenu (sans garder les anciens noms accentués à côté des nouveaux noms). Les identifiants exacts sont dans `correspondances_noms.csv`.

**Limite importante :** cette archive intègre les ressources dans **Kolor Studio** et prépare les exports Kolor/Kontexte ; elle ne modifie pas automatiquement le code d'une autre application Kolor installée localement, dont les sources n'ont pas été fournies ici. Les six valeurs HEX doivent être vérifiées avant publication ; un contrôle heuristique n'est pas une garantie de palette exacte.

## Palettes de couleurs et skin tones (version intégrée)

L'application comporte maintenant **13 palettes de couleurs** (y compris le code
technique original) et **12 carnations / skin tones** (y compris le jaune de
repérage), qui peuvent être combinées indépendamment. Les anciens préréglages
évoqués dans le projet précédent **n'étaient pas présents dans cette archive** :
les palettes naturelles ci-incluses sont une base modifiable, et ne sont pas
présentées comme une récupération à l'identique de l'ancien nuancier.

1. Sélectionne un personnage dans la liste.
2. Dans le panneau de droite, section **3. Palettes et skin tones**, choisis la
   palette (cheveux, haut, bas, chaussures, accessoires) et la carnation (peau).
3. L'aperçu central et les quatre vignettes affichent les couleurs choisies.
   La case **Voir les couleurs techniques d’origine** permet de comparer avec la
   source sans modifier ce qui sera exporté.
4. La sélection est sauvegardée **par personnage**, même avant l'import d'une
   planche. Lorsqu'une palette change, la validation de ce personnage est
   réinitialisée pour demander une nouvelle inspection.
5. Clique sur **Exporter pour Kolor / Kontexte** pour produire les PNG recolorisés.

Les couleurs sont définies dans **`data/palettes.json`**, en HEX `#RRGGBB`.
On peut y ajouter des palettes ou skin tones personnalisés en suivant la même
structure (`id` simple, `nom`, couleurs HEX) puis **redémarrer Kolor Studio**.
Le fichier est contrôlé au démarrage. Le bouton d'export joint également un
copie des presets à `projet/exports/palettes.json`.

### Structure des exports après choix d'une palette

- `projet/planches/<id>.png` et `projet/variantes/<id>/01.png` à `04.png` : **sources techniques inchangées**, à leur résolution d'origine.
- `projet/exports/images/roles_natifs/<id>.png` : **pose choisie colorisée** dans sa résolution native.
- `projet/exports/images/roles/<id>.png` : **pose choisie colorisée** en 512 × 512 (contrat existant de l'ancienne application Ekole/Kontexte).
- `projet/exports/images/roles_techniques/<id>.png` : **pose technique d'origine** également au format historique, pour restauration ou comparaison.
- `projet/exports/manifest.json` : les entrées contiennent `palette_id`,
  `skin_tone_id`, `skin_tone_hex`, `couleurs`, `chemin_natif` et
  `chemin_technique`, tout en conservant les anciens champs.
- `projet/exports/palettes.json` : catalogue des palettes et carnations,
  transportable vers une autre application.

**Important :** le recoloriage repose sur les six codes techniques. Si
l'image générée comporte des couleurs parasites ou emploie le même rouge à la
fois pour les cheveux et l'intérieur de la bouche, ces régions peuvent recevoir
la même nouvelle couleur. Les nuances antialiasées sont préservées au mieux,
mais un rendu parfait n'est pas garanti : contrôle visuel requis. Le programme
ne recolore ni les noirs purs ni les blancs purs.

Le projet **Kolor** distinct de **Kolor Studio** n'est pas inclus dans les ZIP
fournis. Les sorties et métadonnées sont donc prêtes à être consommées par
Kolor, mais aucune modification automatique de son code n'est revendiquée.

### Opérations en ligne de commande

Lister les préréglages :

`py Kolor_Studio_CLI.py palettes`

Définir la palette du pêcheur :

`py Kolor_Studio_CLI.py choisir-palette --role pecheur --palette ocean --skin-tone caramel`

Appliquer les couleurs aux exports :

`py Kolor_Studio_CLI.py exporter`

Les nouveaux réglages n'influent jamais sur les **prompts de génération** :
les six codes techniques restent la référence pendant la génération des planches.

## Mise à jour — couleurs variées, skin tones et contours noirs fixes

- **12 palettes multicolores** plus la palette de repérage technique : les cheveux, le haut, le bas, les chaussures et les accessoires ont chacun leur propre couleur. Les 38 rôles intégrés sont initialisés avec des combinaisons variées.
- **12 skin tones** (11 carnations naturelles + jaune technique) : la couleur de la peau se règle **séparément** et ne change jamais les vêtements ou les accessoires.
- **5 teintes indépendantes modifiables** : cliquer sur l'échantillon de couleur d'une catégorie dans le panneau de droite pour choisir son propre HEX via le sélecteur de couleurs. Le changement concerne le rôle courant seulement.
- **Générer une combinaison multicolore** : mélange les couleurs des 5 catégories, sans changer la peau.
- **Revenir aux couleurs de la palette** : efface seulement les ajustements des 5 catégories ; la carnation choisie est conservée.
- **Contours noirs #000000 et fond blanc #FFFFFF verrouillés** : ni les palettes, ni les choix individuels ne peuvent les recolorer. Une couleur individuelle ne peut pas être exactement noir pur ou blanc pur.
- Les paramètres sont enregistrés **pour chaque personnage** dans `projet/etat.json`, avec la clé `couleurs_libres` pour les changements personnels. Dans le manifeste exporté : `couleurs_personnalisees` et `couleurs` (valeurs finales).
- Les images originales dans `projet/planches/` et `projet/variantes/` restent **intactes**. Toutes les recolorations sont créées dans les sorties `projet/exports/`.
- La première utilisation de cette version choisit des palettes multicolores / carnations variées pour les rôles sans réglage préalable. Les personnalisations déjà enregistrées ont priorité : une mise à jour n'efface pas les choix d'un projet existant.

Pour changer une seule région en ligne de commande :

`py Kolor_Studio_CLI.py choisir-couleur --role pecheur --region haut --hex #E97B35`

Pour revenir à la couleur de la palette sur cette région :

`py Kolor_Studio_CLI.py choisir-couleur --role pecheur --region haut --hex RESET`

À noter : ce moteur repose sur six codes de couleur source. Si un générateur mélange accidentellement deux régions sous le même code, elles ne sont pas toujours distinguables automatiquement. Un contrôle visuel des 38 rôles reste nécessaire. Les images générées et la taille des prompts ne sont pas modifiées.
