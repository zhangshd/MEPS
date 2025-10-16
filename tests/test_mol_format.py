#!/usr/bin/env python3
"""
Test MOL/MOL2 Format Support
This script tests the MOL/SDF/MOL2 file reading and writing functionality
Author: zhangshd
Date: 2025-10-16
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from structure_parser import StructureParser


def test_read_write_mol():
    """Test reading XYZ and writing to MOL format"""
    print("="*70)
    print("Test 1: Read XYZ and Write MOL")
    print("="*70)
    
    input_dir = Path(__file__).parent.parent / 'data' / 'input'
    output_dir = Path(__file__).parent / 'test_output'
    output_dir.mkdir(exist_ok=True)
    
    water_xyz = input_dir / 'water.xyz'
    
    if not water_xyz.exists():
        print(f"Warning: {water_xyz} not found, skipping this test")
        return
    
    parser = StructureParser()
    parser.read_xyz(str(water_xyz))
    print(f"Read {parser.get_atom_count()} atoms from {water_xyz}")
    
    output_mol = output_dir / 'water.mol'
    parser.write_mol(str(output_mol), mol_title="Water Molecule")
    print(f"Successfully wrote MOL file: {output_mol}")
    
    if output_mol.exists():
        print(f"MOL file created successfully: {output_mol}")
        with open(output_mol, 'r') as f:
            print("\nFirst 15 lines of MOL file:")
            for i, line in enumerate(f):
                if i >= 15:
                    break
                print(line.rstrip())
    
    print("\n")


def test_read_mol_file():
    """Test reading MOL file if one exists"""
    print("="*70)
    print("Test 2: Read MOL File")
    print("="*70)
    
    output_dir = Path(__file__).parent / 'test_output'
    water_mol = output_dir / 'water.mol'
    
    if not water_mol.exists():
        print(f"Warning: {water_mol} not found, run test 1 first")
        return
    
    parser = StructureParser()
    parser.read_mol(str(water_mol))
    print(f"Successfully read MOL file: {water_mol}")
    print(f"Number of atoms: {parser.get_atom_count()}")
    print(f"Charge: {parser.charge}")
    print(f"Multiplicity: {parser.multiplicity}")
    
    print("\nAtom coordinates:")
    for i, (element, x, y, z) in enumerate(parser.atoms, 1):
        print(f"  Atom {i}: {element:2s}  {x:12.6f}  {y:12.6f}  {z:12.6f}")
    
    print("\n")


def test_mol_xyz_roundtrip():
    """Test XYZ -> MOL -> XYZ conversion"""
    print("="*70)
    print("Test 3: XYZ -> MOL -> XYZ Roundtrip")
    print("="*70)
    
    input_dir = Path(__file__).parent.parent / 'data' / 'input'
    output_dir = Path(__file__).parent / 'test_output'
    output_dir.mkdir(exist_ok=True)
    
    methane_xyz = input_dir / 'methane.xyz'
    
    if not methane_xyz.exists():
        print(f"Warning: {methane_xyz} not found, skipping this test")
        return
    
    parser1 = StructureParser()
    parser1.read_xyz(str(methane_xyz))
    print(f"Original XYZ: {parser1.get_atom_count()} atoms")
    
    mol_file = output_dir / 'methane.mol'
    parser1.write_mol(str(mol_file), mol_title="Methane")
    print(f"Converted to MOL: {mol_file}")
    
    parser2 = StructureParser()
    parser2.read_mol(str(mol_file))
    print(f"Read back from MOL: {parser2.get_atom_count()} atoms")
    
    xyz_file = output_dir / 'methane_from_mol.xyz'
    parser2.write_xyz(str(xyz_file), comment="Converted from MOL")
    print(f"Converted back to XYZ: {xyz_file}")
    
    if parser1.get_atom_count() == parser2.get_atom_count():
        print("\nRoundtrip conversion successful!")
        print(f"Atom count matches: {parser1.get_atom_count()}")
    else:
        print("\nWarning: Atom count mismatch!")
        print(f"Original: {parser1.get_atom_count()}, After roundtrip: {parser2.get_atom_count()}")
    
    print("\n")


def test_multiple_formats():
    """Test conversion between multiple formats"""
    print("="*70)
    print("Test 4: Multiple Format Conversions")
    print("="*70)
    
    input_dir = Path(__file__).parent.parent / 'data' / 'input'
    output_dir = Path(__file__).parent / 'test_output'
    output_dir.mkdir(exist_ok=True)
    
    water_xyz = input_dir / 'water.xyz'
    
    if not water_xyz.exists():
        print(f"Warning: {water_xyz} not found, skipping this test")
        return
    
    parser = StructureParser()
    parser.read_xyz(str(water_xyz))
    
    formats = [
        ('xyz', 'water_copy.xyz', lambda f: parser.write_xyz(f, "Test water")),
        ('pdb', 'water.pdb', lambda f: parser.write_pdb(f)),
        ('mol', 'water_v2.mol', lambda f: parser.write_mol(f, "Water")),
    ]
    
    print(f"Converting water molecule to multiple formats:")
    for fmt_name, filename, write_func in formats:
        output_file = output_dir / filename
        write_func(str(output_file))
        file_size = output_file.stat().st_size
        print(f"  {fmt_name.upper():4s}: {filename:20s} ({file_size} bytes)")
    
    print("\n")


def test_mol2_format():
    """Test MOL2 format reading and writing"""
    print("="*70)
    print("Test 5: MOL2 Format Support")
    print("="*70)
    
    input_dir = Path(__file__).parent.parent / 'data' / 'input'
    output_dir = Path(__file__).parent / 'test_output'
    output_dir.mkdir(exist_ok=True)
    
    water_xyz = input_dir / 'water.xyz'
    
    if not water_xyz.exists():
        print(f"Warning: {water_xyz} not found, skipping this test")
        return
    
    # Read XYZ and write to MOL2
    parser = StructureParser()
    parser.read_xyz(str(water_xyz))
    print(f"Read XYZ: {parser.get_atom_count()} atoms")
    
    mol2_file = output_dir / 'water.mol2'
    parser.write_mol2(str(mol2_file), mol_title="Water Molecule")
    print(f"Wrote MOL2: {mol2_file}")
    
    # Read MOL2 back
    parser2 = StructureParser()
    parser2.read_mol2(str(mol2_file))
    print(f"Read MOL2 back: {parser2.get_atom_count()} atoms")
    
    # Verify
    if parser.get_atom_count() == parser2.get_atom_count():
        print(f"✓ MOL2 roundtrip successful! Atom count: {parser.get_atom_count()}")
    else:
        print(f"✗ Atom count mismatch!")
    
    print("\n")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MOL/MOL2 Format Support Tests")
    print("="*70 + "\n")
    
    try:
        test_read_write_mol()
        test_read_mol_file()
        test_mol_xyz_roundtrip()
        test_multiple_formats()
        test_mol2_format()
        
        print("="*70)
        print("All tests completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
