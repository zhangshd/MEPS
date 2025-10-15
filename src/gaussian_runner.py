"""
Gaussian Runner Module
This module provides utilities for running and monitoring Gaussian calculations.
Author: zhangshd
Date: 2025-10-12
"""

import os
import time
import subprocess
import json
from typing import Dict, Optional, List, Tuple
from pathlib import Path

try:
    from .gaussian_io import GaussianInputGenerator, GaussianOutputParser
    from .structure_parser import StructureParser
    from .result_extractor import ResultExtractor
    from .vina_docking import VinaDocking
except ImportError:
    from gaussian_io import GaussianInputGenerator, GaussianOutputParser
    from structure_parser import StructureParser
    from result_extractor import ResultExtractor
    from vina_docking import VinaDocking


class GaussianRunner:
    """Gaussian计算任务运行和监控类"""
    
    def __init__(self, gaussian_root: str = "/opt/share/gaussian/g16"):
        """
        初始化Gaussian运行器
        
        Args:
            gaussian_root: Gaussian安装根目录
        """
        self.gaussian_root = gaussian_root
        self.g16_exe = os.path.join(gaussian_root, "g16")
        self.formchk_exe = os.path.join(gaussian_root, "formchk")
        
        # 验证Gaussian是否可用
        if not os.path.exists(self.g16_exe):
            raise FileNotFoundError(f"Gaussian可执行文件不存在: {self.g16_exe}")
    
    def setup_environment(self) -> Dict[str, str]:
        """
        设置Gaussian运行环境变量
        
        Returns:
            环境变量字典
        """
        env = os.environ.copy()
        env['g16root'] = os.path.dirname(self.gaussian_root)
        env['GAUSS_EXEDIR'] = self.gaussian_root
        
        # 添加Gaussian到PATH
        if 'PATH' in env:
            env['PATH'] = f"{self.gaussian_root}:{env['PATH']}"
        else:
            env['PATH'] = self.gaussian_root
        
        return env
    
    def run_gaussian(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        wait: bool = True,
        timeout: Optional[int] = None
    ) -> subprocess.CompletedProcess:
        """
        运行Gaussian计算
        
        Args:
            input_file: Gaussian输入文件(.gjf)路径
            output_file: 输出文件路径，如果为None则自动生成
            wait: 是否等待计算完成
            timeout: 超时时间（秒），None表示不限时
            
        Returns:
            subprocess.CompletedProcess对象
        """
        if output_file is None:
            # 自动生成输出文件名
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.log"
        
        env = self.setup_environment()
        
        # 运行Gaussian
        with open(output_file, 'w') as out_f:
            if wait:
                result = subprocess.run(
                    [self.g16_exe, input_file],
                    env=env,
                    stdout=out_f,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout
                )
            else:
                # 后台运行
                result = subprocess.Popen(
                    [self.g16_exe, input_file],
                    env=env,
                    stdout=out_f,
                    stderr=subprocess.PIPE,
                    text=True
                )
        
        return result
    
    def monitor_calculation(
        self,
        output_file: str,
        check_interval: int = 60
    ) -> bool:
        """
        监控正在运行的Gaussian计算
        
        Args:
            output_file: Gaussian输出文件路径
            check_interval: 检查间隔（秒）
            
        Returns:
            计算是否成功完成
        """
        print(f"开始监控计算: {output_file}")
        
        while True:
            if not os.path.exists(output_file):
                print("等待输出文件生成...")
                time.sleep(check_interval)
                continue
            
            with open(output_file, 'r') as f:
                content = f.read()
            
            if 'Normal termination' in content:
                print("计算正常完成!")
                return True
            elif 'Error termination' in content:
                print("计算出错终止!")
                return False
            else:
                # 尝试提取当前进度信息
                lines = content.split('\n')
                for line in reversed(lines[-100:]):  # 检查最后100行
                    if 'Step number' in line:
                        print(f"当前进度: {line.strip()}")
                        break
                
                print(f"计算进行中，等待{check_interval}秒后再次检查...")
                time.sleep(check_interval)
    
    def convert_chk_to_fchk(self, chk_file: str, fchk_file: Optional[str] = None) -> str:
        """
        将Gaussian的chk文件转换为fchk格式
        
        Args:
            chk_file: checkpoint文件路径
            fchk_file: 格式化checkpoint文件路径，如果为None则自动生成
            
        Returns:
            生成的fchk文件路径
        """
        if fchk_file is None:
            base_name = os.path.splitext(chk_file)[0]
            fchk_file = f"{base_name}.fchk"
        
        env = self.setup_environment()
        
        result = subprocess.run(
            [self.formchk_exe, chk_file, fchk_file],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"formchk转换失败: {result.stderr}")
        
        return fchk_file
    
    def check_calculation_status(self, output_file: str) -> Dict[str, any]:
        """
        检查计算状态
        
        Args:
            output_file: Gaussian输出文件路径
            
        Returns:
            状态信息字典
        """
        status = {
            'exists': os.path.exists(output_file),
            'completed': False,
            'success': False,
            'error_message': None
        }
        
        if not status['exists']:
            return status
        
        parser = GaussianOutputParser(output_file)
        status['completed'] = True
        status['success'] = parser.is_normal_termination()
        
        if not status['success']:
            extractor = ResultExtractor(output_file)
            errors = extractor.extract_error_messages()
            if errors:
                status['error_message'] = '; '.join(errors[:3])  # 只保留前3个错误
        
        return status


class InteractionEnergyPipeline:
    """分子间相互作用能计算的完整流程管理类"""
    
    def __init__(
        self,
        gaussian_root: str = "/opt/share/gaussian/g16",
        work_dir: str = "./meps_calculations"
    ):
        """
        初始化流程管理器
        
        Args:
            gaussian_root: Gaussian安装根目录
            work_dir: 工作目录
        """
        self.gaussian_root = gaussian_root
        self.work_dir = work_dir
        self.runner = GaussianRunner(gaussian_root)
        self.input_gen = GaussianInputGenerator(gaussian_root)
        
        # 创建工作目录
        os.makedirs(work_dir, exist_ok=True)
        
        # 创建子目录
        self.monomer_dir = os.path.join(work_dir, "monomers")
        self.complex_dir = os.path.join(work_dir, "complex")
        self.results_dir = os.path.join(work_dir, "results")
        
        for dir_path in [self.monomer_dir, self.complex_dir, self.results_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def optimize_monomer(
        self,
        structure: StructureParser,
        name: str,
        functional: str = "B3LYP",
        basis_set: str = "6-311++G(d,p)",
        dispersion: str = "GD3BJ",
        mem: str = "100GB",
        nproc: int = 96,
        wait: bool = True
    ) -> Dict[str, str]:
        """
        优化单体分子
        
        Args:
            structure: StructureParser对象
            name: 分子名称
            functional: 泛函
            basis_set: 基组
            dispersion: 色散校正
            mem: 内存
            nproc: CPU核心数
            wait: 是否等待计算完成
            
        Returns:
            包含文件路径的字典
        """
        print(f"\n{'='*60}")
        print(f"步骤: 优化单体分子 - {name}")
        print(f"{'='*60}")
        
        # 生成文件路径
        gjf_file = os.path.join(self.monomer_dir, f"{name}.gjf")
        chk_file = f"{name}.chk"
        log_file = os.path.join(self.monomer_dir, f"{name}.log")
        
        # 生成输入文件
        print(f"生成Gaussian输入文件: {gjf_file}")
        self.input_gen.generate_optimization_input(
            structure=structure,
            output_file=gjf_file,
            checkpoint_file=chk_file,
            job_title=f"{name} Optimization",
            functional=functional,
            basis_set=basis_set,
            dispersion=dispersion,
            mem=mem,
            nproc=nproc
        )
        
        # 运行计算
        print(f"开始运行Gaussian计算...")
        self.runner.run_gaussian(gjf_file, log_file, wait=wait)
        
        if wait:
            # 检查计算结果
            status = self.runner.check_calculation_status(log_file)
            if status['success']:
                print(f"✓ {name} 优化成功完成")
            else:
                print(f"✗ {name} 优化失败: {status.get('error_message', 'Unknown error')}")
        
        return {
            'gjf': gjf_file,
            'chk': os.path.join(self.monomer_dir, chk_file),
            'log': log_file,
            'name': name
        }
    
    def dock_molecules(
        self,
        structure_a: StructureParser,
        structure_b: StructureParser,
        exhaustiveness: int = 8
    ) -> Tuple[StructureParser, Dict[str, any]]:
        """
        使用Vina对接两个分子
        
        Args:
            structure_a: 分子A结构
            structure_b: 分子B结构
            exhaustiveness: 对接精度
            
        Returns:
            (复合物结构, 对接结果)
        """
        print(f"\n{'='*60}")
        print(f"步骤: 分子对接")
        print(f"{'='*60}")
        
        vina_work = os.path.join(self.work_dir, "vina_docking")
        docker = VinaDocking(work_dir=vina_work)
        
        print("运行AutoDock Vina对接...")
        complex_structure, results = docker.dock_two_molecules(
            structure_a,
            structure_b,
            exhaustiveness=exhaustiveness
        )
        
        print(f"✓ 对接完成")
        print(f"  最佳亲和力: {results['best_affinity']} kcal/mol")
        print(f"  生成姿态数: {len(results['modes'])}")
        
        return complex_structure, results
    
    def optimize_complex(
        self,
        structure_a: StructureParser = None,
        structure_b: StructureParser = None,
        complex_structure: StructureParser = None,
        name: str = "complex",
        functional: str = "B3LYP",
        basis_set: str = "6-311++G(d,p)",
        dispersion: str = "GD3BJ",
        mem: str = "100GB",
        nproc: int = 96,
        wait: bool = True
    ) -> Dict[str, str]:
        """
        优化复合物并计算Counterpoise校正的相互作用能
        
        Args:
            structure_a: 片段A结构 (如果提供complex_structure则可选)
            structure_b: 片段B结构 (如果提供complex_structure则可选)
            complex_structure: 已组装的复合物结构 (例如来自对接)
                如果提供此参数，将使用前N个原子作为片段A，其余作为片段B
                其中N是structure_a的原子数（必须同时提供structure_a以确定分割点）
            name: 复合物名称
            functional: 泛函
            basis_set: 基组
            dispersion: 色散校正
            mem: 内存
            nproc: CPU核心数
            wait: 是否等待计算完成
            
        Returns:
            包含文件路径的字典
        """
        print(f"\n{'='*60}")
        print(f"步骤: 优化复合物并计算相互作用能")
        print(f"{'='*60}")
        
        # Handle complex_structure input
        if complex_structure is not None:
            if structure_a is None:
                raise ValueError("When using complex_structure, structure_a must be provided to determine fragment split point")
            
            # Split complex_structure into fragments based on structure_a atom count
            n_atoms_a = len(structure_a.atoms)
            total_atoms = len(complex_structure.atoms)
            
            # Create fragment A from first n_atoms_a atoms
            frag_a = StructureParser()
            frag_a.atoms = complex_structure.atoms[:n_atoms_a]
            frag_a.charge = structure_a.charge
            frag_a.multiplicity = structure_a.multiplicity
            
            # Create fragment B from remaining atoms
            frag_b = StructureParser()
            frag_b.atoms = complex_structure.atoms[n_atoms_a:]
            if structure_b is not None:
                frag_b.charge = structure_b.charge
                frag_b.multiplicity = structure_b.multiplicity
            else:
                frag_b.charge = 0
                frag_b.multiplicity = 1
            
            # Use these fragments for the calculation
            use_structure_a = frag_a
            use_structure_b = frag_b
            
            print(f"使用对接后的复合物结构:")
            print(f"  片段A: {n_atoms_a} 个原子")
            print(f"  片段B: {total_atoms - n_atoms_a} 个原子")
        else:
            if structure_a is None or structure_b is None:
                raise ValueError("Either complex_structure or both structure_a and structure_b must be provided")
            use_structure_a = structure_a
            use_structure_b = structure_b
        
        # 生成文件路径
        gjf_file = os.path.join(self.complex_dir, f"{name}.gjf")
        chk_file = f"{name}.chk"
        log_file = os.path.join(self.complex_dir, f"{name}.log")
        
        # 生成Counterpoise输入文件
        print(f"生成Counterpoise计算输入文件: {gjf_file}")
        self.input_gen.generate_counterpoise_input(
            structure_a=use_structure_a,
            structure_b=use_structure_b,
            output_file=gjf_file,
            checkpoint_file=chk_file,
            job_title=f"{name} Counterpoise Calculation",
            functional=functional,
            basis_set=basis_set,
            dispersion=dispersion,
            mem=mem,
            nproc=nproc
        )
        
        # 运行计算
        print(f"开始运行Gaussian Counterpoise计算...")
        print(f"注意: 该计算可能需要较长时间...")
        self.runner.run_gaussian(gjf_file, log_file, wait=wait)
        
        if wait:
            # 检查计算结果
            status = self.runner.check_calculation_status(log_file)
            if status['success']:
                print(f"✓ 复合物优化成功完成")
            else:
                print(f"✗ 复合物优化失败: {status.get('error_message', 'Unknown error')}")
        
        return {
            'gjf': gjf_file,
            'chk': os.path.join(self.complex_dir, chk_file),
            'log': log_file,
            'name': name
        }
    
    def extract_and_save_results(
        self,
        complex_log: str,
        output_name: str = "results"
    ) -> Dict[str, any]:
        """
        提取并保存计算结果
        
        Args:
            complex_log: 复合物计算输出文件
            output_name: 结果文件基础名称
            
        Returns:
            结果字典
        """
        print(f"\n{'='*60}")
        print(f"步骤: 提取计算结果")
        print(f"{'='*60}")
        
        extractor = ResultExtractor(complex_log)
        
        # 提取Counterpoise结果
        results = extractor.extract_counterpoise_results()
        
        # 生成文本报告
        txt_report = os.path.join(self.results_dir, f"{output_name}.txt")
        extractor.generate_summary_report(txt_report)
        print(f"✓ 文本报告已保存: {txt_report}")
        
        # 保存JSON格式结果
        json_report = os.path.join(self.results_dir, f"{output_name}.json")
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON结果已保存: {json_report}")
        
        # 打印关键结果
        print(f"\n关键结果:")
        print(f"  相互作用能 (BSSE校正): {results['complexation_energy_corrected']:.2f} kcal/mol")
        print(f"  BSSE能量: {results['bsse_energy']:.6f} Hartree")
        print(f"  BSSE能量: {results['bsse_energy'] * 627.509:.2f} kcal/mol")
        
        return results
    
    def run_full_pipeline(
        self,
        molecule_a_file: str,
        molecule_b_file: str,
        name_a: str = "molecule_a",
        name_b: str = "molecule_b",
        functional: str = "B3LYP",
        basis_set: str = "6-311++G(d,p)",
        dispersion: str = "GD3BJ",
        mem: str = "100GB",
        nproc: int = 96,
        use_docking: bool = True,
        docking_exhaustiveness: int = 8
    ) -> Dict[str, any]:
        """
        运行完整的相互作用能计算流程
        
        Args:
            molecule_a_file: 分子A的结构文件(.xyz, .pdb等)
            molecule_b_file: 分子B的结构文件
            name_a: 分子A的名称
            name_b: 分子B的名称
            functional: 泛函
            basis_set: 基组
            dispersion: 色散校正
            mem: 内存
            nproc: CPU核心数
            use_docking: 是否使用Vina对接获取初始构象
            docking_exhaustiveness: 对接精度
            
        Returns:
            完整的结果字典
        """
        print("\n" + "="*80)
        print("分子间相互作用能自动化计算流程")
        print("="*80)
        
        # 读取输入结构
        print("\n读取输入结构...")
        struct_a = StructureParser()
        struct_b = StructureParser()
        
        # 根据文件扩展名选择读取方法
        ext_a = os.path.splitext(molecule_a_file)[1].lower()
        ext_b = os.path.splitext(molecule_b_file)[1].lower()
        
        if ext_a == '.xyz':
            struct_a.read_xyz(molecule_a_file)
        elif ext_a == '.pdb':
            struct_a.read_pdb(molecule_a_file)
        else:
            raise ValueError(f"不支持的文件格式: {ext_a}")
        
        if ext_b == '.xyz':
            struct_b.read_xyz(molecule_b_file)
        elif ext_b == '.pdb':
            struct_b.read_pdb(molecule_b_file)
        else:
            raise ValueError(f"不支持的文件格式: {ext_b}")
        
        print(f"✓ 分子A: {struct_a.get_atom_count()} 个原子")
        print(f"✓ 分子B: {struct_b.get_atom_count()} 个原子")
        
        # 步骤1: 优化单体A
        monomer_a_files = self.optimize_monomer(
            struct_a, name_a, functional, basis_set, dispersion, mem, nproc
        )
        
        # 步骤2: 优化单体B
        monomer_b_files = self.optimize_monomer(
            struct_b, name_b, functional, basis_set, dispersion, mem, nproc
        )
        
        # 从优化输出中获取优化后的结构
        print("\n提取优化后的单体结构...")
        opt_struct_a = StructureParser()
        opt_struct_a.read_gaussian_output(monomer_a_files['log'])
        
        opt_struct_b = StructureParser()
        opt_struct_b.read_gaussian_output(monomer_b_files['log'])
        
        # 步骤3: 分子对接（可选）
        if use_docking:
            complex_struct, docking_results = self.dock_molecules(
                opt_struct_a,
                opt_struct_b,
                exhaustiveness=docking_exhaustiveness
            )
            
            # 从对接后的复合物中分离两个片段
            # 注意：这里简化处理，实际应用中可能需要更复杂的片段分离逻辑
            frag_a = opt_struct_a
            frag_b = opt_struct_b
        else:
            # 不使用对接，直接使用优化后的单体
            frag_a = opt_struct_a
            frag_b = opt_struct_b
        
        # 步骤4: 优化复合物
        complex_files = self.optimize_complex(
            frag_a,
            frag_b,
            name="complex",
            functional=functional,
            basis_set=basis_set,
            dispersion=dispersion,
            mem=mem,
            nproc=nproc
        )
        
        # 步骤5: 提取结果
        final_results = self.extract_and_save_results(
            complex_files['log'],
            output_name="interaction_energy_results"
        )
        
        print("\n" + "="*80)
        print("计算流程完成!")
        print("="*80)
        
        return final_results
