# microbiome_cli/cli.py
"""
Command Line Interface para el pipeline de microbioma.
"""
import argparse
import os
from .config import load_config
from .qc import run_qc
from .taxonomy import run_taxonomy
from .pathways import run_pathways


def run_all(samples_dir, config):
    print(f"🚀 Iniciando pipeline completo para muestras en: {samples_dir}")
    if not os.path.exists(samples_dir):
        print(f"❌ Error: El directorio no existe: {samples_dir}")
        return
    if not os.path.isdir(samples_dir):
        print(f"❌ Error: La ruta no es un directorio: {samples_dir}")
        return

    try:
        samples = [
            item for item in os.listdir(samples_dir)
            if os.path.isdir(os.path.join(samples_dir, item))
        ]
    except PermissionError as e:
        print(f"❌ Error de permisos al leer el directorio: {e}")
        return

    if not samples:
        print(f"⚠️ No se encontraron muestras en: {samples_dir}")
        return

    print(f"📁 Muestras encontradas: {samples}")
    for sample_name in samples:
        sample_path = os.path.join(samples_dir, sample_name)
        print(f"\n{'='*60}\n📦 PROCESANDO MUESTRA: {sample_name}\n{'='*60}")
        try:
            run_qc(sample_path, config)
            run_taxonomy(sample_path, config)
            run_pathways(sample_path, config)
            print(f"✅ MUESTRA COMPLETADA: {sample_name}")
        except Exception as e:
            print(f"❌ ERROR en {sample_name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline modular de microbioma: QC, taxonomía y vías metabólicas"
    )

    # 1. Subparsers
    subparsers = parser.add_subparsers(
        dest="command",
        help="Comandos disponibles"
    )

    # 2. Definir subcomandos
    subparsers.add_parser("qc", help="Control de calidad").add_argument("sample", help="Carpeta de la muestra")
    subparsers.add_parser("taxonomy", help="Taxonomía con MetaPhlAn").add_argument("sample", help="Carpeta de la muestra")
    subparsers.add_parser("pathways", help="Vías metabólicas con HUMAnN3").add_argument("sample", help="Carpeta de la muestra")
    subparsers.add_parser("run-all", help="Ejecutar todo el pipeline").add_argument("data_dir", help="Carpeta con muestras")

    # ✅ 3. --config DEBE ir aquí (después de subparsers, antes de parse_args)
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Ruta al archivo de configuración (por defecto: config.yaml)"
    )

    # 4. Parsear argumentos
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 5. Cargar configuración
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"❌ Error al cargar config: {e}")
        return

    # 6. Ejecutar comando
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