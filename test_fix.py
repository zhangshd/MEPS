"""
Test script to verify the docking and complex structure extraction fix
Author: zhangshd
Date: 2025-10-17
"""

import sys
sys.path.insert(0, '/home/zhangsd/repos/MEPS/src')

from structure_parser import StructureParser
from vina_docking import VinaDocking

# Read the two molecules
struct_a = StructureParser()
struct_a.read_mol2('example/clopidol.mol2')

struct_b = StructureParser()
struct_b.read_mol2('example/GRAS_19.mol2')

print(f"Molecule A: {struct_a.get_atom_count()} atoms")
print(f"Molecule B: {struct_b.get_atom_count()} atoms")

# Run docking
docking = VinaDocking(work_dir="./test_docking")
complex_struct, results = docking.dock_two_molecules(
    struct_a,
    struct_b,
    exhaustiveness=8,
    padding=10.0
)

print(f"\nDocking results:")
print(f"  Best affinity: {results['best_affinity']} kcal/mol")
print(f"  Complex structure: {complex_struct.get_atom_count()} atoms")

# Extract fragments from complex
n_atoms_a = struct_a.get_atom_count()
n_atoms_b = struct_b.get_atom_count()

frag_a = StructureParser()
frag_a.atoms = complex_struct.atoms[:n_atoms_a]
frag_a.charge = struct_a.charge
frag_a.multiplicity = struct_a.multiplicity

frag_b = StructureParser()
frag_b.atoms = complex_struct.atoms[n_atoms_a:]
frag_b.charge = struct_b.charge
frag_b.multiplicity = struct_b.multiplicity

print(f"\nExtracted fragments:")
print(f"  Fragment A: {len(frag_a.atoms)} atoms")
print(f"  Fragment B: {len(frag_b.atoms)} atoms")

# Check coordinates - first few atoms of each fragment
print(f"\nFragment A coordinates (first 3 atoms):")
for i in range(min(3, len(frag_a.atoms))):
    elem, x, y, z = frag_a.atoms[i]
    print(f"  {i+1}. {elem:2s}: ({x:8.3f}, {y:8.3f}, {z:8.3f})")

print(f"\nFragment B coordinates (first 3 atoms):")
for i in range(min(3, len(frag_b.atoms))):
    elem, x, y, z = frag_b.atoms[i]
    print(f"  {i+1}. {elem:2s}: ({x:8.3f}, {y:8.3f}, {z:8.3f})")

# Check if there are any overlapping atoms
is_valid, problematic_pairs = complex_struct.check_atom_distances(min_distance=0.5)

if is_valid:
    print(f"\n✓ No atom overlaps detected (all distances >= 0.5 A)")
else:
    print(f"\n✗ Warning: Found {len(problematic_pairs)} atom pair(s) with distance < 0.5 A")
    for i, j, dist in problematic_pairs[:5]:
        print(f"  Atoms {i+1}-{j+1}: {dist:.3f} A")
