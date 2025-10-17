"""
Parallel Optimization Example
Demonstrates the improved parallel monomer optimization feature
Author: zhangshd
Date: 2025-10-17
"""

from src.gaussian_runner import InteractionEnergyPipeline
from src.structure_parser import StructureParser

def main():
    """
    Example: Calculate interaction energy with parallel monomer optimization
    """
    
    # Initialize pipeline
    pipeline = InteractionEnergyPipeline(
        gaussian_root="/opt/share/gaussian/g16",
        work_dir="./parallel_example"
    )
    
    # Example 1: Using run_full_pipeline (automatic parallel optimization)
    print("="*80)
    print("Example 1: Full pipeline with automatic parallel optimization")
    print("="*80)
    
    results = pipeline.run_full_pipeline(
        molecule_a_file="example/benzene.xyz",
        molecule_b_file="example/methane.xyz",
        name_a="benzene",
        name_b="methane",
        functional="B3LYP",
        basis_set="6-311++G(d,p)",
        dispersion="GD3BJ",
        mem="90GB",      # Adjust based on available RAM
        nproc=48,        # Use 48 cores per job (total: 96 on a dual-CPU system)
        use_docking=True,
        docking_exhaustiveness=8
    )
    
    print(f"\nInteraction energy (BSSE corrected): {results['complexation_energy_corrected']:.2f} kcal/mol")
    
    
    # Example 2: Manual control of parallel optimization
    print("\n" + "="*80)
    print("Example 2: Manual parallel optimization (advanced usage)")
    print("="*80)
    
    # Read structures
    struct_a = StructureParser()
    struct_a.read_xyz("example/benzene.xyz")
    
    struct_b = StructureParser()
    struct_b.read_xyz("example/methane.xyz")
    
    # Optimize both monomers in parallel
    monomer_files = pipeline.optimize_monomers_parallel(
        structures=[
            (struct_a, "benzene"),
            (struct_b, "methane")
        ],
        functional="B3LYP",
        basis_set="6-311++G(d,p)",
        dispersion="GD3BJ",
        mem="90GB",
        nproc=48
    )
    
    print(f"\nOptimized {len(monomer_files)} monomers in parallel")
    for files in monomer_files:
        print(f"  - {files['name']}: {files['log']}")
    
    
    # Example 3: Extend to more than 2 molecules
    print("\n" + "="*80)
    print("Example 3: Optimize multiple molecules in parallel")
    print("="*80)
    
    # Prepare multiple structures
    structures_to_optimize = []
    
    molecule_files = [
        ("example/benzene.xyz", "benzene"),
        ("example/methane.xyz", "methane"),
        ("data/input/water.xyz", "water")
    ]
    
    for mol_file, mol_name in molecule_files:
        struct = StructureParser()
        struct.read_xyz(mol_file)
        structures_to_optimize.append((struct, mol_name))
    
    # Optimize all at once (adjust nproc accordingly!)
    # For 3 molecules with nproc=32 each, you need 96 total cores
    all_optimized = pipeline.optimize_monomers_parallel(
        structures=structures_to_optimize,
        functional="B3LYP",
        basis_set="6-31G(d)",  # Smaller basis for demo
        mem="30GB",            # 30GB per job
        nproc=32               # 32 cores per job
    )
    
    print(f"\nSuccessfully optimized {len(all_optimized)} molecules in parallel!")


if __name__ == "__main__":
    main()
