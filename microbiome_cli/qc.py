from .utils import run_cmd
import os

def run_qc(sample_dir, config):
    print(f"🔍 QC: Procesando {sample_dir}")

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
        f"--run-fastqc-start --run-fastqc-end"
    )
    run_cmd(cmd)
    print(f"✅ QC completado: {output_dir}")