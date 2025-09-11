
# microbiome-pipeline

Es un flujo de trabajo completo capaz de obtener resultados de abundancia relativa de microorganismos, genes y rutas metabolicas de muestras de microbiota a partir de secuencias de material genetico.

Este pipeline permite procesar datos de metagenómica mediante una interfaz modular y reproducible. Está diseñado para ejecutar:

- Control de calidad (QC) con KneadData
- Clasificación taxonómica con MetaPhlAn4
- Perfilado funcional con HUMAnN3

Incluye una interfaz gráfica (GUI).

## Requerimientos
- Sistema Operativo Linux (recomendado) o WSL2 en Windows
- Python: 3.8 o superior
- Gestor de entornos: conda, miniforge o mamba
- Espacio en disco: ~50 GB (para bases de datos)
- Sistema de gestion de versiones (GIT)

## Instalacion

1. Clonar el repositorio.
```bash
git clone https://github.com/daxer99/microbiome-pipeline.git
cd microbiome-pipeline
```
2. Crear el entorno virtual, instalando dependencias y requerimientos.
```bash
./setup.sh
```
3. Instalar el paquete en modo desarrollo.
```bash
pip install -e .
```
## Descarga de bases de datos
- Opcion 1: mediante GUI. 
```bash
streamlit run app.py
```
![Logo](https://i.ibb.co/6RMDq7nj/screencapture-localhost-8501-2025-09-08-12-24-51-1.png)

- Opcion 2: mediante terminal dentro del entorno microbiome-pipeline.
```bash
# KneadData (genoma humano hg37)
kneaddata_database --download human_genome bowtie2 $DIR

# MetaPhlAn
metaphlan --install --index mpa_vJun23_CHOCOPhlAnSGB_202307 --db_dir $DIR

# HUMAnN - ChocoPhlAn
humann_databases --download chocophlan full $DIR

# HUMAnN - UniRef
humann_databases --download uniref uniref90_diamond $DIR

# HUMAnN - Utility Mapping (para KO, GO, EC, etc.)
humann_databases --download utility_mapping full $DIR
```
## Uso
- CLI (linea de comandos)

```bash
# Control de calidad (QC)
microbiome-cli qc /ruta/a/muestra_01

# Taxonomía
microbiome-cli taxonomy /ruta/a/muestra_01

# Vías metabólicas
microbiome-cli pathways /ruta/a/muestra_01

# Todo el pipeline (procesa todas las muestras en la carpeta)
microbiome-cli run-all /ruta/a/muestras/
```

- GUI (Interfaz grafica)
```bash
streamlit run app.py
```
![Logo](https://i.ibb.co/s9nxJ0jr/screencapture-localhost-8501-2025-09-08-12-26-29-1.png)
## Licencia

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)


## Autor

- [@Rodrigo Peralta](https://www.github.com/daxer99)

