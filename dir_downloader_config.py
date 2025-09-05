# db_downloader_with_config.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import threading
import yaml

class MicrobiomeDBDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Bases de Datos - microbiome-pipeline")
        self.root.geometry("800x650")
        self.root.resizable(True, True)

        # Variables para rutas (sin trimmomatic ni kraken2)
        self.kneaddata_db_dir = tk.StringVar(value="/media/rodrigo/Data1/Microbiome/Recursos/DB/metagenomic/Kneaddata/hg37")
        self.metaphlan_db_dir = tk.StringVar(value="/media/rodrigo/Data1/TESIS/MP_dbs/metaphlan_databases_vJun23")
        self.chocophlan_dir = tk.StringVar(value="/media/rodrigo/Data1/TESIS/MP_dbs/chocophlan")
        self.uniref_dir = tk.StringVar(value="/media/rodrigo/Data1/Microbiome/Recursos/DB/metagenomic/Humann_databases/uniref")
        self.utility_mapping_dir = tk.StringVar(value="/media/rodrigo/Data1/Microbiome/Recursos/DB/metagenomic/Humann_databases/utility_mapping")
        self.samples_dir = tk.StringVar(value="/home/rodrigo/Desktop/sample_test")

        # Ruta de salida del config.yaml
        self.config_output = tk.StringVar(value=os.path.expanduser("~/microbiome-pipeline/config.yaml"))

        self.create_widgets()

    def create_widgets(self):
        # --- Título ---
        tk.Label(
            self.root,
            text="Descargador de Bases de Datos\nmicrobiome-pipeline",
            font=("Arial", 16, "bold"),
            fg="darkblue"
        ).pack(pady=10)

        # --- Sección: KneadData ---
        self.create_download_section(
            "KneadData - Genoma humano (hg37)",
            self.kneaddata_db_dir,
            "kneaddata_database --download human_genome bowtie2"
        )

        # --- Sección: MetaPhlAn ---
        self.create_download_section(
            "MetaPhlAn - mpa_vJun23_CHOCOPhlAnSGB_202307",
            self.metaphlan_db_dir,
            "metaphlan --install --index mpa_vJun23_CHOCOPhlAnSGB_202307 --db_dir"
        )

        # --- Sección: HUMAnN - ChocoPhlAn ---
        self.create_download_section(
            "HUMAnN - ChocoPhlAn (nucleótidos)",
            self.chocophlan_dir,
            "humann_databases --download chocophlan full"
        )

        # --- Sección: HUMAnN - UniRef ---
        self.create_download_section(
            "HUMAnN - UniRef90 (proteínas)",
            self.uniref_dir,
            "humann_databases --download uniref uniref90_diamond"
        )

        # --- Sección: HUMAnN - Utility Mapping ---
        self.create_download_section(
            "HUMAnN - utility_mapping (para regroup: KO, GO, EC, etc.)",
            self.utility_mapping_dir,
            "humann_databases --download utility_mapping full"
        )

        # --- Sección: Directorio de muestras ---
        self.create_path_section("Directorio de muestras (para config.yaml)", self.samples_dir)

        # --- Ruta de salida del config.yaml ---
        self.create_path_section("Guardar config.yaml en direcrotio raiz", self.config_output)

        # --- Botón: Descargar TODAS y generar config ---
        tk.Button(
            self.root,
            text="🚀 Descargar TODAS y generar config.yaml",
            command=self.download_all_and_generate_config,
            bg="green",
            fg="white",
            font=("Arial", 11, "bold"),
            height=2
        ).pack(pady=15)

        # --- Consola de salida ---
        tk.Label(self.root, text="Salida del proceso:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)
        self.log_text = scrolledtext.ScrolledText(self.root, height=12, state="normal", font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, padx=20, pady=10, expand=True)

        # --- Pie de página ---
        tk.Label(self.root, text="Rodrigo Peralta - UNER | microbiome-pipeline", fg="gray").pack(side="bottom")

    def create_path_section(self, title, var):
        frame = tk.Frame(self.root)
        frame.pack(pady=5, fill=tk.X, padx=20)

        tk.Label(frame, text=title, font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))

        tk.Label(frame, text="Ruta:").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=var, width=50).grid(row=1, column=1, padx=5)
        tk.Button(frame, text="Seleccionar", command=lambda: self.select_dir(var)).grid(row=1, column=2)

    def create_download_section(self, title, var, command_prefix):
        frame = tk.Frame(self.root)
        frame.pack(pady=5, fill=tk.X, padx=20)

        tk.Label(frame, text=title, font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))

        tk.Label(frame, text="Ruta:").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=var, width=50).grid(row=1, column=1, padx=5)
        tk.Button(frame, text="Seleccionar", command=lambda: self.select_dir(var)).grid(row=1, column=2)
        tk.Button(
            frame,
            text="Descargar",
            command=lambda: self.start_download(command_prefix, var.get()),
            bg="blue",
            fg="white"
        ).grid(row=1, column=3, padx=10)

    def select_dir(self, var):
        folder = filedialog.askdirectory(initialdir=var.get())
        if folder:
            var.set(folder)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def start_download(self, command_prefix, db_dir):
        if not db_dir:
            messagebox.showerror("Error", "Por favor, define una ruta válida.")
            return

        os.makedirs(db_dir, exist_ok=True)
        self.log(f"[{command_prefix.split()[0]}] Ruta: {db_dir}")

        # Usar conda run para evitar problemas de activación
        full_command = f"conda run -n microbiome-pipeline {command_prefix} {db_dir}"

        def run():
            try:
                self.log(f"🔧 Ejecutando: {full_command}")
                result = subprocess.run(
                    full_command,
                    shell=True,
                    executable="/bin/bash",
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log("✅ Descarga completada.\n")
                else:
                    self.log("❌ Error:")
                    self.log(result.stderr)
            except Exception as e:
                self.log(f"❌ Excepción: {e}")

        thread = threading.Thread(target=run)
        thread.start()

    def download_all_and_generate_config(self):
        """Descargar todas las bases de datos y generar config.yaml"""
        downloads = [
            ("kneaddata_database --download human_genome bowtie2", self.kneaddata_db_dir.get()),
            ("metaphlan --install --index mpa_vJun23_CHOCOPhlAnSGB_202307 --db_dir", self.metaphlan_db_dir.get()),
            ("humann_databases --download chocophlan full", self.chocophlan_dir.get()),
            ("humann_databases --download uniref uniref90_diamond", self.uniref_dir.get()),
            ("humann_databases --download utility_mapping full", self.utility_mapping_dir.get()),
        ]

        def run_all():
            for cmd_prefix, db_dir in downloads:
                if not db_dir:
                    self.log(f"❌ Ruta no definida para: {cmd_prefix}")
                    continue
                os.makedirs(db_dir, exist_ok=True)
                self.log(f"[{cmd_prefix.split()[0]}] Iniciando descarga en: {db_dir}")
                full_command = f"conda run -n microbiome-pipeline {cmd_prefix} {db_dir}"
                self.log(f"🔧 {full_command}")
                result = subprocess.run(
                    full_command,
                    shell=True,
                    executable="/bin/bash",
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log("✅ Completado.\n")
                else:
                    self.log("❌ Error:")
                    self.log(result.stderr)

            # Generar config.yaml al final
            self.generate_config_yaml()

        thread = threading.Thread(target=run_all)
        thread.start()

    def generate_config_yaml(self):
        """Genera el config.yaml con la estructura exacta"""
        config = {
            "paths": {
                "kneaddata_db": self.kneaddata_db_dir.get(),
                "metaphlan_db": self.metaphlan_db_dir.get(),
                "humann_nucleotide_db": self.chocophlan_dir.get(),
                "humann_protein_db": self.uniref_dir.get(),
                "humann_go_db": os.path.join(self.utility_mapping_dir.get(), "utility_mapping", "map_go_uniref90.txt.gz"),
                "humann_ko_db": os.path.join(self.utility_mapping_dir.get(), "utility_mapping", "map_ko_uniref90.txt.gz"),
                "humann_ec_db": os.path.join(self.utility_mapping_dir.get(), "utility_mapping", "map_level4ec_uniref90.txt.gz"),
                "humann_pfam_db": os.path.join(self.utility_mapping_dir.get(), "utility_mapping", "map_pfam_uniref90.txt.gz"),
                "humann_eggnog_db": os.path.join(self.utility_mapping_dir.get(), "utility_mapping", "map_eggnog_uniref90.txt.gz"),
            },
            "tools": {
                "threads": 8,
                "kneaddata_env": "microbiome-pipeline",
                "metaphlan_env": "microbiome-pipeline",
                "humann3_env": "microbiome-pipeline",
            },
            "samples_dir": self.samples_dir.get(),
        }

        config_path = self.config_output.get()
        try:
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
            self.log(f"✅ Archivo de configuración generado: {config_path}")
            messagebox.showinfo("Éxito", f"¡Todo completado!\nConfig guardado en:\n{config_path}")
        except Exception as e:
            self.log(f"❌ Error al guardar config.yaml: {e}")
            messagebox.showerror("Error", f"No se pudo guardar el archivo de configuración:\n{e}")

# --- Iniciar GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MicrobiomeDBDownloader(root)
    root.mainloop()