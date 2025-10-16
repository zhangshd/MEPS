#!/usr/bin/env python3
"""
MEPS Main Pipeline Script - Automated Molecular Interaction Energy Calculation
Author: zhangshd
Date: 2025-10-16

Usage examples:
    python run_pipeline.py molecule_a.xyz molecule_b.xyz --name_a benzene --name_b methane
    python run_pipeline.py molecule_a.mol molecule_b.mol --name_a mol_a --name_b mol_b
"""

import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gaussian_runner import InteractionEnergyPipeline


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Automated Molecular Interaction Energy Calculation Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python run_pipeline.py molecule_a.xyz molecule_b.xyz
  
  # Specify molecule names
  python run_pipeline.py benzene.xyz methane.xyz --name_a benzene --name_b methane
  
  # Using MOL format files
  python run_pipeline.py benzene.mol methane.mol --name_a benzene --name_b methane
  
  # Custom calculation parameters
  python run_pipeline.py mol_a.pdb mol_b.pdb --functional M06-2X --basis def2-TZVP
  
  # Without molecular docking
  python run_pipeline.py mol_a.xyz mol_b.xyz --no-docking
        """
    )
    
    # Required arguments
    parser.add_argument(
        'molecule_a',
        help='Structure file for molecule A (supports .xyz, .pdb, .mol, .sdf formats)'
    )
    parser.add_argument(
        'molecule_b',
        help='Structure file for molecule B (supports .xyz, .pdb, .mol, .sdf formats)'
    )
    
    # Optional arguments - Molecule information
    parser.add_argument(
        '--name_a',
        default='molecule_a',
        help='Name for molecule A (default: molecule_a)'
    )
    parser.add_argument(
        '--name_b',
        default='molecule_b',
        help='Name for molecule B (default: molecule_b)'
    )
    
    # Optional arguments - Calculation settings
    parser.add_argument(
        '--functional',
        default='B3LYP',
        choices=['B3LYP', 'M06-2X', 'wB97X-D', 'B2PLYP'],
        help='Density functional theory method (default: B3LYP)'
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
        help='Dispersion correction method (default: GD3BJ)'
    )
    
    # Optional arguments - Computational resources
    parser.add_argument(
        '--mem',
        default='100GB',
        help='Memory for Gaussian calculation (default: 100GB)'
    )
    parser.add_argument(
        '--nproc',
        type=int,
        default=96,
        help='Number of CPU cores for Gaussian (default: 96)'
    )
    
    # Optional arguments - Docking settings
    parser.add_argument(
        '--no-docking',
        action='store_true',
        help='Skip AutoDock Vina docking, use optimized monomers directly'
    )
    parser.add_argument(
        '--exhaustiveness',
        type=int,
        default=8,
        help='Vina docking search accuracy (default: 8)'
    )
    
    # Optional arguments - Path settings
    parser.add_argument(
        '--gaussian_root',
        default='/opt/share/gaussian/g16',
        help='Gaussian installation root directory (default: /opt/share/gaussian/g16)'
    )
    parser.add_argument(
        '--work_dir',
        default='./meps_calculations',
        help='Working directory (default: ./meps_calculations)'
    )
    
    return parser.parse_args()


def main():
    """Main function"""
    # Parse arguments
    args = parse_arguments()
    
    # Check if input files exist
    if not os.path.exists(args.molecule_a):
        print(f"Error: Cannot find file for molecule A: {args.molecule_a}")
        sys.exit(1)
    
    if not os.path.exists(args.molecule_b):
        print(f"Error: Cannot find file for molecule B: {args.molecule_b}")
        sys.exit(1)
    
    # Process dispersion correction parameter
    dispersion = args.dispersion if args.dispersion != 'None' else ''
    
    # Initialize pipeline manager
    try:
        pipeline = InteractionEnergyPipeline(
            gaussian_root=args.gaussian_root,
            work_dir=args.work_dir
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please check if Gaussian is correctly installed and the path is correct")
        sys.exit(1)
    
    # Run full pipeline
    try:
        results = pipeline.run_full_pipeline(
            molecule_a_file=args.molecule_a,
            molecule_b_file=args.molecule_b,
            name_a=args.name_a,
            name_b=args.name_b,
            functional=args.functional,
            basis_set=args.basis,
            dispersion=dispersion,
            mem=args.mem,
            nproc=args.nproc,
            use_docking=not args.no_docking,
            docking_exhaustiveness=args.exhaustiveness
        )
        
        # Print final results summary
        print("\n" + "="*80)
        print("Calculation Results Summary")
        print("="*80)
        print(f"Molecular pair: {args.name_a} + {args.name_b}")
        print(f"Theory level: {args.functional}/{args.basis}")
        if dispersion:
            print(f"Dispersion correction: {dispersion}")
        print("-"*80)
        
        if results['complexation_energy_corrected'] is not None:
            print(f"\nInteraction energy (BSSE-corrected): {results['complexation_energy_corrected']:.2f} kcal/mol")
            print(f"Interaction energy (uncorrected):    {results['complexation_energy_raw']:.2f} kcal/mol")
            print(f"BSSE energy:                         {results['bsse_energy']:.6f} Hartree")
            print(f"                                     {results['bsse_energy'] * 627.509:.2f} kcal/mol")
            
            # Classify interaction type
            energy = results['complexation_energy_corrected']
            if energy < -5:
                interaction_type = "Strong attractive interaction"
            elif energy < -2:
                interaction_type = "Moderate attractive interaction"
            elif energy < 0:
                interaction_type = "Weak attractive interaction"
            else:
                interaction_type = "Repulsive interaction"
            
            print(f"\nInteraction type: {interaction_type}")
            
            # BSSE assessment
            bsse_kcal = abs(results['bsse_energy'] * 627.509)
            if bsse_kcal > 3:
                print(f"\n⚠️  Warning: Large BSSE ({bsse_kcal:.2f} kcal/mol)")
                print("   Recommend using a larger basis set for more reliable results")
            elif bsse_kcal > 2:
                print(f"\nNote: Moderate BSSE ({bsse_kcal:.2f} kcal/mol)")
                print("   Results are reasonably reliable, but a larger basis set may be better")
            else:
                print(f"\n✓ Small BSSE ({bsse_kcal:.2f} kcal/mol), results are reliable")
        else:
            print("\n⚠️  Warning: Unable to extract interaction energy results")
            print("   Please check the calculation log files")
        
        print("\nDetailed results saved to:")
        print(f"  Text report: {args.work_dir}/results/interaction_energy_results.txt")
        print(f"  JSON data: {args.work_dir}/results/interaction_energy_results.json")
        print("="*80)
        
    except Exception as e:
        print(f"\nError: Exception occurred during calculation")
        print(f"Details: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
