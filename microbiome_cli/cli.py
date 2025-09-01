import argparse
from .config import load_config
from .qc import run_qc
from .taxonomy import run_taxonomy
from .pathways import run_pathways
import os


def run_all(samples_dir, config):
    print(f"🚀 Iniciando pipeline completo para muestras en: {samples_dir}")
    if not os.path.exists(samples_dir) or not os.path.isdir(samples_dir):
        print(f"❌ Error: Directorio inválido: {samples_dir}")
        return

    samples = [item for item in os.listdir(samples_dir) if os.path.isdir(os.path.join(samples_dir, item))]
    if not samples:
        print(f"⚠️ No se encontraron muestras en: {samples_dir}")
        return

    print(f"📁 Muestras encontradas: {samples}")
    for sample_name in samples:
        sample_path = os.path.join(samples_dir, sample_name)
        print(f"\n{'='*50}\n📦 PROCESANDO MUESTRA: {sample_name}\n{'='*50}")
        try:
            run_qc(sample_path, config)
            run_taxonomy(sample_path, config)
            run_pathways(sample_path, config)
            print(f"✅ MUESTRA COMPLETADA: {sample_name}")
        except Exception as e:
            print(f"❌ ERROR en {sample_name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Pipeline modular de microbioma")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    subparsers.add_parser("qc", help="QC con KneadData").add_argument("sample", help="Directorio de la muestra")
    subparsers.add_parser("taxonomy", help="Taxonomía con MetaPhlAn").add_argument("sample", help="Directorio de la muestra")
    subparsers.add_parser("pathways", help="Vías con HUMAnN3").add_argument("sample", help="Directorio de la muestra")
    subparsers.add_parser("run-all", help="Ejecutar todo").add_argument("data_dir", help="Directorio con muestras")

    parser.add_argument("--config", default="config.yaml", help="Ruta a config.yaml")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"❌ Error al cargar config: {e}")
        return

    if args.command == "qc":
        run_qc(args.sample, config)
    elif args.command == "taxonomy":
        run_taxonomy(args.sample, config)
    elif args.command == "pathways":
        run_pathways(args.sample, config)
    elif args.command == "run-all":
        run_all(args.data_dir, config)