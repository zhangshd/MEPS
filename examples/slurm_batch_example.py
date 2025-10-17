#!/usr/bin/env python3
"""
SLURM Batch Calculation Example
This script demonstrates how to use the SLURM batch calculation feature.
Author: zhangshd
Date: 2025-10-17
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def example_1_basic_usage():
    """Example 1: Basic usage - generate SLURM scripts only"""
    print_section("Example 1: Generate SLURM Scripts (No Submission)")
    
    print("""
This example generates SLURM job scripts for all molecule pairs but does not
submit them. You can review the scripts before submitting manually.

Command:
    python scripts/batch_interaction_slurm.py \\
        data/molA/ \\
        data/molB/ \\
        results/slurm_batch/

What happens:
    1. Discovers all molecule files in molA/ and molB/ directories
    2. Generates all pairwise combinations (Cartesian product)
    3. Creates a subdirectory for each molecule pair
    4. Generates a submit_job.sh SLURM script in each subdirectory
    5. Creates slurm_logs/ directory for job outputs
    6. Saves summary in slurm_job_summary.json

Output structure:
    results/slurm_batch/
    ├── slurm_logs/                    # Will contain .out and .err files
    ├── molA1_molB1/
    │   └── submit_job.sh              # SLURM submission script
    ├── molA1_molB2/
    │   └── submit_job.sh
    └── slurm_job_summary.json         # Summary of all generated jobs

To submit jobs manually:
    # Submit all jobs at once
    find results/slurm_batch/ -name 'submit_job.sh' -exec sbatch {} \\;
    
    # Or submit selectively
    sbatch results/slurm_batch/molA1_molB1/submit_job.sh
    sbatch results/slurm_batch/molA1_molB2/submit_job.sh
    """)


def example_2_auto_submit():
    """Example 2: Generate and automatically submit jobs"""
    print_section("Example 2: Generate and Auto-Submit Jobs")
    
    print("""
This example generates SLURM scripts and automatically submits all jobs
to the cluster queue.

Command:
    python scripts/batch_interaction_slurm.py \\
        data/molA/ \\
        data/molB/ \\
        results/slurm_batch/ \\
        --submit

What happens:
    1. Generates all SLURM scripts (same as Example 1)
    2. Automatically submits each job using 'sbatch' command
    3. Records job IDs in slurm_job_summary.json
    4. Returns exit code 1 if any jobs fail to submit

Monitor jobs:
    # Check job status
    squeue -u $USER
    
    # Watch job queue (updates every 30 seconds)
    watch -n 30 'squeue -u $USER'
    
    # Check specific job output
    tail -f results/slurm_batch/slurm_logs/molA1_molB1_*.out
    
    # Count completed jobs
    grep -c "Job completed" results/slurm_batch/slurm_logs/*.out
    """)


def example_3_custom_slurm_settings():
    """Example 3: Customize SLURM job settings"""
    print_section("Example 3: Custom SLURM Settings")
    
    print("""
This example shows how to customize SLURM partition, CPU count, and memory
for your specific cluster configuration.

Command:
    python scripts/batch_interaction_slurm.py \\
        data/molA/ \\
        data/molB/ \\
        results/slurm_custom/ \\
        --partition gpu \\
        --cpus 48 \\
        --mem 50GB \\
        --conda-env meps \\
        --submit

Parameters:
    --partition gpu       : Submit to 'gpu' partition instead of default 'C9654'
    --cpus 48            : Use 48 CPU cores per job instead of default 96
    --mem 50GB           : Allocate 50GB memory per job instead of default 100GB
    --conda-env meps     : Use 'meps' conda environment

Resource planning tips:
    - For small molecules (<20 atoms): 24-48 CPUs, 20-50GB RAM
    - For medium molecules (20-50 atoms): 48-96 CPUs, 50-100GB RAM
    - For large molecules (>50 atoms): 96+ CPUs, 100-200GB RAM
    
    Check available partitions:
        sinfo
    
    Check partition limits:
        scontrol show partition <partition_name>
    """)


def example_4_calculation_parameters():
    """Example 4: Customize calculation parameters"""
    print_section("Example 4: Custom Calculation Parameters")
    
    print("""
This example demonstrates how to specify quantum chemistry calculation
parameters (functional, basis set, dispersion correction).

Command:
    python scripts/batch_interaction_slurm.py \\
        data/molA/ \\
        data/molB/ \\
        results/slurm_m062x/ \\
        --functional M06-2X \\
        --basis def2-TZVP \\
        --dispersion GD3 \\
        --submit

Parameters:
    --functional M06-2X   : Use M06-2X functional instead of default B3LYP
    --basis def2-TZVP     : Use def2-TZVP basis set instead of 6-311++G(d,p)
    --dispersion GD3      : Use Grimme's D3 dispersion instead of D3BJ

Functional choices:
    - B3LYP     : Default, economical, good for initial screening
    - M06-2X    : Robust, recommended for non-covalent interactions
    - wB97X-D   : Long-range corrected, excellent for weak interactions
    - B2PLYP    : Double-hybrid, high accuracy but expensive

Basis set recommendations:
    - 6-311++G(d,p)  : Default, balanced accuracy/cost
    - def2-TZVP      : Modern, efficient, good performance
    - aug-cc-pVTZ    : High accuracy, computationally expensive
    """)


def example_5_file_filtering():
    """Example 5: Filter files by extension"""
    print_section("Example 5: Filter Input Files")
    
    print("""
This example shows how to process only specific file types from the input
directories.

Command:
    python scripts/batch_interaction_slurm.py \\
        data/molA/ \\
        data/molB/ \\
        results/slurm_mol2/ \\
        --extensions .mol2 .xyz \\
        --submit

Parameters:
    --extensions .mol2 .xyz  : Only process MOL2 and XYZ files

Default extensions (if not specified):
    .xyz, .pdb, .mol, .sdf, .mol2

Use case:
    - Mixed directory with multiple file formats
    - Want to exclude certain file types
    - Testing with specific format only
    
Example directory structure:
    data/molA/
    ├── mol1.xyz       # Will be processed
    ├── mol2.mol2      # Will be processed
    ├── mol3.pdb       # Will be IGNORED
    └── mol4.gjf       # Will be IGNORED
    """)


def example_6_no_docking():
    """Example 6: Skip molecular docking step"""
    print_section("Example 6: Skip Molecular Docking")
    
    print("""
This example demonstrates how to disable the molecular docking step and use
the optimized monomer structures directly to form the complex.

Command:
    python scripts/batch_interaction_slurm.py \\
        data/molA/ \\
        data/molB/ \\
        results/slurm_no_dock/ \\
        --no-docking \\
        --submit

When to use --no-docking:
    ✓ You already have pre-arranged complex structures
    ✓ You want to test specific relative orientations
    ✓ Docking is not appropriate for your system
    ✓ Faster calculation (skips docking step)

Workflow with --no-docking:
    1. Optimize monomer A
    2. Optimize monomer B
    3. Combine optimized monomers directly (no docking)
    4. Optimize complex
    5. Extract results

Workflow with docking (default):
    1. Optimize monomer A
    2. Optimize monomer B
    3. Dock monomers to find best orientation
    4. Use docked structure for complex
    5. Optimize complex
    6. Extract results
    """)


def example_7_monitoring_jobs():
    """Example 7: Monitor and manage submitted jobs"""
    print_section("Example 7: Monitor and Manage Jobs")
    
    print("""
After submitting jobs, here are useful commands to monitor and manage them:

1. Check job queue status:
    squeue -u $USER
    
2. Check detailed job information:
    squeue -u $USER --format="%.18i %.9P %.30j %.8T %.10M %.6D %R"
    
    Columns:
        JOBID    : Job ID
        PARTITION: Partition name
        NAME     : Job name (molecule pair name)
        ST       : State (PD=Pending, R=Running, CG=Completing)
        TIME     : Time running
        NODES    : Number of nodes
        NODELIST : Allocated nodes or reason for pending
    
3. Check when pending jobs will start:
    squeue -u $USER --start
    
4. Watch job queue (auto-refresh):
    watch -n 30 'squeue -u $USER'
    
5. Monitor specific job output in real-time:
    tail -f results/slurm_batch/slurm_logs/molA1_molB1_12345.out
    
6. Search for completed jobs:
    grep -l "Job completed" results/slurm_batch/slurm_logs/*.out
    
7. Find failed jobs:
    grep -l "Error\\|Exception\\|Failed" results/slurm_batch/slurm_logs/*.err
    
8. Count job statistics:
    # Total jobs submitted
    ls results/slurm_batch/*/submit_job.sh | wc -l
    
    # Completed jobs
    grep -c "Job completed" results/slurm_batch/slurm_logs/*.out
    
    # Running jobs
    squeue -u $USER -t RUNNING | wc -l
    
    # Pending jobs
    squeue -u $USER -t PENDING | wc -l
    
9. Cancel jobs:
    # Cancel specific job
    scancel 12345
    
    # Cancel all your jobs
    scancel -u $USER
    
    # Cancel jobs by name pattern
    scancel -u $USER --name="molA1_*"
    
10. Resubmit failed jobs:
    # Find and resubmit failed jobs
    for err_file in results/slurm_batch/slurm_logs/*.err; do
        if grep -q "Error" "$err_file"; then
            job_name=$(basename "$err_file" | sed 's/_.*.err//')
            echo "Resubmitting $job_name"
            sbatch "results/slurm_batch/${job_name}/submit_job.sh"
        fi
    done
    """)


def example_8_workflow():
    """Example 8: Complete workflow from setup to analysis"""
    print_section("Example 8: Complete Workflow")
    
    print("""
This example shows a complete workflow from preparing input files to
analyzing results.

Step 1: Prepare input directories
    mkdir -p data/receptors data/ligands
    
    # Copy your molecule files
    cp /path/to/receptor*.mol2 data/receptors/
    cp /path/to/ligand*.mol2 data/ligands/

Step 2: Generate SLURM scripts (dry run)
    python scripts/batch_interaction_slurm.py \\
        data/receptors/ \\
        data/ligands/ \\
        results/production/
    
    # Review the generated scripts
    cat results/production/receptor1_ligand1/submit_job.sh

Step 3: Submit jobs
    python scripts/batch_interaction_slurm.py \\
        data/receptors/ \\
        data/ligands/ \\
        results/production/ \\
        --functional M06-2X \\
        --basis 6-311++G(d,p) \\
        --cpus 96 \\
        --mem 100GB \\
        --submit

Step 4: Monitor progress
    # Watch job queue
    watch -n 30 'squeue -u $USER'
    
    # Check how many completed
    grep -c "Job completed" results/production/slurm_logs/*.out

Step 5: Analyze results
    # Extract interaction energies from all results
    python -c "
    import json
    from pathlib import Path
    
    results_dir = Path('results/production')
    energies = []
    
    for pair_dir in results_dir.glob('*_*'):
        result_file = pair_dir / 'results' / 'interaction_energy_results.json'
        if result_file.exists():
            with open(result_file) as f:
                data = json.load(f)
                energies.append({
                    'pair': pair_dir.name,
                    'energy': data.get('complexation_energy_corrected', 'N/A')
                })
    
    # Sort by energy
    energies.sort(key=lambda x: x['energy'] if isinstance(x['energy'], float) else 999)
    
    # Print results
    print('\\nInteraction Energies (sorted):')
    print('-' * 60)
    for e in energies:
        print(f'{e[\"pair\"]:40} {e[\"energy\"]:>15} kcal/mol')
    "

Step 6: Handle failed jobs (if any)
    # Find failed jobs
    failed_jobs=()
    for err_file in results/production/slurm_logs/*.err; do
        if grep -q "Error" "$err_file"; then
            failed_jobs+=("$err_file")
        fi
    done
    
    # Review error messages
    for err_file in "${failed_jobs[@]}"; do
        echo "=== $err_file ==="
        tail -20 "$err_file"
    done
    
    # Resubmit if needed
    for err_file in "${failed_jobs[@]}"; do
        job_name=$(basename "$err_file" | sed 's/_.*.err//')
        sbatch "results/production/${job_name}/submit_job.sh"
    done
    """)


def main():
    """Main function"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   SLURM Batch Calculation Examples                         ║
║                                                                            ║
║  This script demonstrates various use cases for the SLURM batch            ║
║  calculation feature in MEPS.                                              ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run all examples
    example_1_basic_usage()
    example_2_auto_submit()
    example_3_custom_slurm_settings()
    example_4_calculation_parameters()
    example_5_file_filtering()
    example_6_no_docking()
    example_7_monitoring_jobs()
    example_8_workflow()
    
    print_section("Summary")
    print("""
The SLURM batch calculation feature provides:
    ✓ Automatic generation of SLURM job scripts
    ✓ Independent jobs for each molecule pair
    ✓ No parallel job limits (managed by SLURM)
    ✓ Flexible resource allocation per job
    ✓ Comprehensive job monitoring and logging
    ✓ Easy resubmission of failed jobs

For more information, see:
    - docs/SLURM_BATCH_CALCULATION.md
    - scripts/batch_interaction_slurm.py --help

Happy computing!
    """)


if __name__ == '__main__':
    main()
