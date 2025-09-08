# app.py
import streamlit as st
import subprocess
import os
from pathlib import Path
import yaml
import signal
import psutil
import time

# --- Configuración ---
PROJECT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = PROJECT_DIR / "config.yaml"

# --- Configuración de la página ---
st.set_page_config(
    page_title="microbiome-pipeline",
    page_icon="🧫",
    layout="centered"
)

# --- Título estilizado ---
st.markdown(
    """
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #f5f7fa, #c3cfe2); border-radius: 10px; border: 1px solid #d0d8e8; margin-bottom: 1.5rem;">
        <h1 style="color: #2c3e50; margin: 0; font-size: 2.5rem; font-weight: bold;">
            🧫 microbiome-pipeline
        </h1>
        <p style="color: #34495e; font-size: 1.1rem; margin: 0.5rem 0;">
            <em>GUI para análisis de microbioma: QC, taxonomía y rutas metabólicas</em>
        </p>
        <hr style="border: 1px solid #bdc3c7; width: 80%; margin: 1rem auto;">
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Estado para logs y procesos ---
if "logs" not in st.session_state:
    st.session_state.logs = []

# Inicializar rutas y procesos
db_keys = ["kneaddata_dir", "metaphlan_dir", "chocophlan_dir", "uniref_dir", "utility_dir", "samples_dir"]
for key in db_keys:
    if key not in st.session_state:
        if key == "samples_dir":
            st.session_state[key] = "/home/User/sample_test"
        else:
            st.session_state[key] = f"/media/User/DBs/metagenomic/{key.split('_')[0].capitalize()}"

# Para cada base de datos, almacenamos su proceso
for db in ["kneaddata", "metaphlan", "chocophlan", "uniref", "utility"]:
    if f"{db}_process" not in st.session_state:
        st.session_state[f"{db}_process"] = None
    if f"{db}_running" not in st.session_state:
        st.session_state[f"{db}_running"] = False


def log(message):
    st.session_state.logs.append(message)


def run_command(command, db_name, cwd=None):
    """Ejecuta un comando en segundo plano y permite su cancelación"""
    if st.session_state.get(f"{db_name}_running", False):
        st.warning(f"Ya hay una descarga en curso para {db_name}.")
        return

    st.session_state.logs = []
    log(f"🔧 Iniciando: {command}")
    st.session_state[f"{db_name}_running"] = True

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd or PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            preexec_fn=os.setsid
        )
        st.session_state[f"{db_name}_process"] = process

        while st.session_state[f"{db_name}_running"] and process.poll() is None:
            output = process.stdout.readline()
            if output:
                log(output.strip())
                st.rerun()
            time.sleep(0.1)

        stdout, stderr = process.communicate(timeout=5)
        if stdout:
            for line in stdout.splitlines():
                log(line)
        if stderr:
            for line in stderr.splitlines():
                log(f"❌ {line}")

        if process.returncode == 0:
            log(f"✅ {db_name} descargado con éxito.")
        else:
            if st.session_state[f"{db_name}_running"]:
                log(f"❌ Error en {db_name}: código {process.returncode}")

    except Exception as e:
        log(f"❌ Excepción: {e}")
    finally:
        st.session_state[f"{db_name}_process"] = None
        st.session_state[f"{db_name}_running"] = False


def cancel_download(db_name):
    """Cancela la descarga de una base de datos"""
    proc_key = f"{db_name}_process"
    running_key = f"{db_name}_running"
    if st.session_state.get(proc_key):
        try:
            parent = psutil.Process(st.session_state[proc_key].pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            log(f"🛑 Descarga de {db_name} cancelada.")
        except psutil.NoSuchProcess:
            log(f"🛑 Proceso de {db_name} ya finalizado.")
        except Exception as e:
            log(f"❌ Error al cancelar {db_name}: {e}")
        finally:
            st.session_state[proc_key] = None
            st.session_state[running_key] = False
    else:
        log(f"🛑 No hay descarga activa para {db_name}.")


def select_folder_ui(label, session_key, default_value=""):
    """Interfaz para seleccionar carpeta"""
    st.write(f"**{label}:**")
    col1, col2 = st.columns([3, 1])
    with col1:
        current = st.text_input("Ruta", st.session_state.get(session_key, default_value), key=f"input_{session_key}")
        st.session_state[session_key] = current
    with col2:
        if st.button("📁 Elegir", key=f"btn_{session_key}"):
            st.session_state[f"selecting_{session_key}"] = True

    if st.session_state.get(f"selecting_{session_key}", False):
        st.info("Abre una terminal y escribe:")
        st.code(f"xdg-open {Path.home()}", language="bash")
        st.write("Selecciona una carpeta y pégala arriba.")
        if st.button("✅ Hecho", key=f"done_{session_key}"):
            st.session_state[f"selecting_{session_key}"] = False
            st.rerun()


# --- Pestañas ---
tab1, tab2 = st.tabs(["📦 Descargar Bases de Datos", "▶️ Ejecutar Pipeline"])

# --- Tab 1: Descargar Bases de Datos ---
with tab1:
    select_folder_ui("KneadData - Genoma humano (hg37)", "kneaddata_dir", "/media/User/DBs/Kneaddata/hg37")
    select_folder_ui("MetaPhlAn", "metaphlan_dir", "/media/User/DBs/metaphlan_databases_vJun23")
    select_folder_ui("HUMAnN - ChocoPhlAn", "chocophlan_dir", "/media/User/DBs/Humann_databases/chocophlan")
    select_folder_ui("HUMAnN - UniRef90", "uniref_dir", "/media/User/DBs/Humann_databases/uniref")
    select_folder_ui("HUMAnN - Utility Mapping", "utility_dir", "/media/User/DBs/Humann_databases/utility_mapping")

    st.markdown("---")

    st.subheader("Descarga individual")

    dbs = [
        ("kneaddata", "KneadData", st.session_state.kneaddata_dir, "kneaddata_database --download human_genome bowtie2"),
        ("metaphlan", "MetaPhlAn", st.session_state.metaphlan_dir, "metaphlan --install --index mpa_vJun23_CHOCOPhlAnSGB_202307 --db_dir"),
        ("chocophlan", "ChocoPhlAn", st.session_state.chocophlan_dir, "humann_databases --download chocophlan full"),
        ("uniref", "UniRef90", st.session_state.uniref_dir, "humann_databases --download uniref uniref90_diamond"),
        ("utility", "Utility Mapping", st.session_state.utility_dir, "humann_databases --download utility_mapping full"),
    ]

    for db_key, db_label, db_dir, cmd_part in dbs:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{db_label}**")
        with col2:
            if st.button("⬇️ Descargar", key=f"btn_{db_key}", use_container_width=True):
                os.makedirs(db_dir, exist_ok=True)
                cmd = f"conda run -n microbiome-pipeline {cmd_part} {db_dir}"
                run_command(cmd, db_key)
        with col3:
            if st.session_state.get(f"{db_key}_running", False):
                if st.button("🛑", key=f"cancel_{db_key}", use_container_width=True):
                    cancel_download(db_key)
            else:
                st.button("🛑", disabled=True, key=f"cancel_{db_key}_disabled", use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Generar config.yaml", type="secondary"):
            st.session_state.logs = []
            log("🔧 Generando config.yaml...")

            config_data = {
                "paths": {
                    "kneaddata_db": str(Path(st.session_state.kneaddata_dir).resolve()),
                    "metaphlan_db": str(Path(st.session_state.metaphlan_dir).resolve()),
                    "humann_nucleotide_db": str(Path(st.session_state.chocophlan_dir).resolve()),
                    "humann_protein_db": str(Path(st.session_state.uniref_dir).resolve()),
                    "humann_go_db": str(Path(st.session_state.utility_dir) / "utility_mapping" / "map_go_uniref90.txt.gz"),
                    "humann_ko_db": str(Path(st.session_state.utility_dir) / "utility_mapping" / "map_ko_uniref90.txt.gz"),
                    "humann_ec_db": str(Path(st.session_state.utility_dir) / "utility_mapping" / "map_level4ec_uniref90.txt.gz"),
                    "humann_pfam_db": str(Path(st.session_state.utility_dir) / "utility_mapping" / "map_pfam_uniref90.txt.gz"),
                    "humann_eggnog_db": str(Path(st.session_state.utility_dir) / "utility_mapping" / "map_eggnog_uniref90.txt.gz"),
                },
                "tools": {
                    "threads": 8,
                    "kneaddata_env": "microbiome-pipeline",
                    "metaphlan_env": "microbiome-pipeline",
                    "humann3_env": "microbiome-pipeline",
                },
                "samples_dir": str(Path(st.session_state.samples_dir).resolve()),
            }

            try:
                with open(CONFIG_PATH, 'w') as f:
                    yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, indent=2)
                log(f"✅ Archivo generado: {CONFIG_PATH}")
                st.success(f"✅ config.yaml generado exitosamente en:\n`{CONFIG_PATH}`")
            except Exception as e:
                log(f"❌ Error al guardar config.yaml: {e}")
                st.error(f"No se pudo guardar el archivo: {e}")

    with col2:
        if st.button("🚀 Descargar TODAS", type="primary", use_container_width=True):
            st.session_state.logs = []
            log("🔧 Iniciando descarga de todas las bases de datos...")

            for db_key, db_label, db_dir, cmd_part in dbs:
                if st.session_state.get(f"{db_key}_running", False):
                    log(f"⚠️ {db_label} ya está descargándose. Omitiendo.")
                    continue
                log(f"⬇️ {db_label}: {db_dir}")
                os.makedirs(db_dir, exist_ok=True)
                cmd = f"conda run -n microbiome-pipeline {cmd_part} {db_dir}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    log(f"✅ {db_label} descargado.")
                else:
                    log(f"❌ Error en {db_label}: {result.stderr}")

            st.success("✅ Todas las descargas completadas (ver log para detalles)")

# --- Tab 2: Ejecutar Pipeline ---
with tab2:
    st.header("Ejecutar Pipeline")
    select_folder_ui("Carpeta de muestra(s)", "samples_dir", "/home/rodrigo/Desktop/sample_test")

    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🔍 QC", use_container_width=True):
            sample_dir = st.session_state.samples_dir
            if not sample_dir or not os.path.exists(sample_dir):
                st.error("Carpeta inválida")
            else:
                cmd = f"microbiome-cli qc {sample_dir}"
                run_command(cmd, "pipeline")

    with col2:
        if st.button("🧬 Taxonomía", use_container_width=True):
            sample_dir = st.session_state.samples_dir
            if not sample_dir or not os.path.exists(sample_dir):
                st.error("Carpeta inválida")
            else:
                cmd = f"microbiome-cli taxonomy {sample_dir}"
                run_command(cmd, "pipeline")

    with col3:
        if st.button("🧪 Rutas Metabolicas", use_container_width=True):
            sample_dir = st.session_state.samples_dir
            if not sample_dir or not os.path.exists(sample_dir):
                st.error("Carpeta inválida")
            else:
                cmd = f"microbiome-cli pathways {sample_dir}"
                run_command(cmd, "pipeline")

    with col4:
        if st.button("🚀 Todo", type="primary", use_container_width=True):
            sample_dir = st.session_state.samples_dir
            if not sample_dir or not os.path.exists(sample_dir):
                st.error("Carpeta inválida")
            else:
                cmd = f"microbiome-cli run-all {sample_dir}"
                run_command(cmd, "pipeline")

    with col5:
        if st.button("🛑 Cancelar", type="secondary", use_container_width=True):
            cancel_download("pipeline")

# --- Mostrar logs ---
st.markdown("### 📝 Log de salida")
log_output = st.empty()
if st.session_state.logs:
    log_text = "\n".join(st.session_state.logs)
    log_output.text_area("", value=log_text, height=300)

# --- Pie de página ---
st.markdown("---")
st.caption("Rodrigo Peralta - UNER | microbiome-pipeline")