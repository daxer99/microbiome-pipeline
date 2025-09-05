#!/bin/bash
# setup.sh
# Instalación completa del pipeline de microbioma

set -e

echo "🚀 Iniciando instalación del entorno microbiome-pipeline"

ENV_NAME="microbiome-pipeline"

# 1. Crear entorno conda
echo "🔹 Creando entorno conda: $ENV_NAME"
conda create -n "$ENV_NAME" -y
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# 2. Instalar herramientas
echo "🔹 Instalando herramientas bioinformáticas..."
conda install -c conda-forge -c bioconda -y \
    metaphlan=4.2.2 \
    kneaddata=0.12.3 \
    bowtie2 \
    samtools \
    pigz

# 3. Instalar HUMAnN (si es necesario)
echo "🔹 Instalando HUMAnN..."
pip install humann