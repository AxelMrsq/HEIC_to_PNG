import os
import sys

# --- Configuration pour ImageMagick (DLLs embarquées) ---
if getattr(sys, 'frozen', False):
    # Si le script est exécuté depuis un .exe (PyInstaller)
    application_path = os.path.dirname(sys.executable)
    # Chemin vers le dossier temporaire où PyInstaller extrait les DLLs
    imagemagick_path = application_path  # Les DLLs sont extraites dans le même dossier que le .exe
    os.environ['PATH'] = imagemagick_path + os.pathsep + os.environ['PATH']
    os.environ['MAGICK_HOME'] = imagemagick_path  # Crucial pour wand !
else:
    # Pour le développement (pas nécessaire pour le .exe)
    imagemagick_path = os.path.join(os.path.dirname(__file__), 'imagemagick')
    if os.path.exists(imagemagick_path):
        os.environ['PATH'] = imagemagick_path + os.pathsep + os.environ['PATH']
        os.environ['MAGICK_HOME'] = imagemagick_path

# --- Imports après la configuration ---
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from wand.image import Image

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from wand.image import Image
import os

def convert_heic_to_png(heic_path, png_path):
    """Convertit un fichier HEIC en PNG avec wand (ImageMagick)."""
    try:
        with Image(filename=heic_path) as img:
            img.format = 'png'
            img.save(filename=png_path)
        return True
    except Exception as e:
        print(f"Erreur lors de la conversion de {heic_path} : {e}")
        return False

def select_files():
    """Ouvre une boîte de dialogue pour sélectionner des fichiers HEIC."""
    file_paths = filedialog.askopenfilenames(
        title="Sélectionner des fichiers HEIC",
        filetypes=[("Fichiers HEIC", "*.heic *.HEIC")]
    )
    if file_paths:
        entry_files.delete(0, tk.END)
        entry_files.insert(0, ", ".join(file_paths))

def select_output_folder():
    """Ouvre une boîte de dialogue pour sélectionner un dossier de sortie."""
    folder_path = filedialog.askdirectory(title="Sélectionner un dossier de sortie")
    if folder_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, folder_path)

def update_progress(current, total):
    """Met à jour la barre de progression et le label de statut."""
    progress_var.set(f"Conversion en cours... ({current}/{total})")
    progress_bar['value'] = (current / total) * 100
    root.update_idletasks()  # Met à jour l'interface immédiatement

def convert_files():
    """Convertit les fichiers sélectionnés en PNG avec barre de progression."""
    heic_files = entry_files.get().split(", ")
    output_folder = entry_output.get()

    if not heic_files or not output_folder:
        messagebox.showerror("Erreur", "Veuillez sélectionner des fichiers HEIC et un dossier de sortie.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Réinitialiser la barre de progression
    progress_bar['value'] = 0
    progress_var.set("Préparation...")

    success_count = 0
    total_files = len([f for f in heic_files if f.strip()])

    for i, heic_path in enumerate(heic_files):
        heic_path = heic_path.strip()
        if not heic_path:
            continue

        # Créer le nom du fichier PNG
        filename = os.path.basename(heic_path)
        png_filename = os.path.splitext(filename)[0] + ".png"
        png_path = os.path.join(output_folder, png_filename)

        # Mettre à jour la barre de progression
        update_progress(i + 1, total_files)

        # Convertir le fichier
        if convert_heic_to_png(heic_path, png_path):
            success_count += 1

    # Réinitialiser la barre de progression à la fin
    progress_bar['value'] = 100
    progress_var.set(f"Conversion terminée ! {success_count}/{total_files} fichiers convertis.")

    messagebox.showinfo(
        "Conversion terminée",
        f"{success_count} fichier(s) converti(s) avec succès dans {output_folder} !"
    )

import os
import sys

# Ajouter le dossier imagemagick/ au PATH pour que wand trouve les DLLs
if getattr(sys, 'frozen', False):
    # Si le script est exécuté depuis un .exe (PyInstaller)
    application_path = os.path.dirname(sys.executable)
    imagemagick_path = os.path.join(application_path, 'imagemagick')
    os.environ['PATH'] = imagemagick_path + os.pathsep + os.environ['PATH']
else:
    # Si le script est exécuté normalement (pour le développement)
    imagemagick_path = os.path.join(os.path.dirname(__file__), 'imagemagick')
    os.environ['PATH'] = imagemagick_path + os.pathsep + os.environ['PATH']

# --- Interface Tkinter ---
root = tk.Tk()
root.title("Convertisseur HEIC vers PNG")
root.geometry("500x350")  # Augmenter la hauteur pour la barre de progression

# Frame pour les fichiers HEIC
frame_files = tk.Frame(root)
frame_files.pack(pady=10)

label_files = tk.Label(frame_files, text="Fichiers HEIC :")
label_files.pack(side=tk.LEFT)

entry_files = tk.Entry(frame_files, width=40)
entry_files.pack(side=tk.LEFT, padx=5)

button_browse_files = tk.Button(frame_files, text="Parcourir", command=select_files)
button_browse_files.pack(side=tk.LEFT)

# Frame pour le dossier de sortie
frame_output = tk.Frame(root)
frame_output.pack(pady=10)

label_output = tk.Label(frame_output, text="Dossier de sortie :")
label_output.pack(side=tk.LEFT)

entry_output = tk.Entry(frame_output, width=40)
entry_output.pack(side=tk.LEFT, padx=5)

button_browse_output = tk.Button(frame_output, text="Parcourir", command=select_output_folder)
button_browse_output.pack(side=tk.LEFT)

# Bouton de conversion
button_convert = tk.Button(root, text="Convertir en PNG", command=convert_files)
button_convert.pack(pady=10)

# Barre de progression
frame_progress = tk.Frame(root)
frame_progress.pack(pady=10, padx=20, fill=tk.X)

progress_var = tk.StringVar()
progress_var.set("Prêt")
label_progress = tk.Label(frame_progress, textvariable=progress_var)
label_progress.pack()

progress_bar = ttk.Progressbar(
    frame_progress,
    orient=tk.HORIZONTAL,
    length=400,
    mode='determinate'
)
progress_bar.pack()

# Lancer l'interface
root.mainloop()