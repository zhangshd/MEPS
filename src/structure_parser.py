"""
Structure Parser Module
This module provides utilities for parsing and manipulating molecular structures.
Author: zhangshd
Date: 2025-10-12
"""

import os
from typing import List, Tuple, Dict, Optional
import numpy as np

try:
    from openbabel import openbabel as ob
    OPENBABEL_AVAILABLE = True
except ImportError:
    OPENBABEL_AVAILABLE = False

try:
    from rdkit import Chem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


class StructureParser:
    """分子结构解析器，支持多种格式的分子结构文件读写"""
    
    def __init__(self):
        """初始化结构解析器"""
        self.atoms = []  # 存储原子信息列表，每个元素为(元素符号, x, y, z)
        self.charge = 0
        self.multiplicity = 1
        
    def read_xyz(self, filepath: str) -> None:
        """
        读取XYZ格式的分子结构文件
        
        Args:
            filepath: XYZ文件路径
        """
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # XYZ格式：第一行是原子数，第二行是注释，之后是原子坐标
        num_atoms = int(lines[0].strip())
        self.atoms = []
        
        for i in range(2, 2 + num_atoms):
            parts = lines[i].split()
            element = parts[0]
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            self.atoms.append((element, x, y, z))
    
    def read_pdb(self, filepath: str) -> None:
        """
        读取PDB格式的分子结构文件
        
        Args:
            filepath: PDB文件路径
        """
        self.atoms = []
        
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    # PDB格式固定列宽
                    element = line[76:78].strip()
                    if not element:
                        element = line[12:16].strip()[0]
                    
                    x = float(line[30:38].strip())
                    y = float(line[38:46].strip())
                    z = float(line[46:54].strip())
                    
                    self.atoms.append((element, x, y, z))
    
    def read_mol(self, filepath: str) -> None:
        """
        Read MOL/SDF format molecular structure file
        
        This method supports reading MOL and SDF format files using either 
        OpenBabel or RDKit library. The file can contain 2D or 3D coordinates.
        
        Args:
            filepath: Path to the MOL/SDF file
            
        Raises:
            RuntimeError: If neither OpenBabel nor RDKit is available
            ValueError: If the file cannot be parsed
        """
        self.atoms = []
        
        if OPENBABEL_AVAILABLE:
            self._read_mol_openbabel(filepath)
        elif RDKIT_AVAILABLE:
            self._read_mol_rdkit(filepath)
        else:
            raise RuntimeError(
                "MOL format support requires either OpenBabel or RDKit. "
                "Please install one of them: conda install openbabel or conda install rdkit"
            )
    
    def _read_mol_openbabel(self, filepath: str) -> None:
        """
        Read MOL file using OpenBabel library
        
        Args:
            filepath: Path to the MOL/SDF file
        """
        obConversion = ob.OBConversion()
        obConversion.SetInFormat("mol")
        
        mol = ob.OBMol()
        success = obConversion.ReadFile(mol, filepath)
        
        if not success:
            raise ValueError(f"Failed to read MOL file: {filepath}")
        
        self.atoms = []
        for i in range(mol.NumAtoms()):
            atom = mol.GetAtom(i + 1)
            element = atom.GetType()
            if len(element) > 1 and element[1].isupper():
                element = element[0]
            x = atom.GetX()
            y = atom.GetY()
            z = atom.GetZ()
            self.atoms.append((element, x, y, z))
        
        self.charge = mol.GetTotalCharge()
        self.multiplicity = mol.GetTotalSpinMultiplicity()
    
    def _read_mol_rdkit(self, filepath: str) -> None:
        """
        Read MOL file using RDKit library
        
        Args:
            filepath: Path to the MOL/SDF file
        """
        mol = Chem.MolFromMolFile(filepath, removeHs=False)
        
        if mol is None:
            raise ValueError(f"Failed to read MOL file: {filepath}")
        
        if mol.GetNumConformers() == 0:
            raise ValueError(f"No 3D coordinates found in MOL file: {filepath}")
        
        conf = mol.GetConformer()
        self.atoms = []
        
        for i in range(mol.GetNumAtoms()):
            atom = mol.GetAtomWithIdx(i)
            element = atom.GetSymbol()
            pos = conf.GetAtomPosition(i)
            x, y, z = pos.x, pos.y, pos.z
            self.atoms.append((element, x, y, z))
        
        self.charge = Chem.GetFormalCharge(mol)
        
        num_radical_electrons = sum(atom.GetNumRadicalElectrons() for atom in mol.GetAtoms())
        self.multiplicity = num_radical_electrons + 1
    
    def read_mol2(self, filepath: str) -> None:
        """
        Read MOL2 (Tripos) format molecular structure file
        
        This method reads MOL2 format files using OpenBabel library.
        MOL2 format includes atom types and bond information.
        
        Args:
            filepath: Path to the MOL2 file
            
        Raises:
            RuntimeError: If OpenBabel is not available
            ValueError: If the file cannot be parsed
        """
        if not OPENBABEL_AVAILABLE:
            raise RuntimeError(
                "MOL2 format support requires OpenBabel. "
                "Please install it: conda install openbabel"
            )
        
        obConversion = ob.OBConversion()
        obConversion.SetInFormat("mol2")
        
        mol = ob.OBMol()
        success = obConversion.ReadFile(mol, filepath)
        
        if not success:
            raise ValueError(f"Failed to read MOL2 file: {filepath}")
        
        self.atoms = []
        for i in range(mol.NumAtoms()):
            atom = mol.GetAtom(i + 1)
            element = atom.GetType()
            if len(element) > 1 and element[1].isupper():
                element = element[0]
            x = atom.GetX()
            y = atom.GetY()
            z = atom.GetZ()
            self.atoms.append((element, x, y, z))
        
        self.charge = mol.GetTotalCharge()
        self.multiplicity = mol.GetTotalSpinMultiplicity()
    
    def read_gaussian_output(self, filepath: str) -> None:
        """
        从Gaussian输出文件中读取优化后的结构
        
        Args:
            filepath: Gaussian输出文件(.log或.out)路径
        """
        self.atoms = []
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # 查找最后一次优化的标准坐标
        orientation_blocks = []
        for i, line in enumerate(lines):
            if 'Standard orientation:' in line or 'Input orientation:' in line:
                orientation_blocks.append(i)
        
        if not orientation_blocks:
            raise ValueError("在Gaussian输出文件中未找到坐标信息")
        
        # 使用最后一个坐标块
        start_line = orientation_blocks[-1] + 5  # 跳过表头
        
        atomic_numbers = {
            1: 'H', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 
            15: 'P', 16: 'S', 17: 'Cl', 35: 'Br', 53: 'I'
        }
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            if '---' in line:
                break
            
            parts = line.split()
            if len(parts) >= 6:
                atomic_num = int(parts[1])
                x, y, z = float(parts[3]), float(parts[4]), float(parts[5])
                element = atomic_numbers.get(atomic_num, str(atomic_num))
                self.atoms.append((element, x, y, z))
    
    def write_xyz(self, filepath: str, comment: str = "") -> None:
        """
        写入XYZ格式的分子结构文件
        
        Args:
            filepath: 输出文件路径
            comment: 注释行内容
        """
        with open(filepath, 'w') as f:
            f.write(f"{len(self.atoms)}\n")
            f.write(f"{comment}\n")
            for element, x, y, z in self.atoms:
                f.write(f"{element:2s} {x:12.6f} {y:12.6f} {z:12.6f}\n")
    
    def write_pdb(self, filepath: str) -> None:
        """
        写入PDB格式的分子结构文件
        
        Args:
            filepath: 输出文件路径
        """
        with open(filepath, 'w') as f:
            for i, (element, x, y, z) in enumerate(self.atoms, 1):
                # PDB格式固定列宽
                f.write(f"ATOM  {i:5d}  {element:2s}  MOL A   1    "
                       f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00          {element:2s}\n")
            f.write("END\n")
    
    def write_mol(self, filepath: str, mol_title: str = "Molecule") -> None:
        """
        Write MOL/SDF format molecular structure file
        
        This method supports writing MOL format files using either 
        OpenBabel or RDKit library. The output is in V2000 format.
        
        Args:
            filepath: Path to the output MOL file
            mol_title: Title/name for the molecule (optional)
            
        Raises:
            RuntimeError: If neither OpenBabel nor RDKit is available
        """
        if OPENBABEL_AVAILABLE:
            self._write_mol_openbabel(filepath, mol_title)
        elif RDKIT_AVAILABLE:
            self._write_mol_rdkit(filepath, mol_title)
        else:
            raise RuntimeError(
                "MOL format support requires either OpenBabel or RDKit. "
                "Please install one of them: conda install openbabel or conda install rdkit"
            )
    
    def _write_mol_openbabel(self, filepath: str, mol_title: str) -> None:
        """
        Write MOL file using OpenBabel library
        
        Args:
            filepath: Path to the output MOL file
            mol_title: Title for the molecule
        """
        mol = ob.OBMol()
        mol.SetTitle(mol_title)
        
        element_to_atomic_num = {
            'H': 1, 'C': 6, 'N': 7, 'O': 8, 'F': 9,
            'P': 15, 'S': 16, 'Cl': 17, 'Br': 35, 'I': 53
        }
        
        for element, x, y, z in self.atoms:
            atom = mol.NewAtom()
            atomic_num = element_to_atomic_num.get(element, 6)
            atom.SetAtomicNum(atomic_num)
            atom.SetVector(x, y, z)
        
        mol.SetTotalCharge(int(self.charge))
        
        obConversion = ob.OBConversion()
        obConversion.SetOutFormat("mol")
        success = obConversion.WriteFile(mol, filepath)
        
        if not success:
            raise RuntimeError(f"Failed to write MOL file: {filepath}")
    
    def _write_mol_rdkit(self, filepath: str, mol_title: str) -> None:
        """
        Write MOL file using RDKit library
        
        Args:
            filepath: Path to the output MOL file
            mol_title: Title for the molecule
        """
        rwmol = Chem.RWMol()
        
        element_to_atomic_num = {
            'H': 1, 'C': 6, 'N': 7, 'O': 8, 'F': 9,
            'P': 15, 'S': 16, 'Cl': 17, 'Br': 35, 'I': 53
        }
        
        atom_indices = []
        for element, x, y, z in self.atoms:
            atomic_num = element_to_atomic_num.get(element, 6)
            atom = Chem.Atom(atomic_num)
            idx = rwmol.AddAtom(atom)
            atom_indices.append(idx)
        
        mol = rwmol.GetMol()
        
        conf = Chem.Conformer(len(self.atoms))
        for i, (element, x, y, z) in enumerate(self.atoms):
            conf.SetAtomPosition(i, (x, y, z))
        mol.AddConformer(conf)
        
        mol.SetProp("_Name", mol_title)
        
        writer = Chem.SDWriter(filepath)
        writer.write(mol)
        writer.close()
    
    def write_mol2(self, filepath: str, mol_title: str = "Molecule") -> None:
        """
        Write MOL2 (Tripos) format molecular structure file
        
        This method writes MOL2 format files using OpenBabel library.
        The output includes atom types and basic connectivity.
        
        Args:
            filepath: Path to the output MOL2 file
            mol_title: Title/name for the molecule (optional)
            
        Raises:
            RuntimeError: If OpenBabel is not available
        """
        if not OPENBABEL_AVAILABLE:
            raise RuntimeError(
                "MOL2 format support requires OpenBabel. "
                "Please install it: conda install openbabel"
            )
        
        mol = ob.OBMol()
        mol.SetTitle(mol_title)
        
        element_to_atomic_num = {
            'H': 1, 'C': 6, 'N': 7, 'O': 8, 'F': 9,
            'P': 15, 'S': 16, 'Cl': 17, 'Br': 35, 'I': 53
        }
        
        for element, x, y, z in self.atoms:
            atom = mol.NewAtom()
            atomic_num = element_to_atomic_num.get(element, 6)
            atom.SetAtomicNum(atomic_num)
            atom.SetVector(x, y, z)
        
        mol.SetTotalCharge(int(self.charge))
        
        obConversion = ob.OBConversion()
        obConversion.SetOutFormat("mol2")
        success = obConversion.WriteFile(mol, filepath)
        
        if not success:
            raise RuntimeError(f"Failed to write MOL2 file: {filepath}")
    
    def write_gaussian_coords(self, filepath: str, fragment: Optional[int] = None) -> None:
        """
        写入Gaussian输入文件格式的坐标部分
        
        Args:
            filepath: 输出文件路径
            fragment: 片段编号，如果指定则在原子后添加(Fragment=N)标记
        """
        with open(filepath, 'w') as f:
            for element, x, y, z in self.atoms:
                if fragment is not None:
                    f.write(f" {element}(Fragment={fragment})  {x:12.6f} {y:12.6f} {z:12.6f}\n")
                else:
                    f.write(f" {element}  {x:12.6f} {y:12.6f} {z:12.6f}\n")
    
    def get_center_of_mass(self) -> Tuple[float, float, float]:
        """
        计算分子的质心坐标
        
        Returns:
            质心坐标(x, y, z)
        """
        atomic_masses = {
            'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
            'F': 18.998, 'P': 30.974, 'S': 32.065, 'Cl': 35.453,
            'Br': 79.904, 'I': 126.904
        }
        
        total_mass = 0.0
        cx, cy, cz = 0.0, 0.0, 0.0
        
        for element, x, y, z in self.atoms:
            mass = atomic_masses.get(element, 12.011)  # 默认使用碳的质量
            total_mass += mass
            cx += mass * x
            cy += mass * y
            cz += mass * z
        
        return cx / total_mass, cy / total_mass, cz / total_mass
    
    def translate(self, dx: float, dy: float, dz: float) -> None:
        """
        平移分子结构
        
        Args:
            dx, dy, dz: 各方向的平移距离
        """
        self.atoms = [(element, x + dx, y + dy, z + dz) 
                      for element, x, y, z in self.atoms]
    
    def center_at_origin(self) -> None:
        """将分子质心移动到原点"""
        cx, cy, cz = self.get_center_of_mass()
        self.translate(-cx, -cy, -cz)
    
    def get_bounding_box(self) -> Dict[str, Tuple[float, float]]:
        """
        获取分子的边界盒
        
        Returns:
            包含x, y, z范围的字典，每个键对应(min, max)元组
        """
        if not self.atoms:
            return {'x': (0, 0), 'y': (0, 0), 'z': (0, 0)}
        
        coords = np.array([[x, y, z] for _, x, y, z in self.atoms])
        
        return {
            'x': (coords[:, 0].min(), coords[:, 0].max()),
            'y': (coords[:, 1].min(), coords[:, 1].max()),
            'z': (coords[:, 2].min(), coords[:, 2].max())
        }
    
    def merge(self, other: 'StructureParser') -> 'StructureParser':
        """
        合并两个分子结构
        
        Args:
            other: 另一个StructureParser对象
            
        Returns:
            包含两个分子的新StructureParser对象
        """
        merged = StructureParser()
        merged.atoms = self.atoms + other.atoms
        merged.charge = self.charge + other.charge
        # 对于多重度，简单情况下取较大值
        merged.multiplicity = max(self.multiplicity, other.multiplicity)
        return merged
    
    def set_charge_multiplicity(self, charge: int, multiplicity: int) -> None:
        """
        设置分子的电荷和自旋多重度
        
        Args:
            charge: 总电荷
            multiplicity: 自旋多重度
        """
        self.charge = charge
        self.multiplicity = multiplicity
    
    def get_atom_count(self) -> int:
        """
        获取原子数量
        
        Returns:
            原子总数
        """
        return len(self.atoms)
    
    def copy(self) -> 'StructureParser':
        """
        创建当前对象的深拷贝
        
        Returns:
            新的StructureParser对象
        """
        new_parser = StructureParser()
        new_parser.atoms = self.atoms.copy()
        new_parser.charge = self.charge
        new_parser.multiplicity = self.multiplicity
        return new_parser
    
    def align_to(self, reference: 'StructureParser') -> None:
        """
        Align this structure to a reference structure based on heavy atoms
        Uses Kabsch algorithm for optimal rotation and translation
        
        Args:
            reference: Reference structure to align to
        """
        # Extract heavy atoms (non-hydrogen) from both structures
        self_heavy = [(i, atom) for i, atom in enumerate(self.atoms) if atom[0] != 'H']
        ref_heavy = [(i, atom) for i, atom in enumerate(reference.atoms) if atom[0] != 'H']
        
        if len(self_heavy) == 0 or len(ref_heavy) == 0:
            return
        
        if len(self_heavy) != len(ref_heavy):
            # If heavy atom counts don't match, just do centroid-based translation
            self_coords = np.array([[x, y, z] for _, (_, x, y, z) in self_heavy])
            ref_coords = np.array([[x, y, z] for _, (_, x, y, z) in ref_heavy])
            
            self_centroid = self_coords.mean(axis=0)
            ref_centroid = ref_coords.mean(axis=0)
            
            translation = ref_centroid - self_centroid
            self.translate(translation[0], translation[1], translation[2])
            return
        
        # Extract coordinates of heavy atoms
        self_coords = np.array([[x, y, z] for _, (_, x, y, z) in self_heavy])
        ref_coords = np.array([[x, y, z] for _, (_, x, y, z) in ref_heavy])
        
        # Center both coordinate sets
        self_centroid = self_coords.mean(axis=0)
        ref_centroid = ref_coords.mean(axis=0)
        
        self_coords_centered = self_coords - self_centroid
        ref_coords_centered = ref_coords - ref_centroid
        
        # Compute covariance matrix
        H = self_coords_centered.T @ ref_coords_centered
        
        # SVD to find optimal rotation
        U, S, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T
        
        # Ensure proper rotation (det(R) = 1)
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T
        
        # Apply transformation to all atoms
        all_coords = np.array([[x, y, z] for _, x, y, z in self.atoms])
        
        # Translate to origin, rotate, then translate to reference centroid
        all_coords_centered = all_coords - self_centroid
        all_coords_rotated = all_coords_centered @ R.T
        all_coords_final = all_coords_rotated + ref_centroid
        
        # Update atom coordinates
        self.atoms = [(elem, all_coords_final[i, 0], all_coords_final[i, 1], all_coords_final[i, 2])
                      for i, (elem, _, _, _) in enumerate(self.atoms)]
