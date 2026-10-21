# HEIC vers PNG

Application Windows simple pour convertir localement des photos `.heic` en `.png`.
Aucun fichier n'est envoyé sur Internet. Les photos PNG sont enregistrées dans un
sous-dossier `PNG`, en conservant les sous-dossiers et les noms des photos.

## Utiliser l'application

Lancez `HEICtoPNG.exe`, choisissez le dossier contenant les photos, puis cliquez
sur **Convertir en PNG**. Vous pouvez copier le fichier `HEICtoPNG.exe` généré
sur une clef USB et le lancer sur un ordinateur Windows compatible, sans y
installer Python.

## Créer le fichier `.exe`

Sur un ordinateur Windows avec Python 3 et `pip` installés :

1. Ouvrez ce dossier dans l'Explorateur de fichiers.
2. Double-cliquez sur `build.bat` et attendez la fin de la compilation.
3. Récupérez `dist\HEICtoPNG.exe`.

La compilation télécharge les dépendances Python si elles ne sont pas déjà
installées. Une fois l'exécutable créé, la conversion elle-même fonctionne
hors ligne.
