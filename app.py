import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from converter import ConversionResult, convert_folder


class ConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HEIC vers PNG")
        self.root.geometry("500x205")
        self.root.resizable(False, False)

        self.folder = tk.StringVar()
        self.status = tk.StringVar(value="Choisissez un dossier pour commencer.")
        self.events: queue.Queue = queue.Queue()
        self.convert_button: ttk.Button

        main = ttk.Frame(root, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Dossier contenant les photos HEIC").pack(anchor="w")

        folder_row = ttk.Frame(main)
        folder_row.pack(fill="x", pady=(6, 12))
        ttk.Entry(folder_row, textvariable=self.folder, state="readonly").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(folder_row, text="Parcourir...", command=self.choose_folder).pack(
            side="left", padx=(8, 0)
        )

        self.convert_button = ttk.Button(
            main, text="Convertir en PNG", command=self.start_conversion
        )
        self.convert_button.pack(anchor="w")

        ttk.Label(
            main, text="Les fichiers PNG seront placés dans un sous-dossier « PNG »."
        ).pack(anchor="w", pady=(12, 4))
        ttk.Label(main, textvariable=self.status, wraplength=465).pack(anchor="w")

        self.root.after(100, self.check_events)

    def choose_folder(self) -> None:
        initial_folder = self.folder.get()
        selected = filedialog.askdirectory(
            title="Choisir le dossier des photos",
            initialdir=initial_folder if Path(initial_folder).is_dir() else None,
        )
        if selected:
            self.folder.set(selected)
            self.status.set("Dossier sélectionné. Prêt à convertir.")

    def start_conversion(self) -> None:
        source = Path(self.folder.get())
        if not source.is_dir():
            messagebox.showerror("Dossier invalide", "Choisissez un dossier valide.")
            return

        self.convert_button.configure(state="disabled")
        self.status.set("Conversion en cours...")
        threading.Thread(
            target=self.convert_in_background,
            args=(source,),
            daemon=True,
        ).start()

    def convert_in_background(self, source: Path) -> None:
        try:
            result = convert_folder(
                source,
                source / "PNG",
                lambda completed, total, current: self.events.put(
                    ("progress", completed, total, current.name)
                ),
            )
            self.events.put(("complete", result))
        except Exception as error:
            self.events.put(("error", str(error)))

    def check_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "progress":
                    _, completed, total, name = event
                    self.status.set(f"Conversion : {completed}/{total} — {name}")
                elif event[0] == "complete":
                    self.show_result(event[1])
                else:
                    self.convert_button.configure(state="normal")
                    self.status.set("La conversion n'a pas pu démarrer.")
                    messagebox.showerror("Erreur", event[1])
        except queue.Empty:
            pass
        self.root.after(100, self.check_events)

    def show_result(self, result: ConversionResult) -> None:
        self.convert_button.configure(state="normal")
        if result.total == 0:
            self.status.set("Aucun fichier .heic trouvé dans ce dossier.")
            return

        self.status.set(
            f"Terminé : {result.converted}/{result.total} photo(s) convertie(s). "
            f"Résultats : {self.folder.get()}\\PNG"
        )
        if result.errors:
            details = "\n".join(
                f"{path.name} : {error}" for path, error in result.errors[:5]
            )
            if len(result.errors) > 5:
                details += f"\n... et {len(result.errors) - 5} autre(s) erreur(s)."
            messagebox.showwarning(
                "Conversion incomplète",
                f"{len(result.errors)} fichier(s) n'ont pas pu être convertis :\n\n"
                f"{details}",
            )


def main() -> None:
    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
