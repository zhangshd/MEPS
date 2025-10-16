#!/usr/bin/env python3
"""
MOL Format Usage Example
This example demonstrates basic MOL/SDF format file operations with MEPS
Author: zhangshd
Date: 2025-10-16
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from structure_parser import StructureParser


def example_basic_operations():
    """Basic MOL file read/write operations"""
    print("\n" + "="*70)
    print("MOL Format Basic Operations")
    print("="*70)
    
    # Read XYZ and convert to MOL
    parser = StructureParser()
    xyz_file = "../data/input/water.xyz"
    parser.read_xyz(xyz_file)
    print(f"\nRead XYZ file: {xyz_file}")
    print(f"Number of atoms: {parser.get_atom_count()}")
    
    # Write to MOL format
    mol_file = "../data/output/water_example.mol"
    parser.write_mol(mol_file, mol_title="Water Molecule")
    print(f"Wrote MOL file: {mol_file}")
    
    # Read MOL file back
    parser2 = StructureParser()
    parser2.read_mol(mol_file)
    print(f"Read MOL file: {parser2.get_atom_count()} atoms")
    print(f"Charge: {parser2.charge}, Multiplicity: {parser2.multiplicity}")
    
    print("\nAtom coordinates:")
    for i, (element, x, y, z) in enumerate(parser2.atoms, 1):
        print(f"  {i}. {element:2s}  {x:10.6f}  {y:10.6f}  {z:10.6f}")


def example_format_conversion():
    """Convert between different formats"""
    print("\n" + "="*70)
    print("Format Conversion")
    print("="*70)
    
    parser = StructureParser()
    parser.read_xyz("../data/input/water.xyz")
    
    output_dir = Path("../data/output")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Convert to different formats
    formats = [
        ("XYZ", "water_conv.xyz", lambda f: parser.write_xyz(f, "Converted")),
        ("PDB", "water_conv.pdb", lambda f: parser.write_pdb(f)),
        ("MOL", "water_conv.mol", lambda f: parser.write_mol(f, "Water")),
    ]
    
    print("\nConverting water molecule:")
    for fmt_name, filename, write_func in formats:
        output_file = output_dir / filename
        write_func(str(output_file))
        file_size = output_file.stat().st_size
        print(f"  {fmt_name:4s}: {filename:20s} ({file_size} bytes)")


def example_pipeline_usage():
    """Show how to use MOL files with the pipeline"""
    print("\n" + "="*70)
    print("Pipeline Usage with MOL Files")
    print("="*70)
    
    print("\nTo use MOL files in calculations:")
    print("""
from src.gaussian_runner import InteractionEnergyPipeline

pipeline = InteractionEnergyPipeline(
    gaussian_root="/opt/share/gaussian/g16",
    work_dir="./calculations"
)

# Use MOL format files
results = pipeline.run_full_pipeline(
    molecule_a_file="molecule_a.mol",
    molecule_b_file="molecule_b.mol",
    name_a="mol_a",
    name_b="mol_b"
)
    """)
    
    print("\nSupported formats: .xyz, .pdb, .mol, .sdf")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("MEPS MOL Format Examples")
    print("="*70)
    
    try:
        example_basic_operations()
        example_format_conversion()
        example_pipeline_usage()
        
        print("\n" + "="*70)
        print("All examples completed!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
