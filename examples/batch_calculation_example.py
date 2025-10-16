#!/usr/bin/env python3
"""
Batch Calculation Test Example
This script demonstrates how to use the batch interaction energy calculator
Author: zhangshd
Date: 2025-10-16
"""

from pathlib import Path
import shutil


def create_test_directories():
    """Create test directories with sample molecule files"""
    
    # Create test directories
    test_dir = Path(__file__).parent / "test_batch"
    molA_dir = test_dir / "molA"
    molB_dir = test_dir / "molB"
    output_dir = test_dir / "results"
    
    # Clean up existing test directory
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    molA_dir.mkdir(parents=True, exist_ok=True)
    molB_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy sample molecules to test directories
    data_input = Path(__file__).parent.parent / "data" / "input"
    
    # Copy water.xyz to molA directory (create multiple copies with different names)
    if (data_input / "water.xyz").exists():
        shutil.copy(data_input / "water.xyz", molA_dir / "water.xyz")
        shutil.copy(data_input / "water.xyz", molA_dir / "water2.xyz")
    
    # Copy methane.xyz to molB directory (if exists)
    if (data_input / "methane.xyz").exists():
        shutil.copy(data_input / "methane.xyz", molB_dir / "methane.xyz")
        shutil.copy(data_input / "methane.xyz", molB_dir / "methane2.xyz")
    else:
        # Create a simple methane structure if methane.xyz doesn't exist
        methane_content = """5
Methane molecule
C     0.000000     0.000000     0.000000
H     0.629118     0.629118     0.629118
H    -0.629118    -0.629118     0.629118
H    -0.629118     0.629118    -0.629118
H     0.629118    -0.629118    -0.629118
"""
        with open(molB_dir / "methane.xyz", 'w') as f:
            f.write(methane_content)
        with open(molB_dir / "methane2.xyz", 'w') as f:
            f.write(methane_content)
    
    print(f"Test directories created:")
    print(f"  molA: {molA_dir} ({len(list(molA_dir.glob('*.xyz')))} files)")
    print(f"  molB: {molB_dir} ({len(list(molB_dir.glob('*.xyz')))} files)")
    print(f"  output: {output_dir}")
    
    return str(molA_dir), str(molB_dir), str(output_dir)


def print_usage_examples():
    """Print usage examples"""
    print("\n" + "="*80)
    print("Batch Interaction Energy Calculator - Usage Examples")
    print("="*80)
    
    print("""
1. Basic Usage (Auto-detect parallel jobs):
   python scripts/batch_interaction_energy.py molA/ molB/ results/
   
   This will:
   - Discover all molecule files (.xyz, .pdb, .mol, .sdf, .mol2) in molA/ and molB/
   - Calculate interaction energy for all pairs
   - Auto-detect optimal parallel job count based on CPU cores
   - Save each pair's results in results/molA_molB/

2. Control Computational Resources:
   python scripts/batch_interaction_energy.py molA/ molB/ results/ \\
       --nproc 48 --max-jobs 4 --mem 50GB
   
   - Each Gaussian job uses 48 CPU cores
   - Run maximum 4 jobs in parallel
   - Allocate 50GB memory per job

3. Specify Calculation Parameters:
   python scripts/batch_interaction_energy.py molA/ molB/ results/ \\
       --functional M06-2X --basis def2-TZVP --dispersion GD3
   
   - Use M06-2X functional
   - Use def2-TZVP basis set
   - Use GD3 dispersion correction

4. Without Molecular Docking:
   python scripts/batch_interaction_energy.py molA/ molB/ results/ \\
       --no-docking
   
   - Skip AutoDock Vina docking step
   - Use input structures directly

5. Specify File Types:
   python scripts/batch_interaction_energy.py molA/ molB/ results/ \\
       --extensions .mol .mol2
   
   - Only process .mol and .mol2 files
   - Ignore other formats

6. Complete Example with All Options:
   python scripts/batch_interaction_energy.py molA/ molB/ results/ \\
       --nproc 96 \\
       --max-jobs 2 \\
       --mem 100GB \\
       --functional B3LYP \\
       --basis "6-311++G(d,p)" \\
       --dispersion GD3BJ \\
       --gaussian-root /opt/share/gaussian/g16 \\
       --extensions .xyz .pdb .mol

Output Structure:
  results/
  ├── batch_summary.json          # Overall summary of all calculations
  ├── molA1_molB1/                # Results for molA1-molB1 pair
  │   ├── complex.gjf
  │   ├── complex.log
  │   ├── results.json
  │   └── results.txt
  ├── molA1_molB2/                # Results for molA1-molB2 pair
  │   └── ...
  └── molA2_molB1/                # Results for molA2-molB1 pair
      └── ...

Summary File (batch_summary.json) Contains:
  - Configuration parameters
  - Total/successful/failed calculations
  - Timing statistics
  - Results for each successful pair
  - Error messages for failed pairs
    """)


def print_cpu_configuration_guide():
    """Print CPU configuration guide"""
    print("\n" + "="*80)
    print("CPU Configuration Guide")
    print("="*80)
    
    import multiprocessing as mp
    total_cpus = mp.cpu_count()
    
    print(f"\nYour system has {total_cpus} CPU cores available.")
    print("\nRecommended configurations:")
    
    configs = [
        (96, total_cpus // 96),
        (48, total_cpus // 48),
        (32, total_cpus // 32),
        (24, total_cpus // 24),
        (16, total_cpus // 16),
        (12, total_cpus // 12),
        (8, total_cpus // 8),
        (4, total_cpus // 4),
    ]
    
    print(f"\n{'Cores/Job':<12} {'Max Jobs':<12} {'Total Used':<12} {'Efficiency':<12}")
    print("-" * 50)
    
    for nproc, max_jobs in configs:
        if max_jobs >= 1:
            total_used = nproc * max_jobs
            efficiency = (total_used / total_cpus) * 100
            print(f"{nproc:<12} {max_jobs:<12} {total_used:<12} {efficiency:.1f}%")
    
    print("\nRecommendations:")
    print("  1. For large molecules: Use 96 cores per job for faster single calculations")
    print("  2. For many small molecules: Use 24-48 cores per job for more parallelism")
    print("  3. Balance based on memory: Each job needs sufficient memory (default 100GB)")
    print("  4. Monitor system load: Avoid oversubscription of CPUs or memory")


def main():
    """Main function"""
    print_usage_examples()
    print_cpu_configuration_guide()
    
    print("\n" + "="*80)
    print("Creating test directories...")
    print("="*80)
    
    molA_dir, molB_dir, output_dir = create_test_directories()
    
    print("\n" + "="*80)
    print("To run the test calculation:")
    print("="*80)
    print(f"\npython scripts/batch_interaction_energy.py {molA_dir} {molB_dir} {output_dir} \\")
    print(f"    --nproc 8 --max-jobs 2 --no-docking")
    print("\nNote: Using --no-docking for quick testing (skips AutoDock Vina step)")
    

if __name__ == '__main__':
    main()
