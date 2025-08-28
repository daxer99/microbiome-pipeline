#!/usr/bin/env python3
# microbiome-cli.py

import os
import subprocess
import yaml
import argparse
from datetime import datetime


# --- Función auxiliar: ejecutar comandos ---
def run_cmd(cmd):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    if result.stdout.strip():
        print(result.stdout.strip())
    return result


# --- Cargar configuración ---
def load_config(config_file="config.yaml"):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_file}")
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


# --- Módulo: QC con KneadData ---
def run_qc(sample_dir, config):
    print(f"🔍 QC: Procesando {sample_dir}")

    # Buscar archivos FASTQ en la carpeta de la muestra
    fastq_files = [
        f for f in os.listdir(sample_dir)
        if f.endswith((".fastq", ".fq", ".fastq.gz", ".fq.gz"))
    ]
    fastq_files.sort()

    if len(fastq_files) < 2:
        raise ValueError(f"No se encontraron suficientes archivos FASTQ en {sample_dir}")

    r1 = os.path.join(sample_dir, fastq_files[0])
    r2 = os.path.join(sample_dir, fastq_files[1])
    output_dir = os.path.join(sample_dir, "kneaddata_output")

    cmd = (
        f"conda run -n {config['tools']['kneaddata_env']} kneaddata "
        f"--input1 {r1} --input2 {r2} "
        f"-db {config['paths']['kneaddata_db']} "
        f"-t {config['tools']['threads']} "
        f"-o {output_dir} "
        #f"--trimmomatic {config['paths']['trimmomatic']} "
        f"--run-fastqc-start --run-fastqc-end"
    )
    run_cmd(cmd)
    print(f"✅ QC completado: {output_dir}")


# --- Módulo: Taxonomía con MetaPhlAn ---
def run_taxonomy(sample_dir, config):
    print(f"🧬 Taxonomía: {sample_dir}")
    clean_dir = os.path.join(sample_dir, "kneaddata_output")

    if not os.path.exists(clean_dir):
        raise FileNotFoundError(f"Directorio kneaddata_output no encontrado: {clean_dir}")

    # Listar solo archivos (no carpetas) y excluir .log
    files = []
    for f in os.listdir(clean_dir):
        path = os.path.join(clean_dir, f)
        if os.path.isfile(path) and not f.endswith('.log'):
            files.append(f)

    # Ordenar alfabéticamente
    files.sort()

    if len(files) < 2:
        raise FileNotFoundError(f"Se esperaban 2 archivos limpios, encontrados: {files}")

    # Buscar R1 y R2 por patrón
    r1_file = None
    r2_file = None
    for f in files:
        if "_paired_1" in f:
            r1_file = f
        elif "_paired_2" in f:
            r2_file = f

    if not r1_file or not r2_file:
        raise FileNotFoundError(f"No se encontraron archivos R1/R2 limpios: {files}")

    r1 = os.path.join(clean_dir, r1_file)
    r2 = os.path.join(clean_dir, r2_file)

    print(f"✅ Archivos limpios encontrados:")
    print(f"   R1: {r1}")
    print(f"   R2: {r2}")

    # Ejecutar MetaPhlAn
    output_file = os.path.join(sample_dir, "profile_mpa.txt")
    temp_bz2 = os.path.join(sample_dir, "profile_mpa.bz2")

    cmd = (
        f"conda run -n {config['tools']['metaphlan_env']} metaphlan "
        f"{r1},{r2} "
        f"--input_type fastq "
        f"--db_dir {config['paths']['metaphlan_db']} "
        f"--mapout {temp_bz2} "
        f"--nproc {config['tools']['threads']} "
        f"-x mpa_vJun23_CHOCOPhlAnSGB_202307 "
        f"-t rel_ab_w_read_stats "
        f"-o {output_file}"
    )
    run_cmd(cmd)
    run_cmd(f"rm {temp_bz2}")
    print(f"✅ Taxonomía completada: {output_file}")


# --- Módulo: Vías metabólicas con HUMAnN3 ---
def run_pathways(sample_dir, config):
    print(f"🧪 Vías metabólicas: {sample_dir}")
    clean_dir = os.path.join(sample_dir, "kneaddata_output")

    if not os.path.exists(clean_dir):
        raise FileNotFoundError(f"Directorio kneaddata_output no encontrado: {clean_dir}")

    # Listar archivos limpios (sin .log)
    files = []
    for f in os.listdir(clean_dir):
        path = os.path.join(clean_dir, f)
        if os.path.isfile(path) and not f.endswith('.log'):
            files.append(f)

    files.sort()

    if len(files) < 2:
        raise FileNotFoundError(f"Se esperaban 2 archivos limpios, encontrados: {files}")

    r1_file = None
    r2_file = None
    for f in files:
        if "_paired_1" in f:
            r1_file = f
        elif "_paired_2" in f:
            r2_file = f

    if not r1_file or not r2_file:
        raise FileNotFoundError(f"No se encontraron archivos R1/R2 limpios: {files}")

    r1 = os.path.join(clean_dir, r1_file)
    r2 = os.path.join(clean_dir, r2_file)

    mpa_profile = os.path.join(sample_dir, "profile_mpa.txt")
    if not os.path.exists(mpa_profile):
        raise FileNotFoundError("Falta perfil taxonómico. Ejecuta 'taxonomy' primero.")

    merged = os.path.join(sample_dir, "merged.fastq")
    humann_out = os.path.join(sample_dir, "humann3_results")

    run_cmd(f"cat {r1} {r2} > {merged}")

    cmd = (
        f"conda run -n {config['tools']['humann3_env']} humann "
        f"--input {merged} "
        f"--output {humann_out} "
        f"--threads {config['tools']['threads']} "
        f"--taxonomic-profile {mpa_profile} "
        f"--remove-temp-output"
    )
    run_cmd(cmd)
    print(f"✅ Vías metabólicas completadas: {humann_out}")


# --- Pipeline completo ---
def run_all(samples_dir, config):
    print(f"🚀 Iniciando pipeline completo para muestras en: {samples_dir}")

    if not os.path.exists(samples_dir):
        print(f"❌ Error: El directorio no existe: {samples_dir}")
        return

    if not os.path.isdir(samples_dir):
        print(f"❌ Error: La ruta no es un directorio: {samples_dir}")
        return

    samples = [
        item for item in os.listdir(samples_dir)
        if os.path.isdir(os.path.join(samples_dir, item))
    ]

    if len(samples) == 0:
        print(f"⚠️  No se encontraron muestras en: {samples_dir}")
        return

    print(f"📁 Muestras encontradas: {samples}")

    for sample_name in samples:
        sample_path = os.path.join(samples_dir, sample_name)
        print(f"\n{'=' * 50}")
        print(f"📦 PROCESANDO MUESTRA: {sample_name}")
        print(f"{'=' * 50}")
        try:
            run_qc(sample_path, config)
            run_taxonomy(sample_path, config)
            run_pathways(sample_path, config)
            print(f"✅ MUESTRA COMPLETADA: {sample_name}")
        except Exception as e:
            print(f"❌ ERROR en {sample_name}: {e}")


# --- CLI principal ---
def main():
    parser = argparse.ArgumentParser(description="Pipeline de microbioma")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    qc_parser = subparsers.add_parser("qc", help="Control de calidad con KneadData")
    qc_parser.add_argument("sample", help="Directorio de la muestra")

    tax_parser = subparsers.add_parser("taxonomy", help="Taxonomía con MetaPhlAn")
    tax_parser.add_argument("sample", help="Directorio de la muestra")

    path_parser = subparsers.add_parser("pathways", help="Vías metabólicas con HUMAnN3")
    path_parser.add_argument("sample", help="Directorio de la muestra")

    all_parser = subparsers.add_parser("run-all", help="Ejecutar todo el pipeline")
    all_parser.add_argument("data_dir", help="Directorio con todas las muestras")

    parser.add_argument("--config", default="config.yaml", help="Ruta al archivo de configuración")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"❌ Error al cargar configuración: {e}")
        return

    if args.command == "qc":
        run_qc(args.sample, config)
    elif args.command == "taxonomy":
        run_taxonomy(args.sample, config)
    elif args.command == "pathways":
        run_pathways(args.sample, config)
    elif args.command == "run-all":
        run_all(args.data_dir, config)


if __name__ == "__main__":
    main()
