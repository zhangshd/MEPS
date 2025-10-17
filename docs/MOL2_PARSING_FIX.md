# MOL2 Parsing Bug Fix

## Problem Description

When parsing MOL2 files, the original code was writing incorrect atom type labels (e.g., `Nar`, `Car`, `C3`, `O3`, `Npl`) into Gaussian input files instead of standard element symbols (e.g., `N`, `C`, `O`). This caused Gaussian to fail to recognize the atoms.

## Root Cause

The bug was in the `structure_parser.py` file, where the code used `atom.GetType()` to extract atom information from MOL2 files:

```python
# INCORRECT - GetType() returns MOL2 atom types
element = atom.GetType()  # Returns: N.ar, C.ar, C.3, O.3, N.pl3, S.3, etc.
```

In MOL2 format, atom types include hybridization and chemical environment information:
- `N.ar` = aromatic nitrogen
- `C.ar` = aromatic carbon  
- `C.3` = sp³ hybridized carbon
- `C.2` = sp² hybridized carbon
- `N.pl3` = planar trigonal nitrogen
- `O.3` = sp³ oxygen
- `S.3` = sp³ sulfur

These atom types are useful for force field calculations but are NOT valid element symbols for quantum chemistry programs like Gaussian.

## Solution

Changed the code to use `ob.GetSymbol(atom.GetAtomicNum())` which correctly extracts the element symbol:

```python
# CORRECT - GetSymbol() with GetAtomicNum() returns element symbols
element = ob.GetSymbol(atom.GetAtomicNum())  # Returns: N, C, O, S, etc.
```

## Files Modified

- `src/structure_parser.py`:
  - Fixed `_read_mol_openbabel()` method (line ~122)
  - Fixed `read_mol2()` method (line ~195)

## Verification

### Before Fix (clopidol.gjf):
```
 Nar      -0.050900       0.051700       0.012900
 Car      -1.389700       0.000000      -0.008000
 C3      -1.989300      -1.374700       0.060200
 O3      -2.269900       3.525600      -0.226000
```

### After Fix (clopidol_fixed.gjf):
```
 N       -0.050900       0.051700       0.012900
 C       -1.389700       0.000000      -0.008000
 C       -1.989300      -1.374700       0.060200
 O       -2.269900       3.525600      -0.226000
```

### Before Fix (GRAS_19.gjf):
```
 C3       0.030200       0.040100       0.094500
 C2       1.375100       0.006000      -0.570500
 O2       2.091500      -0.969900      -0.390500
 S3       1.631200       3.493800      -2.746300
 Npl       3.119200       0.935000      -1.817900
```

### After Fix (GRAS_19_fixed.gjf):
```
 C        0.030200       0.040100       0.094500
 C        1.375100       0.006000      -0.570500
 O        2.091500      -0.969900      -0.390500
 S        1.631200       3.493800      -2.746300
 N        3.119200       0.935000      -1.817900
```

## Impact

- ✅ Gaussian input files now contain valid element symbols
- ✅ All MOL2 files can be correctly parsed and converted
- ✅ The fix also applies to MOL format files read via OpenBabel
- ✅ Coordinates remain unchanged, only element symbols are corrected

## Testing

Run the following command to verify the fix:

```bash
conda run -n meps python3 -c "
from src.structure_parser import StructureParser

# Test MOL2 parsing
parser = StructureParser()
parser.read_mol2('example/clopidol.mol2')
print('First 5 atoms:')
for atom in parser.atoms[:5]:
    print(f'  {atom[0]:3s} {atom[1]:10.4f} {atom[2]:10.4f} {atom[3]:10.4f}')
"
```

Expected output:
```
First 5 atoms:
  N        -0.0509     0.0517     0.0129
  C        -1.3897     0.0000    -0.0080
  C        -1.9893    -1.3747     0.0602
  C        -2.1302     1.1556    -0.0875
  C        -1.4975     2.3972    -0.1475
```

## Related Files

- Original problematic files:
  - `meps_calculations/monomers/clopidol.gjf`
  - `meps_calculations/monomers/GRAS_19.gjf`

- Fixed files (for comparison):
  - `meps_calculations/monomers/clopidol_fixed.gjf`
  - `meps_calculations/monomers/GRAS_19_fixed.gjf`

## Date
October 17, 2025
