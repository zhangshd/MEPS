"""
AutoDock Vina Docking Module
This module provides utilities for molecular docking using AutoDock Vina.
Author: zhangshd
Date: 2025-10-12
"""

import os
import subprocess
from typing import Dict, Optional, Tuple, List
from openbabel import pybel

try:
    from .structure_parser import StructureParser
except ImportError:
    from structure_parser import StructureParser


class VinaDocking:
    """使用AutoDock Vina进行分子对接的类"""
    
    def __init__(self, work_dir: str = "./vina_work"):
        """
        初始化Vina对接器
        
        Args:
            work_dir: 工作目录
        """
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)
    
    def prepare_receptor(
        self, 
        structure: StructureParser, 
        output_pdbqt: str,
        receptor_name: str = "receptor"
    ) -> str:
        """
        准备受体分子用于对接
        
        Args:
            structure: StructureParser对象，包含受体结构
            output_pdbqt: 输出的PDBQT文件路径
            receptor_name: 受体名称
            
        Returns:
            PDBQT文件路径
        """
        # 首先保存为PDB格式
        pdb_file = os.path.join(self.work_dir, f"{receptor_name}.pdb")
        structure.write_pdb(pdb_file)
        
        # 使用obabel转换为PDBQT格式
        # PDBQT格式包含原子类型和部分电荷信息，是AutoDock/Vina的标准输入格式
        cmd = [
            "obabel",
            pdb_file,
            "-O", output_pdbqt,
            "-xr"  # 刚性受体
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"obabel转换失败: {result.stderr}")
        
        return output_pdbqt
    
    def prepare_ligand(
        self, 
        structure: StructureParser, 
        output_pdbqt: str,
        ligand_name: str = "ligand"
    ) -> str:
        """
        准备配体分子用于对接
        
        Args:
            structure: StructureParser对象，包含配体结构
            output_pdbqt: 输出的PDBQT文件路径
            ligand_name: 配体名称
            
        Returns:
            PDBQT文件路径
        """
        # 保存为PDB格式
        pdb_file = os.path.join(self.work_dir, f"{ligand_name}.pdb")
        structure.write_pdb(pdb_file)
        
        # 使用obabel转换为PDBQT格式，配体需要保持柔性
        cmd = [
            "obabel",
            pdb_file,
            "-O", output_pdbqt,
            "--partialcharge", "gasteiger",  # 添加Gasteiger电荷
            "-h"  # 添加氢原子
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"obabel转换失败: {result.stderr}")
        
        return output_pdbqt
    
    def calculate_search_box(
        self,
        receptor: StructureParser,
        ligand: StructureParser,
        padding: float = 10.0
    ) -> Dict[str, float]:
        """
        计算对接搜索盒的中心和大小
        
        Args:
            receptor: 受体结构
            ligand: 配体结构
            padding: 搜索盒边界填充距离 (Angstrom)
            
        Returns:
            包含中心坐标和尺寸的字典
        """
        # 合并两个分子以获得整体边界
        merged = receptor.merge(ligand)
        bbox = merged.get_bounding_box()
        
        # 计算中心
        center_x = (bbox['x'][0] + bbox['x'][1]) / 2.0
        center_y = (bbox['y'][0] + bbox['y'][1]) / 2.0
        center_z = (bbox['z'][0] + bbox['z'][1]) / 2.0
        
        # 计算尺寸（加上填充）
        size_x = bbox['x'][1] - bbox['x'][0] + 2 * padding
        size_y = bbox['y'][1] - bbox['y'][0] + 2 * padding
        size_z = bbox['z'][1] - bbox['z'][0] + 2 * padding
        
        return {
            'center_x': center_x,
            'center_y': center_y,
            'center_z': center_z,
            'size_x': size_x,
            'size_y': size_y,
            'size_z': size_z
        }
    
    def run_docking(
        self,
        receptor_pdbqt: str,
        ligand_pdbqt: str,
        output_pdbqt: str,
        center_x: float,
        center_y: float,
        center_z: float,
        size_x: float = 20.0,
        size_y: float = 20.0,
        size_z: float = 20.0,
        exhaustiveness: int = 8,
        num_modes: int = 9,
        energy_range: float = 3.0
    ) -> Dict[str, any]:
        """
        运行AutoDock Vina对接
        
        Args:
            receptor_pdbqt: 受体PDBQT文件路径
            ligand_pdbqt: 配体PDBQT文件路径
            output_pdbqt: 输出对接结果PDBQT文件路径
            center_x, center_y, center_z: 搜索盒中心坐标
            size_x, size_y, size_z: 搜索盒尺寸
            exhaustiveness: 搜索精度（越大越精确但越慢）
            num_modes: 输出的对接姿态数量
            energy_range: 能量范围 (kcal/mol)
            
        Returns:
            包含对接结果信息的字典
        """
        # 准备Vina命令
        cmd = [
            "vina",
            "--receptor", receptor_pdbqt,
            "--ligand", ligand_pdbqt,
            "--out", output_pdbqt,
            "--center_x", str(center_x),
            "--center_y", str(center_y),
            "--center_z", str(center_z),
            "--size_x", str(size_x),
            "--size_y", str(size_y),
            "--size_z", str(size_z),
            "--exhaustiveness", str(exhaustiveness),
            "--num_modes", str(num_modes),
            "--energy_range", str(energy_range)
        ]
        
        # 运行Vina
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Vina对接失败: {result.stderr}")
        
        # 解析对接结果
        docking_results = self._parse_vina_output(result.stdout)
        docking_results['output_file'] = output_pdbqt
        
        return docking_results
    
    def _parse_vina_output(self, output: str) -> Dict[str, any]:
        """
        解析Vina的标准输出
        
        Args:
            output: Vina标准输出内容
            
        Returns:
            解析后的结果字典
        """
        results = {
            'modes': [],
            'best_affinity': None
        }
        
        lines = output.split('\n')
        in_results_section = False
        
        for line in lines:
            # Check if we're in the results section
            if 'mode |   affinity' in line.lower() or 'kcal/mol' in line.lower():
                in_results_section = True
                continue
            
            # Parse docking mode information only in results section
            # Format: mode |   affinity | dist from best mode
            #            |   (kcal/mol)| rmsd l.b.| rmsd u.b.
            # Example:    1       -5.2      0.000      0.000
            if in_results_section and line.strip() and line.strip()[0].isdigit():
                parts = line.split()
                # Ensure we have valid numeric data (not progress like "0%")
                # Check that first part is pure digit and we have at least affinity value
                if len(parts) >= 2 and parts[0].isdigit() and not '%' in parts[0]:
                    try:
                        mode = {
                            'mode': int(parts[0]),
                            'affinity': float(parts[1]),
                            'rmsd_lb': float(parts[2]) if len(parts) > 2 else None,
                            'rmsd_ub': float(parts[3]) if len(parts) > 3 else None
                        }
                        results['modes'].append(mode)
                    except (ValueError, IndexError):
                        # Skip lines that cannot be parsed as valid mode data
                        continue
        
        if results['modes']:
            results['best_affinity'] = results['modes'][0]['affinity']
        
        return results
    
    def extract_best_pose(
        self,
        docked_pdbqt: str,
        output_pdb: str,
        mode: int = 1,
        add_hydrogens: bool = True
    ) -> StructureParser:
        """
        Extract specified docking pose from docking results
        
        Args:
            docked_pdbqt: Docked result PDBQT file
            output_pdb: Output PDB file path
            mode: Mode number to extract (1 is the best)
            add_hydrogens: Whether to add hydrogen atoms
            
        Returns:
            StructureParser object containing the extracted pose
        """
        # Read all conformations from PDBQT file using pybel
        mols = list(pybel.readfile("pdbqt", docked_pdbqt))
        
        if not mols:
            raise RuntimeError(f"Failed to read docking results from {docked_pdbqt}")
        
        if mode < 1 or mode > len(mols):
            raise ValueError(f"Mode {mode} is out of range (1-{len(mols)})")
        
        # Extract the specified conformation (mode is 1-indexed)
        mol = mols[mode - 1]
        
        # Write to PDB file
        mol.write("pdb", output_pdb, overwrite=True)
        mol = next(pybel.readfile("pdb", output_pdb))
        # Add hydrogens if requested
        if add_hydrogens:
            mol.addh()
            print("Added hydrogens to the extracted pose.")
        mol.write("pdb", output_pdb, overwrite=True)
        
        # Read the extracted PDB file into StructureParser
        parser = StructureParser()
        parser.read_pdb(output_pdb)
        
        return parser
    
    def dock_two_molecules(
        self,
        molecule_a: StructureParser,
        molecule_b: StructureParser,
        exhaustiveness: int = 8,
        padding: float = 10.0
    ) -> Tuple[StructureParser, Dict[str, any]]:
        """
        对两个分子进行对接（便捷方法）
        
        Args:
            molecule_a: 分子A（作为受体）
            molecule_b: 分子B（作为配体）
            exhaustiveness: 搜索精度
            padding: 搜索盒填充距离
            
        Returns:
            (对接后的复合物结构, 对接结果信息)
        """
        # 准备受体和配体
        receptor_pdbqt = os.path.join(self.work_dir, "receptor.pdbqt")
        ligand_pdbqt = os.path.join(self.work_dir, "ligand.pdbqt")
        output_pdbqt = os.path.join(self.work_dir, "docked.pdbqt")
        
        self.prepare_receptor(molecule_a, receptor_pdbqt)
        self.prepare_ligand(molecule_b, ligand_pdbqt)
        
        # 计算搜索盒
        search_box = self.calculate_search_box(molecule_a, molecule_b, padding)
        
        # 运行对接
        results = self.run_docking(
            receptor_pdbqt,
            ligand_pdbqt,
            output_pdbqt,
            search_box['center_x'],
            search_box['center_y'],
            search_box['center_z'],
            search_box['size_x'],
            search_box['size_y'],
            search_box['size_z'],
            exhaustiveness=exhaustiveness
        )
        
        # Extract best pose (only heavy atoms from PDBQT)
        best_pose_pdb = os.path.join(self.work_dir, "best_pose.pdb")
        ligand_docked = self.extract_best_pose(output_pdbqt, best_pose_pdb, mode=1, add_hydrogens=True)
        return ligand_docked, results
