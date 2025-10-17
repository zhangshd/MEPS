#!/usr/bin/env python3
"""
Batch Interaction Energy Calculation Script with SLURM
This script generates and submits SLURM jobs for pairwise interaction energy calculations.
Each molecule pair gets its own SLURM job.
Author: zhangshd
Date: 2025-10-17
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import subprocess
import time

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class SlurmBatchCalculator:
    """SLURM batch calculator for pairwise molecular interaction energies"""
    
    def __init__(
        self,
        molA_dir: str,
        molB_dir: str,
        output_dir: str,
        partition: str = "C9654",
        cpus_per_task: int = 96,
        mem: str = "100GB",
        functional: str = "B3LYP",
        basis_set: str = "6-311++G(d,p)",
        dispersion: str = "GD3BJ",
        use_docking: bool = True,
        conda_env: str = "meps",
        file_extensions: List[str] = None,
        submit_jobs: bool = False
    ):
        """
        Initialize SLURM batch calculator
        
        Args:
            molA_dir: Directory containing molecule A files
            molB_dir: Directory containing molecule B files
            output_dir: Output directory for all calculations
            partition: SLURM partition name
            cpus_per_task: Number of CPU cores per task
            mem: Memory per job
            functional: DFT functional
            basis_set: Basis set
            dispersion: Dispersion correction
            use_docking: Whether to use molecular docking
            conda_env: Conda environment name
            file_extensions: Supported file extensions
            submit_jobs: Whether to automatically submit jobs
        """
        self.molA_dir = Path(molA_dir)
        self.molB_dir = Path(molB_dir)
        self.output_dir = Path(output_dir)
        self.partition = partition
        self.cpus_per_task = cpus_per_task
        self.mem = mem
        self.functional = functional
        self.basis_set = basis_set
        self.dispersion = dispersion
        self.use_docking = use_docking
        self.conda_env = conda_env
        self.submit_jobs = submit_jobs
        
        # Supported file extensions
        if file_extensions is None:
            self.file_extensions = ['.xyz', '.pdb', '.mol', '.sdf', '.mol2']
        else:
            self.file_extensions = file_extensions
        
        # Validate directories
        if not self.molA_dir.exists():
            raise FileNotFoundError(f"Molecule A directory not found: {molA_dir}")
        if not self.molB_dir.exists():
            raise FileNotFoundError(f"Molecule B directory not found: {molB_dir}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create slurm_logs directory
        self.slurm_logs_dir = self.output_dir / "slurm_logs"
        self.slurm_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Get project root directory
        self.project_root = Path(__file__).parent.parent
        
        print(f"SLURM Batch Calculator Configuration:")
        print(f"  Partition: {self.partition}")
        print(f"  CPUs per task: {self.cpus_per_task}")
        print(f"  Memory: {self.mem}")
        print(f"  Conda environment: {self.conda_env}")
        print(f"  Output directory: {self.output_dir}")
        print(f"  SLURM logs directory: {self.slurm_logs_dir}")
    
    def discover_molecules(self, directory: Path) -> List[Path]:
        """
        Discover all molecule structure files in a directory
        
        Args:
            directory: Directory to search
            
        Returns:
            List of molecule file paths
        """
        molecules = []
        for ext in self.file_extensions:
            molecules.extend(directory.glob(f"*{ext}"))
        
        molecules.sort()
        return molecules
    
    def generate_molecule_pairs(self) -> List[Tuple[Path, Path, str]]:
        """
        Generate all pairwise combinations of molecules from two directories
        
        Returns:
            List of tuples: (molA_file, molB_file, pair_name)
        """
        molA_files = self.discover_molecules(self.molA_dir)
        molB_files = self.discover_molecules(self.molB_dir)
        
        if not molA_files:
            raise ValueError(f"No molecule files found in {self.molA_dir}")
        if not molB_files:
            raise ValueError(f"No molecule files found in {self.molB_dir}")
        
        print(f"\nDiscovered molecules:")
        print(f"  Molecule A directory: {len(molA_files)} files")
        print(f"  Molecule B directory: {len(molB_files)} files")
        
        pairs = []
        for molA in molA_files:
            for molB in molB_files:
                name_a = molA.stem
                name_b = molB.stem
                pair_name = f"{name_a}_{name_b}"
                pairs.append((molA, molB, pair_name))
        
        print(f"  Total pairs to calculate: {len(pairs)}")
        return pairs
    
    def generate_slurm_script(
        self,
        molA_file: Path,
        molB_file: Path,
        pair_name: str,
        pair_output_dir: Path
    ) -> Path:
        """
        Generate SLURM job script for a molecule pair
        
        Args:
            molA_file: Path to molecule A file
            molB_file: Path to molecule B file
            pair_name: Name of the molecule pair
            pair_output_dir: Output directory for this pair
            
        Returns:
            Path to generated SLURM script
        """
        # Create SLURM script path
        slurm_script = pair_output_dir / "submit_job.sh"
        
        # Get absolute paths
        molA_abs = molA_file.resolve()
        molB_abs = molB_file.resolve()
        pair_output_abs = pair_output_dir.resolve()
        
        # Get molecule names
        name_a = molA_file.stem
        name_b = molB_file.stem
        
        # Build run_pipeline.py command with proper shell escaping
        # Use shlex.quote to properly escape arguments for shell
        from shlex import quote
        
        cmd_parts = [
            "python",
            quote(str(self.project_root / "scripts" / "run_pipeline.py")),
            quote(str(molA_abs)),
            quote(str(molB_abs)),
            "--name_a", quote(name_a),
            "--name_b", quote(name_b),
            "--functional", quote(self.functional),
            "--basis", quote(self.basis_set),
            "--dispersion", quote(self.dispersion),
            "--mem", quote(self.mem),
            "--nproc", str(self.cpus_per_task),
        ]
        
        if not self.use_docking:
            cmd_parts.append("--no-docking")
        
        run_command = " ".join(cmd_parts)
        
        # Generate SLURM script content
        script_content = f"""#!/bin/bash
#SBATCH --job-name={pair_name}
#SBATCH --output={self.slurm_logs_dir.resolve()}/%x_%A.out
#SBATCH --error={self.slurm_logs_dir.resolve()}/%x_%A.err
#SBATCH --partition={self.partition}
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task={self.cpus_per_task}

# Set conda environment paths
export PATH=/opt/share/miniconda3/envs/{self.conda_env}/bin/:$PATH
export LD_LIBRARY_PATH=/opt/share/miniconda3/envs/{self.conda_env}/lib/:$LD_LIBRARY_PATH

# Change to pair output directory
cd {pair_output_abs}

# Print job information
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURM_NODELIST"
echo "Start Time: $(date)"
echo "Working Directory: $(pwd)"
echo ""
echo "Molecule A: {molA_abs}"
echo "Molecule B: {molB_abs}"
echo ""

# Run calculation
srun {run_command}

# Print completion information
echo ""
echo "End Time: $(date)"
echo "Job completed"
"""
        
        # Write SLURM script
        with open(slurm_script, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        slurm_script.chmod(0o755)
        
        return slurm_script
    
    def submit_slurm_job(self, slurm_script: Path) -> Optional[str]:
        """
        Submit a SLURM job
        
        Args:
            slurm_script: Path to SLURM script
            
        Returns:
            Job ID if successful, None otherwise
        """
        try:
            result = subprocess.run(
                ["sbatch", str(slurm_script)],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse job ID from output like "Submitted batch job 12345"
            output = result.stdout.strip()
            if "Submitted batch job" in output:
                job_id = output.split()[-1]
                return job_id
            else:
                print(f"Warning: Unexpected sbatch output: {output}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"Error submitting job {slurm_script}: {e}")
            print(f"stderr: {e.stderr}")
            return None
        except FileNotFoundError:
            print("Error: sbatch command not found. Is SLURM installed?")
            return None
    
    def generate_and_submit_jobs(self) -> dict:
        """
        Generate SLURM scripts for all molecule pairs and optionally submit them
        
        Returns:
            Dictionary with job information
        """
        # Generate all molecule pairs
        pairs = self.generate_molecule_pairs()
        
        print(f"\nGenerating SLURM scripts...")
        print("="*80)
        
        generated_scripts = []
        submitted_jobs = []
        
        for molA, molB, pair_name in pairs:
            # Create output directory for this pair
            pair_output_dir = self.output_dir / pair_name
            pair_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate SLURM script
            slurm_script = self.generate_slurm_script(
                molA, molB, pair_name, pair_output_dir
            )
            
            generated_scripts.append({
                'pair_name': pair_name,
                'script_path': str(slurm_script),
                'molA': str(molA),
                'molB': str(molB)
            })
            
            print(f"✓ Generated: {slurm_script}")
            
            # Submit job if requested
            if self.submit_jobs:
                job_id = self.submit_slurm_job(slurm_script)
                if job_id:
                    submitted_jobs.append({
                        'pair_name': pair_name,
                        'job_id': job_id,
                        'script_path': str(slurm_script)
                    })
                    print(f"  → Submitted as job {job_id}")
                else:
                    print(f"  ✗ Failed to submit job")
                
                # Add small delay to avoid overwhelming the scheduler
                time.sleep(0.1)
        
        print("="*80)
        
        # Create summary
        summary = {
            'total_pairs': len(pairs),
            'scripts_generated': len(generated_scripts),
            'jobs_submitted': len(submitted_jobs),
            'generated_scripts': generated_scripts,
            'submitted_jobs': submitted_jobs
        }
        
        # Save summary
        import json
        summary_file = self.output_dir / 'slurm_job_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print(f"\nSummary:")
        print(f"  Total pairs: {len(pairs)}")
        print(f"  Scripts generated: {len(generated_scripts)}")
        
        if self.submit_jobs:
            print(f"  Jobs submitted: {len(submitted_jobs)}")
            if submitted_jobs:
                print(f"\nSubmitted job IDs: {', '.join(j['job_id'] for j in submitted_jobs)}")
        else:
            print(f"\nTo submit all jobs, run:")
            print(f"  find {self.output_dir} -name 'submit_job.sh' -exec sbatch {{}} \\;")
            print(f"\nOr use --submit flag to automatically submit jobs")
        
        print(f"\nSummary saved to: {summary_file}")
        print(f"SLURM logs will be saved to: {self.slurm_logs_dir}")
        
        return summary


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate and submit SLURM jobs for pairwise molecular interaction energy calculations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate SLURM scripts only (no submission)
  python batch_interaction_slurm.py molA/ molB/ results/
  
  # Generate and submit SLURM jobs
  python batch_interaction_slurm.py molA/ molB/ results/ --submit
  
  # Specify calculation parameters
  python batch_interaction_slurm.py molA/ molB/ results/ \\
      --functional M06-2X --basis def2-TZVP --partition gpu
  
  # Customize SLURM settings
  python batch_interaction_slurm.py molA/ molB/ results/ \\
      --cpus 48 --mem 50GB --partition C9654
  
  # Without molecular docking
  python batch_interaction_slurm.py molA/ molB/ results/ --no-docking
        """
    )
    
    # Required arguments
    parser.add_argument(
        'molA_dir',
        help='Directory containing molecule A structure files'
    )
    parser.add_argument(
        'molB_dir',
        help='Directory containing molecule B structure files'
    )
    parser.add_argument(
        'output_dir',
        help='Output directory for all calculation results'
    )
    
    # SLURM settings
    parser.add_argument(
        '--partition',
        default='C9654',
        help='SLURM partition name (default: C9654)'
    )
    parser.add_argument(
        '--cpus',
        type=int,
        default=96,
        dest='cpus_per_task',
        help='Number of CPU cores per task (default: 96)'
    )
    parser.add_argument(
        '--mem',
        default='100GB',
        help='Memory per job (default: 100GB)'
    )
    parser.add_argument(
        '--conda-env',
        default='meps',
        help='Conda environment name (default: meps)'
    )
    
    # Calculation parameters
    parser.add_argument(
        '--functional',
        default='B3LYP',
        choices=['B3LYP', 'M06-2X', 'wB97X-D', 'B2PLYP'],
        help='DFT functional (default: B3LYP)'
    )
    parser.add_argument(
        '--basis',
        default='6-311++G(d,p)',
        help='Basis set (default: 6-311++G(d,p))'
    )
    parser.add_argument(
        '--dispersion',
        default='GD3BJ',
        choices=['GD3', 'GD3BJ', 'None'],
        help='Dispersion correction (default: GD3BJ)'
    )
    
    # Docking settings
    parser.add_argument(
        '--no-docking',
        action='store_true',
        help='Disable molecular docking (use input structures directly)'
    )
    
    # Job submission
    parser.add_argument(
        '--submit',
        action='store_true',
        help='Automatically submit generated SLURM jobs'
    )
    
    # File discovery
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.xyz', '.pdb', '.mol', '.sdf', '.mol2'],
        help='File extensions to search for (default: .xyz .pdb .mol .sdf .mol2)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Create SLURM batch calculator
    calculator = SlurmBatchCalculator(
        molA_dir=args.molA_dir,
        molB_dir=args.molB_dir,
        output_dir=args.output_dir,
        partition=args.partition,
        cpus_per_task=args.cpus_per_task,
        mem=args.mem,
        functional=args.functional,
        basis_set=args.basis,
        dispersion=args.dispersion,
        use_docking=not args.no_docking,
        conda_env=args.conda_env,
        file_extensions=args.extensions,
        submit_jobs=args.submit
    )
    
    # Generate and optionally submit jobs
    summary = calculator.generate_and_submit_jobs()
    
    # Exit with appropriate code
    if args.submit and summary['jobs_submitted'] < summary['total_pairs']:
        print("\nWarning: Some jobs failed to submit")
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
