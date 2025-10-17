#!/usr/bin/env python3
"""
Batch Interaction Energy Calculation Script
This script calculates pairwise interaction energies for all molecules 
from two input folders using parallel processing.
Author: zhangshd
Date: 2025-10-16
"""

import sys
import os
import argparse
import multiprocessing as mp
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import time
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gaussian_runner import InteractionEnergyPipeline


class BatchInteractionCalculator:
    """Batch calculator for pairwise molecular interaction energies"""
    
    def __init__(
        self,
        molA_dir: str,
        molB_dir: str,
        output_dir: str,
        gaussian_root: str = "/opt/share/gaussian/g16",
        nproc_per_job: int = 96,
        max_parallel_jobs: Optional[int] = None,
        functional: str = "B3LYP",
        basis_set: str = "6-311++G(d,p)",
        dispersion: str = "GD3BJ",
        mem: str = "100GB",
        use_docking: bool = True,
        file_extensions: List[str] = None
    ):
        """
        Initialize batch calculator
        
        Args:
            molA_dir: Directory containing molecule A files
            molB_dir: Directory containing molecule B files
            output_dir: Output directory for all calculations
            gaussian_root: Gaussian installation root directory
            nproc_per_job: Number of CPU cores per Gaussian job
            max_parallel_jobs: Maximum parallel jobs (auto-detect if None)
            functional: DFT functional
            basis_set: Basis set
            dispersion: Dispersion correction
            mem: Memory per job
            use_docking: Whether to use molecular docking
            file_extensions: Supported file extensions (default: xyz, pdb, mol, sdf, mol2)
        """
        self.molA_dir = Path(molA_dir)
        self.molB_dir = Path(molB_dir)
        self.output_dir = Path(output_dir)
        self.gaussian_root = gaussian_root
        self.nproc_per_job = nproc_per_job
        self.functional = functional
        self.basis_set = basis_set
        self.dispersion = dispersion
        self.mem = mem
        self.use_docking = use_docking
        
        # Supported file extensions
        if file_extensions is None:
            self.file_extensions = ['.xyz', '.pdb', '.mol', '.sdf', '.mol2']
        else:
            self.file_extensions = file_extensions
        
        # Auto-detect max parallel jobs based on available CPUs
        total_cpus = mp.cpu_count()
        if max_parallel_jobs is None:
            self.max_parallel_jobs = max(1, total_cpus // nproc_per_job)
        else:
            self.max_parallel_jobs = max_parallel_jobs
        
        # Validate directories
        if not self.molA_dir.exists():
            raise FileNotFoundError(f"Molecule A directory not found: {molA_dir}")
        if not self.molB_dir.exists():
            raise FileNotFoundError(f"Molecule B directory not found: {molB_dir}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Batch Calculator Configuration:")
        print(f"  Total CPUs: {total_cpus}")
        print(f"  CPUs per job: {nproc_per_job}")
        print(f"  Max parallel jobs: {self.max_parallel_jobs}")
        print(f"  Output directory: {self.output_dir}")
    
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
    
    def calculate_single_pair(
        self,
        args: Tuple[Path, Path, str, int]
    ) -> Tuple[str, bool, Optional[str], Optional[Dict]]:
        """
        Calculate interaction energy for a single molecule pair
        
        Args:
            args: Tuple of (molA_file, molB_file, pair_name, job_id)
            
        Returns:
            Tuple of (pair_name, success, error_message, results)
        """
        molA_file, molB_file, pair_name, job_id = args
        
        start_time = time.time()
        print(f"[Job {job_id}] Starting: {pair_name}")
        
        # Create output directory for this pair
        pair_output_dir = self.output_dir / pair_name
        pair_output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize pipeline
            pipeline = InteractionEnergyPipeline(
                gaussian_root=self.gaussian_root,
                work_dir=str(pair_output_dir)
            )
            
            # Run calculation
            results = pipeline.run_full_pipeline(
                molecule_a_file=str(molA_file),
                molecule_b_file=str(molB_file),
                name_a=molA_file.stem,
                name_b=molB_file.stem,
                functional=self.functional,
                basis_set=self.basis_set,
                dispersion=self.dispersion,
                mem=self.mem,
                nproc=self.nproc_per_job,
                use_docking=self.use_docking
            )
            
            elapsed_time = time.time() - start_time
            print(f"[Job {job_id}] Completed: {pair_name} ({elapsed_time:.1f}s)")
            
            # Add metadata to results
            results['pair_name'] = pair_name
            results['molA_file'] = str(molA_file)
            results['molB_file'] = str(molB_file)
            results['calculation_time'] = elapsed_time
            
            return pair_name, True, None, results
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"[Job {job_id}] FAILED: {pair_name} ({elapsed_time:.1f}s) - {error_msg}")
            return pair_name, False, error_msg, None
    
    def run_batch_calculation(self) -> Dict:
        """
        Run batch calculation for all molecule pairs
        
        Returns:
            Summary dictionary with all results
        """
        # Generate all molecule pairs
        pairs = self.generate_molecule_pairs()
        
        # Prepare arguments for parallel processing
        job_args = [
            (molA, molB, pair_name, i+1)
            for i, (molA, molB, pair_name) in enumerate(pairs)
        ]
        
        # Run calculations in parallel
        print(f"\nStarting batch calculations with {self.max_parallel_jobs} parallel jobs...")
        print("="*80)
        
        batch_start_time = time.time()
        
        with mp.Pool(processes=self.max_parallel_jobs) as pool:
            results = pool.map(self.calculate_single_pair, job_args)
        
        batch_elapsed_time = time.time() - batch_start_time
        
        # Process results
        successful = []
        failed = []
        
        for pair_name, success, error_msg, result_data in results:
            if success:
                successful.append({
                    'pair_name': pair_name,
                    'results': result_data
                })
            else:
                failed.append({
                    'pair_name': pair_name,
                    'error': error_msg
                })
        
        # Create summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'molA_dir': str(self.molA_dir),
                'molB_dir': str(self.molB_dir),
                'output_dir': str(self.output_dir),
                'functional': self.functional,
                'basis_set': self.basis_set,
                'dispersion': self.dispersion,
                'nproc_per_job': self.nproc_per_job,
                'max_parallel_jobs': self.max_parallel_jobs,
                'use_docking': self.use_docking
            },
            'statistics': {
                'total_pairs': len(pairs),
                'successful': len(successful),
                'failed': len(failed),
                'total_time_seconds': batch_elapsed_time,
                'average_time_per_pair': batch_elapsed_time / len(pairs) if pairs else 0
            },
            'successful_calculations': successful,
            'failed_calculations': failed
        }
        
        # Save summary
        summary_file = self.output_dir / 'batch_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("="*80)
        print(f"\nBatch Calculation Summary:")
        print(f"  Total pairs: {len(pairs)}")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        print(f"  Total time: {batch_elapsed_time:.1f}s ({batch_elapsed_time/60:.1f}min)")
        print(f"  Average time per pair: {batch_elapsed_time/len(pairs):.1f}s")
        print(f"\nResults saved to: {self.output_dir}")
        print(f"Summary file: {summary_file}")
        
        if failed:
            print(f"\nFailed calculations:")
            for item in failed:
                print(f"  - {item['pair_name']}: {item['error']}")
        
        return summary


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Batch calculation of pairwise molecular interaction energies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python batch_interaction_energy.py molA/ molB/ results/
  
  # Specify calculation parameters
  python batch_interaction_energy.py molA/ molB/ results/ --functional M06-2X --basis def2-TZVP
  
  # Control parallel execution
  python batch_interaction_energy.py molA/ molB/ results/ --nproc 48 --max-jobs 4
  
  # Without molecular docking
  python batch_interaction_energy.py molA/ molB/ results/ --no-docking
  
  # Specify file types
  python batch_interaction_energy.py molA/ molB/ results/ --extensions .xyz .mol
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
    
    # Computational resources
    parser.add_argument(
        '--nproc',
        type=int,
        default=96,
        help='Number of CPU cores per Gaussian job (default: 96)'
    )
    parser.add_argument(
        '--max-jobs',
        type=int,
        default=None,
        help='Maximum parallel jobs (default: auto-detect based on total CPUs)'
    )
    parser.add_argument(
        '--mem',
        default='100GB',
        help='Memory per Gaussian job (default: 100GB)'
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
    
    # Gaussian settings
    parser.add_argument(
        '--gaussian-root',
        default='/opt/share/gaussian/g16',
        help='Gaussian installation root directory (default: /opt/share/gaussian/g16)'
    )
    
    # Docking settings
    parser.add_argument(
        '--no-docking',
        action='store_true',
        help='Disable molecular docking (use input structures directly)'
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
    
    # Create batch calculator
    calculator = BatchInteractionCalculator(
        molA_dir=args.molA_dir,
        molB_dir=args.molB_dir,
        output_dir=args.output_dir,
        gaussian_root=args.gaussian_root,
        nproc_per_job=args.nproc,
        max_parallel_jobs=args.max_jobs,
        functional=args.functional,
        basis_set=args.basis,
        dispersion=args.dispersion,
        mem=args.mem,
        use_docking=not args.no_docking,
        file_extensions=args.extensions
    )
    
    # Run batch calculation
    summary = calculator.run_batch_calculation()
    
    # Exit with appropriate code
    if summary['statistics']['failed'] > 0:
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
