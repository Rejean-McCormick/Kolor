# Importation des 38 personnages Kolor — effectuée

À partir du dossier d'images `source.zip`, les 38 PNG ont été associés aux 38 identifiants de `data/roles.json`. Les **planches 2 × 2** et leurs **152 poses** sont déjà stockées dans `projet/`. Aucune clé API n'est nécessaire pour les consulter ou exporter.

## Ouvrir et vérifier

1. Dézipper **toute** l'archive Kolor Studio dans un dossier local.
2. Exécuter `INSTALLER_ET_LANCER.bat` sur Windows. Les 38 rôles sont visibles ; les versions existantes ne doivent pas être écrasées par une copie vide du dossier `projet`.
3. Sélectionner chaque rôle et regarder les quatre poses. La première est la pose choisie par défaut, mais **aucune n'a été approuvée humainement**.
4. Cocher « J'ai vérifié le personnage » et réexporter après contrôle.

## Où trouver les résultats

- `projet/planches/` : 38 planches à résolution native, noms standardisés.
- `projet/variantes/` : 152 images, poses `01` = principal, `02` = bonjour, `03` = accessoire, `04` = action.
- `projet/exports/images/roles/` : 38 poses canoniques pour le catalogue historique.
- `projet/exports/planches_ekole/` : 5 planches historiques recomposées.
- `projet/exports/manifest.json` : correspondance entre rôles et chemins d'images.
- `correspondances_noms.csv` : tableau détaillé des noms originaux et nouveaux.

## Copier les sources renommées dans votre projet Kolor

Archive distincte : `Kolor_source_standardise.zip`. Elle contient un dossier `source/` avec 38 PNG aux noms sans accents, conformes aux identifiants du catalogue (ex. `pecheur.png`, `createur-jeux.png`, `origamiste.png`). Après sauvegarde, remplacez le contenu du dossier `C:\mycode\Ekole\Kolor\source` par les 38 fichiers. **L'installation distante sur votre ordinateur n'est pas faite automatiquement depuis cette conversation.**

Les planches originales n'ont subi ni changement de résolution ni recompression lors du renommage ; le dossier normalisé est une copie octet pour octet des sources de départ. Les variantes peuvent être recentrées et l'export ancien catalogue est redimensionné à 512 × 512 pour compatibilité.

## Ajout des palettes / skin tones

13 palettes (12 multicolores + technique), 12 carnations (11 naturelles + technique), sélection et aperçu par rôle. Contours noirs fixes. 5 couleurs indépendantes pour cheveux, haut, bas, chaussures et accessoires, sélectionnées depuis le panneau de droite. PNG techniques non destructifs. Les PNG natifs recolorisés et les exports historiques sont disponibles dans `projet/exports/`. Les couleurs choisies et leurs valeurs HEX sont décrites dans `projet/exports/manifest.json` et `projet/exports/palettes.json`.
