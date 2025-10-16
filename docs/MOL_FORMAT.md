# MOL Format Support

## Overview

MEPS supports MOL/SDF/MOL2 molecular structure formats for input and output.

## Supported Formats

| Format | Extension | Read | Write | Library |
|--------|-----------|------|-------|---------|
| XYZ | .xyz | ✓ | ✓ | Built-in |
| PDB | .pdb | ✓ | ✓ | Built-in |
| MOL | .mol | ✓ | ✓ | OpenBabel/RDKit |
| SDF | .sdf | ✓ | ✓ | OpenBabel/RDKit |
| MOL2 | .mol2 | ✓ | ✓ | OpenBabel |
| Gaussian | .log, .out | ✓ | - | Built-in |

## Usage

### Basic Reading and Writing

```python
from src.structure_parser import StructureParser

# Read MOL file
parser = StructureParser()
parser.read_mol("molecule.mol")

# Read MOL2 file
parser.read_mol2("molecule.mol2")

# Write MOL file
parser.write_mol("output.mol", mol_title="My Molecule")

# Write MOL2 file
parser.write_mol2("output.mol2", mol_title="My Molecule")

# Format conversion
parser.read_xyz("input.xyz")
parser.write_mol2("output.mol2")
```

### Pipeline Integration

```python
from src.gaussian_runner import InteractionEnergyPipeline

pipeline = InteractionEnergyPipeline(
    gaussian_root="/opt/share/gaussian/g16",
    work_dir="./calculations"
)

# Use MOL/MOL2 files directly
results = pipeline.run_full_pipeline(
    molecule_a_file="benzene.mol2",
    molecule_b_file="methane.mol2",
    name_a="benzene",
    name_b="methane"
)
```

### Command Line

```bash
# Basic usage
python scripts/run_pipeline.py molecule_a.mol2 molecule_b.mol2

# With parameters
python scripts/run_pipeline.py benzene.mol2 methane.mol2 \
    --name_a benzene --name_b methane \
    --functional M06-2X --basis def2-TZVP

# View help
python scripts/run_pipeline.py --help
```

## API Reference

### StructureParser Methods

**`read_mol(filepath: str)`**
- Read MOL/SDF format files
- Supports both OpenBabel and RDKit
- Extracts atomic coordinates, charge, and multiplicity

**`write_mol(filepath: str, mol_title: str = "Molecule")`**
- Write MOL format files (V2000 format)
- Requires OpenBabel or RDKit

**`read_mol2(filepath: str)`**
- Read MOL2 (Tripos) format files
- Requires OpenBabel
- Includes atom types and bond information

**`write_mol2(filepath: str, mol_title: str = "Molecule")`**
- Write MOL2 format files
- Requires OpenBabel
- Includes basic connectivity information

## Requirements

- OpenBabel >= 3.1.1 (already in meps environment) - for MOL, SDF, and MOL2
- RDKit >= 2023.3.1 (already in meps environment) - for MOL and SDF (fallback)

## Notes

- Only 3D coordinates are used for calculations
- MOL/SDF: Both OpenBabel and RDKit backends supported
- MOL2: Only OpenBabel backend supported
- Automatically selects available library
- V2000 format for MOL output files

## Troubleshooting

**"MOL format support requires either OpenBabel or RDKit"**
- Solution: `conda install openbabel` (already installed in meps)

**"MOL2 format support requires OpenBabel"**
- Solution: `conda install openbabel` (already installed in meps)

**"No 3D coordinates found in MOL file"**
- Solution: Generate 3D coordinates using molecular modeling software before use
