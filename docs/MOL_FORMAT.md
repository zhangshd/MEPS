# MOL Format Support

## Overview

MEPS now supports MOL/SDF (MDL Molfile) format for molecular structure input and output.

## Supported Formats

| Format | Extension | Read | Write |
|--------|-----------|------|-------|
| XYZ | .xyz | ✓ | ✓ |
| PDB | .pdb | ✓ | ✓ |
| MOL | .mol | ✓ | ✓ |
| SDF | .sdf | ✓ | ✓ |
| Gaussian | .log, .out | ✓ | - |

## Usage

### Basic Reading and Writing

```python
from src.structure_parser import StructureParser

# Read MOL file
parser = StructureParser()
parser.read_mol("molecule.mol")

# Write MOL file
parser.write_mol("output.mol", mol_title="My Molecule")

# Format conversion
parser.read_xyz("input.xyz")
parser.write_mol("output.mol")
```

### Pipeline Integration

```python
from src.gaussian_runner import InteractionEnergyPipeline

pipeline = InteractionEnergyPipeline(
    gaussian_root="/opt/share/gaussian/g16",
    work_dir="./calculations"
)

# Use MOL files directly
results = pipeline.run_full_pipeline(
    molecule_a_file="benzene.mol",
    molecule_b_file="methane.mol",
    name_a="benzene",
    name_b="methane"
)
```

### Command Line

```bash
# Basic usage
python scripts/run_pipeline.py molecule_a.mol molecule_b.mol

# With parameters
python scripts/run_pipeline.py benzene.mol methane.mol \
    --name_a benzene --name_b methane \
    --functional M06-2X --basis def2-TZVP

# View help
python scripts/run_pipeline.py --help
```

## API Reference

### StructureParser Methods

**`read_mol(filepath: str)`**
- Read MOL/SDF format files
- Supports both 2D and 3D coordinates (3D required for calculations)
- Extracts atomic coordinates, charge, and multiplicity

**`write_mol(filepath: str, mol_title: str = "Molecule")`**
- Write MOL format files (V2000 format)
- `filepath`: Output file path
- `mol_title`: Title/name for the molecule

## Requirements

- OpenBabel >= 3.1.1 (already in meps environment)
- RDKit >= 2023.3.1 (already in meps environment)

The implementation automatically uses whichever library is available.

## Testing

```bash
# Run tests
conda activate meps
python tests/test_mol_format.py

# Run examples
python examples/mol_format_example.py
```

## Notes

- Only 3D coordinates are used for calculations
- Both OpenBabel and RDKit backends supported
- Automatically selects available library
- V2000 format for output files

## Troubleshooting

**"MOL format support requires either OpenBabel or RDKit"**
- Solution: `conda install openbabel` or `conda install rdkit` (already installed in meps)

**"No 3D coordinates found in MOL file"**
- Solution: Generate 3D coordinates using molecular modeling software before use
