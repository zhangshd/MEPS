# SLURM Batch Calculation Guide

This document describes how to use the SLURM-based batch calculation script for molecular interaction energy calculations.

## Overview

`batch_interaction_slurm.py` generates and submits SLURM jobs for calculating pairwise interaction energies between molecules from two directories. Each molecule pair gets its own independent SLURM job.

## Key Features

- **Independent Jobs**: Each molecule pair runs as a separate SLURM job
- **No Process Pool**: No parallel job limits - let SLURM handle scheduling
- **Organized Output**: Each pair gets its own subdirectory with SLURM script
- **Flexible Submission**: Generate scripts first, review, then submit; or auto-submit
- **Comprehensive Logging**: All SLURM outputs saved in `slurm_logs/` directory

## Usage

### Basic Usage

Generate SLURM scripts only (no submission):
```bash
python scripts/batch_interaction_slurm.py molA_dir/ molB_dir/ results/
```

Generate and automatically submit all jobs:
```bash
python scripts/batch_interaction_slurm.py molA_dir/ molB_dir/ results/ --submit
```

### Advanced Options

#### SLURM Configuration

```bash
python scripts/batch_interaction_slurm.py molA/ molB/ results/ \
    --partition gpu \
    --cpus 48 \
    --mem 50GB \
    --conda-env meps
```

#### Calculation Parameters

```bash
python scripts/batch_interaction_slurm.py molA/ molB/ results/ \
    --functional M06-2X \
    --basis def2-TZVP \
    --dispersion GD3
```

#### Disable Molecular Docking

```bash
python scripts/batch_interaction_slurm.py molA/ molB/ results/ --no-docking
```

#### Custom File Extensions

```bash
python scripts/batch_interaction_slurm.py molA/ molB/ results/ \
    --extensions .xyz .mol2
```

## Command Line Arguments

### Required Arguments

- `molA_dir`: Directory containing molecule A structure files
- `molB_dir`: Directory containing molecule B structure files
- `output_dir`: Output directory for all results

### SLURM Settings

- `--partition`: SLURM partition name (default: C9654)
- `--cpus`: CPUs per task (default: 96)
- `--mem`: Memory per job (default: 100GB)
- `--conda-env`: Conda environment name (default: meps)

### Calculation Parameters

- `--functional`: DFT functional (default: B3LYP)
  - Choices: B3LYP, M06-2X, wB97X-D, B2PLYP
- `--basis`: Basis set (default: 6-311++G(d,p))
- `--dispersion`: Dispersion correction (default: GD3BJ)
  - Choices: GD3, GD3BJ, None

### Other Options

- `--no-docking`: Disable molecular docking
- `--submit`: Automatically submit generated jobs
- `--extensions`: File extensions to search (default: .xyz .pdb .mol .sdf .mol2)

## Output Structure

```
results/
├── slurm_logs/                    # SLURM output and error logs
│   ├── molA1_molB1_12345.out
│   ├── molA1_molB1_12345.err
│   └── ...
├── molA1_molB1/                   # First molecule pair
│   ├── submit_job.sh              # SLURM submission script
│   ├── complex/                   # Calculation files
│   ├── monomers/
│   └── results/
├── molA1_molB2/                   # Second molecule pair
│   └── ...
├── molA2_molB1/                   # Third molecule pair
│   └── ...
└── slurm_job_summary.json         # Summary of all jobs
```

## Workflow

### Step 1: Generate SLURM Scripts

First, generate all SLURM scripts without submitting:

```bash
python scripts/batch_interaction_slurm.py molA/ molB/ results/
```

This creates:
- Individual `submit_job.sh` scripts in each pair's directory
- Summary file `slurm_job_summary.json`
- `slurm_logs/` directory for job outputs

### Step 2: Review Scripts (Optional)

Check a few generated scripts to ensure they're correct:

```bash
cat results/molA1_molB1/submit_job.sh
```

### Step 3: Submit Jobs

#### Option A: Submit All Jobs at Once

```bash
find results/ -name 'submit_job.sh' -exec sbatch {} \;
```

#### Option B: Submit Selectively

```bash
sbatch results/molA1_molB1/submit_job.sh
sbatch results/molA1_molB2/submit_job.sh
```

#### Option C: Auto-Submit During Generation

```bash
python scripts/batch_interaction_slurm.py molA/ molB/ results/ --submit
```

### Step 4: Monitor Jobs

Check job status:
```bash
squeue -u $USER
```

Check specific job output:
```bash
tail -f results/slurm_logs/molA1_molB1_12345.out
```

Check all running jobs:
```bash
squeue -u $USER --format="%.18i %.9P %.30j %.8T %.10M %.6D %R"
```

### Step 5: Collect Results

All successful jobs will have results in their respective directories:
```bash
# Check completion
grep -r "Job completed" results/slurm_logs/*.out

# Find failed jobs
grep -r "Error" results/slurm_logs/*.err
```

## SLURM Script Template

Each generated SLURM script follows this template:

```bash
#!/bin/bash
#SBATCH --job-name=molA_molB
#SBATCH --output=slurm_logs/%x_%A.out
#SBATCH --error=slurm_logs/%x_%A.err
#SBATCH --partition=C9654
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96

# Set conda environment paths
export PATH=/opt/share/miniconda3/envs/meps/bin/:$PATH
export LD_LIBRARY_PATH=/opt/share/miniconda3/envs/meps/lib/:$LD_LIBRARY_PATH

# Change to pair output directory
cd /path/to/output/molA_molB

# Print job information
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURM_NODELIST"
echo "Start Time: $(date)"

# Run calculation
srun python scripts/run_pipeline.py molA.mol2 molB.mol2 \
    --name_a molA --name_b molB \
    --functional B3LYP --basis 6-311++G(d,p) \
    --dispersion GD3BJ --mem 100GB --nproc 96

echo "End Time: $(date)"
echo "Job completed"
```

## Job Summary File

`slurm_job_summary.json` contains:

```json
{
  "total_pairs": 100,
  "scripts_generated": 100,
  "jobs_submitted": 100,
  "generated_scripts": [
    {
      "pair_name": "molA1_molB1",
      "script_path": "/path/to/results/molA1_molB1/submit_job.sh",
      "molA": "/path/to/molA1.mol2",
      "molB": "/path/to/molB1.mol2"
    }
  ],
  "submitted_jobs": [
    {
      "pair_name": "molA1_molB1",
      "job_id": "12345",
      "script_path": "/path/to/results/molA1_molB1/submit_job.sh"
    }
  ]
}
```

## Tips and Best Practices

### 1. Test First
Run with a small subset of molecules first to validate settings:
```bash
# Create test directories with 2-3 molecules
mkdir test_molA test_molB
cp molA/molecule1.mol2 test_molA/
cp molB/molecule1.mol2 test_molB/
python scripts/batch_interaction_slurm.py test_molA/ test_molB/ test_results/
```

### 2. Resource Estimation
- Small molecules (<20 atoms): 24-48 CPUs, 20-50GB RAM
- Medium molecules (20-50 atoms): 48-96 CPUs, 50-100GB RAM
- Large molecules (>50 atoms): 96+ CPUs, 100-200GB RAM

### 3. Partition Selection
Choose appropriate partition based on:
- Job duration
- Resource requirements
- Queue availability

### 4. Monitor Disk Space
Check available space before large batch submissions:
```bash
df -h /path/to/results
```

### 5. Job Arrays (Alternative)
For very large batches, consider using SLURM job arrays for better queue management.

### 6. Error Handling
Check for common errors:
```bash
# Find jobs with errors
grep -l "Error\|Exception\|Failed" results/slurm_logs/*.err

# Count completed jobs
grep -c "Job completed" results/slurm_logs/*.out
```

### 7. Resubmit Failed Jobs
```bash
# Find failed job scripts
for err_file in results/slurm_logs/*.err; do
    if grep -q "Error" "$err_file"; then
        job_name=$(basename "$err_file" | sed 's/_.*.err//')
        sbatch "results/${job_name}/submit_job.sh"
    fi
done
```

## Comparison with Multiprocessing Script

| Feature | `batch_interaction_energy.py` | `batch_interaction_slurm.py` |
|---------|------------------------------|------------------------------|
| Execution | Local multiprocessing | SLURM cluster |
| Parallelism | Limited by local CPUs | Limited by cluster capacity |
| Job Management | Python process pool | SLURM scheduler |
| Fault Tolerance | Single point of failure | Independent jobs |
| Resource Control | Global limits | Per-job limits |
| Monitoring | Console output | SLURM logs |
| Best For | Small batches, testing | Large batches, production |

## Troubleshooting

### Jobs Not Starting
- Check partition availability: `sinfo`
- Check job queue: `squeue -u $USER`
- Verify resource limits: `scontrol show partition <partition_name>`

### Jobs Failing Immediately
- Check SLURM error logs in `slurm_logs/`
- Verify conda environment: `conda env list`
- Test run_pipeline.py manually

### Out of Memory Errors
- Increase `--mem` parameter
- Reduce `--cpus` if memory per CPU is limited
- Use larger basis set only when necessary

### Slow Job Start
- SLURM queue is busy - jobs will start when resources available
- Check estimated start time: `squeue -u $USER --start`

## Example Workflow

Complete example for calculating interaction energies:

```bash
# 1. Prepare molecule directories
ls molA/  # Contains: mol1.mol2, mol2.mol2, mol3.mol2
ls molB/  # Contains: ligand1.mol2, ligand2.mol2

# 2. Generate SLURM scripts
python scripts/batch_interaction_slurm.py \
    molA/ molB/ results/ \
    --functional B3LYP \
    --basis 6-311++G(d,p) \
    --cpus 96 \
    --mem 100GB

# 3. Review generated scripts
cat results/mol1_ligand1/submit_job.sh

# 4. Submit all jobs
find results/ -name 'submit_job.sh' -exec sbatch {} \;

# 5. Monitor progress
watch -n 30 'squeue -u $USER'

# 6. Check results when complete
python -c "
import json
with open('results/slurm_job_summary.json') as f:
    summary = json.load(f)
    print(f'Total: {summary[\"total_pairs\"]}')
    print(f'Generated: {summary[\"scripts_generated\"]}')
"

# 7. Analyze results
grep "Interaction Energy" results/*/results/*.json
```

## See Also

- [Batch Calculation Guide](BATCH_CALCULATION.md) - Multiprocessing version
- [Tutorial](../QUICKSTART.md) - Single pair calculation
- [README](../README.md) - Project overview
