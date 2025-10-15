"""
Result Extractor Module
This module provides utilities for extracting interaction energy results from Gaussian output.
Author: zhangshd
Date: 2025-10-12
"""

import re
from typing import Dict, List, Optional, Tuple


class ResultExtractor:
    """从Gaussian输出文件中提取相互作用能结果"""
    
    def __init__(self, output_file: str):
        """
        初始化结果提取器
        
        Args:
            output_file: Gaussian输出文件路径
        """
        self.output_file = output_file
        self.content = self._read_file()
    
    def _read_file(self) -> List[str]:
        """读取输出文件内容"""
        with open(self.output_file, 'r') as f:
            return f.readlines()
    
    def extract_counterpoise_results(self) -> Dict[str, any]:
        """
        从Counterpoise计算输出中提取相互作用能和BSSE能量
        
        Returns:
            包含以下键的字典:
            - counterpoise_corrected_energy: CP校正后的能量 (Hartree)
            - bsse_energy: BSSE能量 (Hartree)
            - sum_of_fragments: 片段能量和 (Hartree)
            - complexation_energy_raw: 未校正的相互作用能 (kcal/mol)
            - complexation_energy_corrected: 校正后的相互作用能 (kcal/mol)
            - optimization_steps: 优化步数列表
            - converged: 是否收敛
        """
        results = {
            'counterpoise_corrected_energy': None,
            'bsse_energy': None,
            'sum_of_fragments': None,
            'complexation_energy_raw': None,
            'complexation_energy_corrected': None,
            'optimization_steps': [],
            'converged': False
        }
        
        # 存储所有优化步骤的能量数据
        step_data = []
        
        for i, line in enumerate(self.content):
            # 提取每一步优化的Counterpoise数据
            if 'Counterpoise corrected energy' in line:
                cp_energy = float(line.split('=')[1].strip())
                
                # 查找接下来的BSSE和complexation energy
                bsse = None
                raw_energy = None
                corrected_energy = None
                
                for j in range(i + 1, min(i + 10, len(self.content))):
                    if 'BSSE energy' in self.content[j]:
                        bsse = float(self.content[j].split('=')[1].strip())
                    elif 'complexation energy' in self.content[j] and '(raw)' in self.content[j]:
                        match = re.search(r'([-+]?\d+\.\d+)\s+kcal/mole', self.content[j])
                        if match:
                            raw_energy = float(match.group(1))
                    elif 'complexation energy' in self.content[j] and '(corrected)' in self.content[j]:
                        match = re.search(r'([-+]?\d+\.\d+)\s+kcal/mole', self.content[j])
                        if match:
                            corrected_energy = float(match.group(1))
                
                step_data.append({
                    'cp_energy': cp_energy,
                    'bsse': bsse,
                    'raw_energy': raw_energy,
                    'corrected_energy': corrected_energy
                })
            
            # 检查是否正常终止
            if 'Normal termination' in line:
                results['converged'] = True
        
        # 使用最后一步的数据作为最终结果
        if step_data:
            last_step = step_data[-1]
            results['counterpoise_corrected_energy'] = last_step['cp_energy']
            results['bsse_energy'] = last_step['bsse']
            results['complexation_energy_raw'] = last_step['raw_energy']
            results['complexation_energy_corrected'] = last_step['corrected_energy']
            results['optimization_steps'] = step_data
        
        return results
    
    def extract_monomer_energy(self) -> Optional[float]:
        """
        从单体优化输出中提取最终SCF能量
        
        Returns:
            SCF能量 (Hartree)，未找到则返回None
        """
        scf_energy = None
        
        for line in self.content:
            if 'SCF Done:' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == '=' and i + 1 < len(parts):
                        scf_energy = float(parts[i + 1])
        
        return scf_energy
    
    def get_optimization_summary(self) -> Dict[str, any]:
        """
        获取优化过程的摘要信息
        
        Returns:
            包含优化摘要的字典
        """
        summary = {
            'converged': False,
            'num_steps': 0,
            'has_imaginary_freq': False,
            'num_imaginary_freq': 0,
            'final_energy': None
        }
        
        # 检查是否收敛
        for line in self.content:
            if 'Optimization completed' in line or 'Stationary point found' in line:
                summary['converged'] = True
            if 'Normal termination' in line:
                summary['converged'] = True
        
        # 统计优化步数
        step_count = 0
        for line in self.content:
            if 'Step number' in line:
                step_count += 1
        summary['num_steps'] = step_count
        
        # 检查虚频
        imag_count = 0
        for line in self.content:
            if 'Frequencies --' in line:
                parts = line.split()
                for i in range(2, len(parts)):
                    try:
                        freq = float(parts[i])
                        if freq < 0:
                            imag_count += 1
                    except ValueError:
                        continue
        
        if imag_count > 0:
            summary['has_imaginary_freq'] = True
            summary['num_imaginary_freq'] = imag_count
        
        # 获取最终能量
        summary['final_energy'] = self.extract_monomer_energy()
        
        return summary
    
    def extract_all_energies(self) -> List[float]:
        """
        提取所有SCF能量（用于监控优化过程）
        
        Returns:
            SCF能量列表 (Hartree)
        """
        energies = []
        
        for line in self.content:
            if 'SCF Done:' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == '=' and i + 1 < len(parts):
                        energies.append(float(parts[i + 1]))
        
        return energies
    
    def extract_error_messages(self) -> List[str]:
        """
        提取错误和警告信息
        
        Returns:
            错误/警告信息列表
        """
        messages = []
        
        for line in self.content:
            if 'Error' in line or 'Warning' in line:
                messages.append(line.strip())
            if 'Error termination' in line:
                messages.append(line.strip())
        
        return messages
    
    def generate_summary_report(self, output_file: str) -> None:
        """
        生成可读的结果摘要报告
        
        Args:
            output_file: 输出报告文件路径
        """
        cp_results = self.extract_counterpoise_results()
        opt_summary = self.get_optimization_summary()
        errors = self.extract_error_messages()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("分子间相互作用能计算结果报告\n")
            f.write("=" * 80 + "\n\n")
            
            # 优化摘要
            f.write("【优化过程摘要】\n")
            f.write(f"  收敛状态: {'已收敛' if opt_summary['converged'] else '未收敛'}\n")
            f.write(f"  优化步数: {opt_summary['num_steps']}\n")
            f.write(f"  虚频检查: {'存在{0}个虚频'.format(opt_summary['num_imaginary_freq']) if opt_summary['has_imaginary_freq'] else '无虚频'}\n")
            f.write(f"  最终能量: {opt_summary['final_energy']:.8f} Hartree\n\n")
            
            # Counterpoise结果
            if cp_results['complexation_energy_corrected'] is not None:
                f.write("【相互作用能结果】\n")
                f.write(f"  相互作用能 (未校正): {cp_results['complexation_energy_raw']:.2f} kcal/mol\n")
                f.write(f"  相互作用能 (BSSE校正后): {cp_results['complexation_energy_corrected']:.2f} kcal/mol\n")
                f.write(f"  BSSE能量: {cp_results['bsse_energy']:.8f} Hartree\n")
                f.write(f"            {cp_results['bsse_energy'] * 627.509:.2f} kcal/mol\n")
                f.write(f"  CP校正能量: {cp_results['counterpoise_corrected_energy']:.8f} Hartree\n\n")
                
                # 优化步骤详情
                if cp_results['optimization_steps']:
                    f.write("【优化步骤详情】\n")
                    f.write(f"  总步数: {len(cp_results['optimization_steps'])}\n")
                    f.write("  步骤   CP能量(Hartree)    BSSE(Hartree)    相互作用能(kcal/mol)\n")
                    f.write("-" * 80 + "\n")
                    for i, step in enumerate(cp_results['optimization_steps'], 1):
                        f.write(f"  {i:4d}   {step['cp_energy']:15.8f}  {step['bsse']:15.8f}  "
                               f"{step['corrected_energy']:10.2f}\n")
                    f.write("\n")
            
            # 错误和警告
            if errors:
                f.write("【警告和错误信息】\n")
                for error in errors:
                    f.write(f"  {error}\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("报告生成完成\n")
            f.write("=" * 80 + "\n")
