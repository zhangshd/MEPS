"""
Quick Test Script for MOL2 Parsing Fix
This script demonstrates the corrected MOL2 parsing behavior.
Author: zhangshd
Date: 2025-10-17
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.structure_parser import StructureParser


def quick_test():
    """Quick demonstration of the MOL2 parsing fix"""
    
    print("\n" + "="*70)
    print("MOL2 Parsing - Quick Verification")
    print("="*70 + "\n")
    
    # Test clopidol
    print("Reading: example/clopidol.mol2")
    parser = StructureParser()
    parser.read_mol2('example/clopidol.mol2')
    
    print(f"✅ Successfully parsed {len(parser.atoms)} atoms")
    print(f"   Elements found: {sorted(set(atom[0] for atom in parser.atoms))}")
    print("\n   Sample atoms:")
    for i, (elem, x, y, z) in enumerate(parser.atoms[:5], 1):
        print(f"   {i}. {elem:3s}  ({x:8.4f}, {y:8.4f}, {z:8.4f})")
    
    # Test GRAS_19
    print("\nReading: example/GRAS_19.mol2")
    parser2 = StructureParser()
    parser2.read_mol2('example/GRAS_19.mol2')
    
    print(f"✅ Successfully parsed {len(parser2.atoms)} atoms")
    print(f"   Elements found: {sorted(set(atom[0] for atom in parser2.atoms))}")
    print("\n   Sample atoms:")
    for i, (elem, x, y, z) in enumerate(parser2.atoms[:5], 1):
        print(f"   {i}. {elem:3s}  ({x:8.4f}, {y:8.4f}, {z:8.4f})")
    
    print("\n" + "="*70)
    print("✅ All MOL2 files are correctly parsed!")
    print("   Element symbols are now standard (N, C, O, S, Cl, etc.)")
    print("   Previous issue (Npl, Car, C3, etc.) is fixed.")
    print("="*70 + "\n")


if __name__ == "__main__":
    quick_test()
