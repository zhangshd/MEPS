"""
MOL2 Parsing Fix Verification Test
This script verifies that MOL2 files are correctly parsed with proper element symbols.
Author: zhangshd
Date: 2025-10-17
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.structure_parser import StructureParser
from src.gaussian_io import GaussianInputGenerator


def test_mol2_element_extraction():
    """Test that MOL2 files extract correct element symbols"""
    
    print("="*70)
    print("MOL2 Parsing Fix Verification Test")
    print("="*70)
    
    test_files = [
        ('example/clopidol.mol2', 'clopidol'),
        ('example/GRAS_19.mol2', 'GRAS_19')
    ]
    
    all_passed = True
    
    for mol2_file, name in test_files:
        print(f"\n{'='*70}")
        print(f"Testing: {name}")
        print(f"File: {mol2_file}")
        print("="*70)
        
        parser = StructureParser()
        parser.read_mol2(mol2_file)
        
        print(f"\nTotal atoms: {len(parser.atoms)}")
        print("\nFirst 10 atoms:")
        print(f"{'#':<4} {'Element':<8} {'X':<12} {'Y':<12} {'Z':<12}")
        print("-"*60)
        
        for i, (element, x, y, z) in enumerate(parser.atoms[:10], 1):
            print(f"{i:<4} {element:<8} {x:<12.6f} {y:<12.6f} {z:<12.6f}")
            
            if '.' in element or element[0].islower():
                print(f"  ❌ ERROR: Invalid element symbol '{element}'")
                all_passed = False
            elif len(element) > 2:
                print(f"  ❌ ERROR: Element symbol too long '{element}'")
                all_passed = False
            elif not element[0].isupper():
                print(f"  ❌ ERROR: Element symbol must start with uppercase '{element}'")
                all_passed = False
        
        valid_elements = {'H', 'C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I'}
        elements_in_file = set(atom[0] for atom in parser.atoms)
        
        print(f"\nUnique elements found: {sorted(elements_in_file)}")
        
        invalid_elements = elements_in_file - valid_elements
        if invalid_elements:
            print(f"❌ Invalid elements detected: {invalid_elements}")
            all_passed = False
        else:
            print("✅ All elements are valid")
        
        print("\nGenerating test Gaussian input file...")
        generator = GaussianInputGenerator()
        test_gjf = f'/tmp/test_{name}_parsing.gjf'
        generator.generate_optimization_input(
            structure=parser,
            output_file=test_gjf,
            checkpoint_file=f'{name}.chk',
            job_title=f'{name} Test',
            mem='4GB',
            nproc=4
        )
        
        with open(test_gjf, 'r') as f:
            lines = f.readlines()
        
        print(f"Created: {test_gjf}")
        print("\nCoordinate section from generated file:")
        coord_started = False
        for line in lines:
            if coord_started:
                if line.strip() == '':
                    break
                element = line.split()[0]
                if '.' in element or element[0].islower():
                    print(f"  ❌ {line.strip()} (Invalid element)")
                    all_passed = False
                else:
                    print(f"  ✅ {line.strip()}")
            elif line.strip().startswith('0 1') or line.strip().startswith('0 2'):
                coord_started = True
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("MOL2 files are correctly parsed with proper element symbols")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please check the errors above")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = test_mol2_element_extraction()
    sys.exit(0 if success else 1)
