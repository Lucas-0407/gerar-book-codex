import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from . import pdf_generator


class BookApp(tk.Tk):
    """Simple GUI to generate photobook PDFs."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Gerar Book Fotográfico")

        self.folder_var = tk.StringVar()
        self.output_var = tk.StringVar(value="BOOK.pdf")
        self.cols_var = tk.IntVar(value=3)
        self.progress = ttk.Progressbar(self, length=300)

        self._build_widgets()

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Pasta das imagens:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.folder_var, width=40)
        entry.grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Selecionar", command=self.browse_folder).grid(row=0, column=2)

        ttk.Label(frame, text="Colunas por página:").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(frame, from_=2, to=4, textvariable=self.cols_var, width=5).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Arquivo de saída:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.output_var, width=40).grid(row=2, column=1, padx=5)

        ttk.Button(frame, text="Gerar", command=self.start).grid(row=3, column=0, columnspan=3, pady=10)
        self.progress.grid(row=4, column=0, columnspan=3, pady=5)

    def browse_folder(self) -> None:
        folder = filedialog.askdirectory(title="Selecione a pasta com imagens")
        if folder:
            self.folder_var.set(folder)

    def start(self) -> None:
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Erro", "Selecione uma pasta válida")
            return
        output = self.output_var.get()
        columns = self.cols_var.get()
        self.progress["value"] = 0
        threading.Thread(target=self._run_generation, args=(folder, output, columns), daemon=True).start()

    def _run_generation(self, folder: str, output: str, cols: int) -> None:
        def update(curr: int, total: int) -> None:
            self.progress["maximum"] = total
            self.progress["value"] = curr

        try:
            pdf_generator.generate_book(folder, output, columns=cols, add_cover=True, log_file="log.txt", progress_cb=update)
            messagebox.showinfo("Concluído", f"PDF salvo em {output}")
        except Exception as exc:  # pragma: no cover - GUI message only
            messagebox.showerror("Erro", str(exc))


def main() -> None:
    app = BookApp()
    app.mainloop()


if __name__ == "__main__":
    main()

