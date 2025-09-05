# gui_launcher.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import shlex
from pathlib import Path

class MicrobiomePipelineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("microbiome-pipeline GUI")
        self.root.geometry("700x550")
        self.root.resizable(True, True)

        # 🔧 Directorio raíz del proyecto
        self.project_dir = Path(__file__).parent.parent.resolve()
        self.config_path = self.project_dir / "config.yaml"

        # ✅ Verificar que config.yaml exista
        if not self.config_path.exists():
            messagebox.showerror(
                "Error",
                f"No se encontró config.yaml en:\n{self.config_path}\n"
                "Asegúrate de que el archivo exista en la raíz del proyecto."
            )
            self.root.destroy()
            return

        self.sample_dir = tk.StringVar()
        self.samples_dir = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # --- Título ---
        tk.Label(
            self.root,
            text="microbiome-pipeline\nGUI para análisis de microbioma",
            font=("Arial", 16, "bold"),
            fg="darkblue"
        ).pack(pady=10)

        # --- Sección: Muestra individual ---
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=10, fill=tk.X, padx=20)

        tk.Label(frame1, text="Muestra individual:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        tk.Entry(frame1, textvariable=self.sample_dir, width=40).grid(row=0, column=1, padx=5)
        tk.Button(frame1, text="Seleccionar", command=self.select_sample).grid(row=0, column=2)

        # --- Botones: qc, taxonomy, pathways ---
        btn_frame1 = tk.Frame(self.root)
        btn_frame1.pack(pady=10)

        tk.Button(
            btn_frame1, text="🔍 QC", command=self.run_qc,
            bg="#4285F4", fg="white", width=10, height=2
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame1, text="🧬 Taxonomía", command=self.run_taxonomy,
            bg="#34A853", fg="white", width=10, height=2
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame1, text="🧪 Vías", command=self.run_pathways,
            bg="#FBBC05", fg="black", width=10, height=2
        ).pack(side=tk.LEFT, padx=5)

        # --- Sección: Directorio de múltiples muestras (run-all) ---
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=15, fill=tk.X, padx=20)

        tk.Label(frame2, text="Carpeta de muestras (run-all):", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        tk.Entry(frame2, textvariable=self.samples_dir, width=40).grid(row=0, column=1, padx=5)
        tk.Button(frame2, text="Seleccionar", command=self.select_samples_dir).grid(row=0, column=2)

        # --- Botón: run-all ---
        tk.Button(
            self.root,
            text="🚀 Ejecutar Todo (run-all)",
            command=self.run_all,
            bg="#EA4335", fg="white", font=("Arial", 10, "bold"), width=20, height=2
        ).pack(pady=10)

        # --- Consola de salida ---
        tk.Label(self.root, text="Salida del pipeline:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)
        self.log_text = scrolledtext.ScrolledText(self.root, height=12, state="normal", font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)

        # --- Pie de página ---
        tk.Label(self.root, text=f"Rodrigo Peralta - UNER | {self.project_dir}", fg="gray").pack(side="bottom")

    def select_sample(self):
        folder = filedialog.askdirectory()
        if folder:
            self.sample_dir.set(folder)

    def select_samples_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.samples_dir.set(folder)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def run_command(self, command):
        """Ejecuta el comando en el directorio del proyecto"""
        self.log(f"🔧 Ejecutando en {self.project_dir}:")
        self.log(f"   {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_dir,  # ✅ Ejecuta en la raíz del proyecto
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                self.log("✅ Comando ejecutado con éxito.")
                self.log(result.stdout)
            else:
                self.log("❌ Error:")
                self.log(result.stderr)
        except Exception as e:
            self.log(f"❌ Excepción: {e}")

    def run_qc(self):
        sample = self.sample_dir.get()
        if not sample:
            messagebox.showerror("Error", "Selecciona una carpeta de muestra")
            return
        cmd = f"microbiome-cli qc {shlex.quote(sample)}"
        self.run_command(cmd)

    def run_taxonomy(self):
        sample = self.sample_dir.get()
        if not sample:
            messagebox.showerror("Error", "Selecciona una carpeta de muestra")
            return
        cmd = f"microbiome-cli taxonomy {shlex.quote(sample)}"
        self.run_command(cmd)

    def run_pathways(self):
        sample = self.sample_dir.get()
        if not sample:
            messagebox.showerror("Error", "Selecciona una carpeta de muestra")
            return
        cmd = f"microbiome-cli pathways {shlex.quote(sample)}"
        self.run_command(cmd)

    def run_all(self):
        samples_dir = self.samples_dir.get()
        if not samples_dir:
            messagebox.showerror("Error", "Selecciona una carpeta de muestras")
            return
        cmd = f"microbiome-cli run-all {shlex.quote(samples_dir)}"
        self.run_command(cmd)


# --- Iniciar GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MicrobiomePipelineGUI(root)
    root.mainloop()