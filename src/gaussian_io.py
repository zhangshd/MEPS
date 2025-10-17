"""
Gaussian Input/Output Module
This module provides utilities for generating Gaussian input files and parsing output files.
Author: zhangshd
Date: 2025-10-12
"""

import os
from typing import Dict, List, Optional, Tuple

try:
    from .structure_parser import StructureParser
except ImportError:
    from structure_parser import StructureParser


class GaussianInputGenerator:
    """Gaussian输入文件生成器"""
    
    def __init__(self, gaussian_root: str = "/opt/share/gaussian/g16"):
        """
        初始化Gaussian输入文件生成器
        
        Args:
            gaussian_root: Gaussian安装根目录
        """
        self.gaussian_root = gaussian_root
        
    def generate_optimization_input(
        self,
        structure: StructureParser,
        output_file: str,
        checkpoint_file: str,
        job_title: str,
        functional: str = "B3LYP",
        basis_set: str = "6-311++G(d,p)",
        dispersion: str = "GD3BJ",
        calc_freq: bool = True,
        mem: str = "100GB",
        nproc: int = 96,
        charge: int = 0,
        multiplicity: int = 1
    ) -> None:
        """
        生成单体结构优化的Gaussian输入文件
        
        Args:
            structure: StructureParser对象，包含分子结构
            output_file: 输出的.gjf文件路径
            checkpoint_file: checkpoint文件名
            job_title: 任务标题
            functional: 密度泛函，如B3LYP
            basis_set: 基组，如6-311++G(d,p)
            dispersion: 色散校正，如GD3BJ
            calc_freq: 是否计算频率
            mem: 内存设置
            nproc: 处理器核心数
            charge: 分子电荷
            multiplicity: 自旋多重度
        """
        with open(output_file, 'w') as f:
            # 写入资源配置
            f.write(f"%chk={checkpoint_file}\n")
            f.write(f"%mem={mem}\n")
            f.write(f"%nproc={nproc}\n")
            
            # 写入计算设置
            calc_type = "opt freq" if calc_freq else "opt"
            f.write(f"#p {calc_type} {functional}/{basis_set}")
            
            if dispersion:
                f.write(f" EmpiricalDispersion={dispersion}")
            
            f.write("\n\n")
            
            # 写入标题
            f.write(f"{job_title}\n\n")
            
            # 写入电荷和多重度
            f.write(f"{charge} {multiplicity}\n")
            
            # 写入坐标
            for element, x, y, z in structure.atoms:
                f.write(f" {element:2s}   {x:12.6f}   {y:12.6f}   {z:12.6f}\n")
            
            f.write("\n \n")
    
    def generate_counterpoise_input(
        self,
        structure_a: StructureParser,
        structure_b: StructureParser,
        output_file: str,
        checkpoint_file: str,
        job_title: str,
        functional: str = "B3LYP",
        basis_set: str = "6-311++G(d,p)",
        dispersion: str = "GD3BJ",
        calc_freq: bool = True,
        mem: str = "100GB",
        nproc: int = 96,
        charge_a: int = 0,
        multiplicity_a: int = 1,
        charge_b: int = 0,
        multiplicity_b: int = 1
    ) -> None:
        """
        生成带Counterpoise校正的复合物输入文件
        
        Args:
            structure_a: 片段A的StructureParser对象
            structure_b: 片段B的StructureParser对象
            output_file: 输出的.gjf文件路径
            checkpoint_file: checkpoint文件名
            job_title: 任务标题
            functional: 密度泛函
            basis_set: 基组
            dispersion: 色散校正
            calc_freq: 是否计算频率
            mem: 内存设置
            nproc: 处理器核心数
            charge_a: 片段A的电荷
            multiplicity_a: 片段A的多重度
            charge_b: 片段B的电荷
            multiplicity_b: 片段B的多重度
        """
        total_charge = charge_a + charge_b
        # 对于两个单重态分子，复合物也是单重态
        total_multiplicity = 1
        
        with open(output_file, 'w') as f:
            # Write resource configuration
            f.write(f"%chk={checkpoint_file}\n")
            f.write(f"%mem={mem}\n")
            f.write(f"%nprocshared={nproc}\n")
            
            # Write calculation settings with Counterpoise=2
            # Note: For stability with Counterpoise, we use opt only (not freq)
            # Freq can be calculated separately if needed
            calc_type = "opt" if calc_freq else "opt"  # Temporarily disable freq for stability
            f.write(f"#p {calc_type} {functional}/{basis_set}")
            
            if dispersion:
                f.write(f" empiricaldispersion={dispersion}")
            
            # Add NoSymm for better stability with Counterpoise calculations
            f.write(" Counterpoise=2 NoSymm\n\n")
            
            # 写入标题
            f.write(f"{job_title}\n\n")
            
            # 写入电荷和多重度
            # 格式：总电荷 总多重度 片段1电荷 片段1多重度 片段2电荷 片段2多重度
            f.write(f"{total_charge} {total_multiplicity} ")
            f.write(f"{charge_a} {multiplicity_a} ")
            f.write(f"{charge_b} {multiplicity_b}\n")
            
            # 写入片段A的坐标
            for element, x, y, z in structure_a.atoms:
                f.write(f" {element}(Fragment=1)  {x:12.6f} {y:12.6f} {z:12.6f}\n")
            
            # 写入片段B的坐标
            for element, x, y, z in structure_b.atoms:
                f.write(f" {element}(Fragment=2)  {x:12.6f} {y:12.6f} {z:12.6f}\n")
            
            f.write("\n\n")


class GaussianOutputParser:
    """Gaussian输出文件解析器"""
    
    def __init__(self, output_file: str):
        """
        初始化Gaussian输出文件解析器
        
        Args:
            output_file: Gaussian输出文件路径(.log或.out)
        """
        self.output_file = output_file
        self.content = self._read_file()
    
    def _read_file(self) -> List[str]:
        """读取输出文件内容"""
        with open(self.output_file, 'r') as f:
            return f.readlines()
    
    def is_normal_termination(self) -> bool:
        """
        检查Gaussian计算是否正常终止
        
        Returns:
            True表示正常终止，False表示异常
        """
        for line in reversed(self.content):
            if 'Normal termination' in line:
                return True
            if 'Error termination' in line:
                return False
        return False
    
    def get_scf_energy(self) -> Optional[float]:
        """
        获取最后一次SCF能量
        
        Returns:
            SCF能量(Hartree)，如果未找到则返回None
        """
        scf_energy = None
        for line in self.content:
            if 'SCF Done:' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == '=':
                        scf_energy = float(parts[i + 1])
        return scf_energy
    
    def get_optimized_structure(self) -> StructureParser:
        """
        获取优化后的分子结构
        
        Returns:
            包含优化后结构的StructureParser对象
        """
        parser = StructureParser()
        parser.read_gaussian_output(self.output_file)
        return parser
    
    def check_imaginary_frequencies(self) -> Tuple[bool, int]:
        """
        检查是否存在虚频
        
        Returns:
            (是否有虚频, 虚频数量)
        """
        has_imaginary = False
        imag_count = 0
        
        for line in self.content:
            if 'Frequencies --' in line:
                parts = line.split()
                for i in range(2, len(parts)):
                    freq = float(parts[i])
                    if freq < 0:
                        has_imaginary = True
                        imag_count += 1
        
        return has_imaginary, imag_count
    
    def get_optimization_steps(self) -> int:
        """
        获取优化步数
        
        Returns:
            优化步数
        """
        step_count = 0
        for line in self.content:
            if 'Step number' in line or 'Optimization completed' in line:
                step_count += 1
        return step_count
    
    def extract_thermochemistry(self) -> Dict[str, float]:
        """
        提取热化学数据
        
        Returns:
            包含热化学数据的字典
        """
        thermo_data = {}
        
        for i, line in enumerate(self.content):
            if 'Zero-point correction=' in line:
                thermo_data['zero_point_correction'] = float(line.split()[2])
            elif 'Thermal correction to Energy=' in line:
                thermo_data['thermal_correction_energy'] = float(line.split()[4])
            elif 'Thermal correction to Enthalpy=' in line:
                thermo_data['thermal_correction_enthalpy'] = float(line.split()[4])
            elif 'Thermal correction to Gibbs Free Energy=' in line:
                thermo_data['thermal_correction_gibbs'] = float(line.split()[6])
            elif 'Sum of electronic and zero-point Energies=' in line:
                thermo_data['energy_zpe'] = float(line.split()[6])
            elif 'Sum of electronic and thermal Energies=' in line:
                thermo_data['energy_thermal'] = float(line.split()[6])
            elif 'Sum of electronic and thermal Enthalpies=' in line:
                thermo_data['enthalpy'] = float(line.split()[6])
            elif 'Sum of electronic and thermal Free Energies=' in line:
                thermo_data['gibbs_free_energy'] = float(line.split()[7])
        
        return thermo_data
