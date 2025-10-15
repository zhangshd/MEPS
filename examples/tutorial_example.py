#!/usr/bin/env python3
"""
使用教程示例 - 计算苯-甲烷复合物的相互作用能
Author: zhangshd
Date: 2025-10-12

本示例演示如何使用MEPS包计算两个分子之间的相互作用能。
示例使用苯(benzene)和甲烷(methane)作为研究对象。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from structure_parser import StructureParser
from gaussian_runner import InteractionEnergyPipeline


def example_1_basic_usage():
    """
    示例1: 基本用法 - 从XYZ文件计算相互作用能
    
    这个示例展示了最简单的使用方式，只需要提供两个分子的XYZ文件。
    """
    print("\n" + "="*80)
    print("示例1: 基本用法")
    print("="*80)
    
    # 初始化流程管理器
    pipeline = InteractionEnergyPipeline(
        gaussian_root="/opt/share/gaussian/g16",
        work_dir="./example_calculations/basic"
    )
    
    # 假设我们有两个XYZ文件
    # 这里使用相对路径，实际使用时替换为你的文件路径
    benzene_file = "../example/benzene.xyz"
    methane_file = "../example/methane.xyz"
    
    # 运行完整流程
    results = pipeline.run_full_pipeline(
        molecule_a_file=benzene_file,
        molecule_b_file=methane_file,
        name_a="benzene",
        name_b="methane"
    )
    
    # 打印结果
    print("\n计算完成!")
    print(f"相互作用能: {results['complexation_energy_corrected']:.2f} kcal/mol")


def example_2_custom_parameters():
    """
    示例2: 自定义计算参数
    
    这个示例展示如何自定义泛函、基组等计算参数。
    """
    print("\n" + "="*80)
    print("示例2: 自定义计算参数")
    print("="*80)
    
    pipeline = InteractionEnergyPipeline(
        gaussian_root="/opt/share/gaussian/g16",
        work_dir="./example_calculations/custom_params"
    )
    
    # 使用M06-2X泛函和def2-TZVP基组
    results = pipeline.run_full_pipeline(
        molecule_a_file="../example/benzene.xyz",
        molecule_b_file="../example/methane.xyz",
        name_a="benzene",
        name_b="methane",
        functional="M06-2X",
        basis_set="def2-TZVP",
        dispersion="",  # M06-2X已包含色散校正
        mem="50GB",
        nproc=48
    )
    
    print(f"\n使用M06-2X/def2-TZVP计算的相互作用能: {results['complexation_energy_corrected']:.2f} kcal/mol")


def example_3_step_by_step():
    """
    示例3: 分步执行流程
    
    这个示例展示如何分步执行计算流程，提供更多控制和中间结果检查的机会。
    """
    print("\n" + "="*80)
    print("示例3: 分步执行流程")
    print("="*80)
    
    # 初始化
    pipeline = InteractionEnergyPipeline(
        gaussian_root="/opt/share/gaussian/g16",
        work_dir="./example_calculations/step_by_step"
    )
    
    # 读取分子结构
    print("\n步骤1: 读取分子结构")
    benzene = StructureParser()
    benzene.read_xyz("../example/benzene.xyz")
    print(f"  苯分子包含 {benzene.get_atom_count()} 个原子")
    
    methane = StructureParser()
    methane.read_xyz("../example/methane.xyz")
    print(f"  甲烷分子包含 {methane.get_atom_count()} 个原子")
    
    # 步骤2: 优化单体
    print("\n步骤2: 优化单体分子")
    benzene_files = pipeline.optimize_monomer(
        structure=benzene,
        name="benzene",
        functional="B3LYP",
        basis_set="6-311++G(d,p)",
        dispersion="GD3BJ"
    )
    print(f"  苯优化完成: {benzene_files['log']}")
    
    methane_files = pipeline.optimize_monomer(
        structure=methane,
        name="methane",
        functional="B3LYP",
        basis_set="6-311++G(d,p)",
        dispersion="GD3BJ"
    )
    print(f"  甲烷优化完成: {methane_files['log']}")
    
    # 步骤3: 获取优化后的结构
    print("\n步骤3: 提取优化后的结构")
    opt_benzene = StructureParser()
    opt_benzene.read_gaussian_output(benzene_files['log'])
    
    opt_methane = StructureParser()
    opt_methane.read_gaussian_output(methane_files['log'])
    
    # 步骤4: 分子对接
    print("\n步骤4: 分子对接")
    complex_struct, docking_results = pipeline.dock_molecules(
        structure_a=opt_benzene,
        structure_b=opt_methane,
        exhaustiveness=8
    )
    print(f"  对接完成，最佳亲和力: {docking_results['best_affinity']:.2f} kcal/mol")
    
    # 步骤5: 优化复合物（使用对接后的结构）
    print("\n步骤5: 优化复合物并计算相互作用能")
    complex_files = pipeline.optimize_complex(
        structure_a=opt_benzene,  # 提供原始结构以确定片段分割点
        structure_b=opt_methane,  # 提供原始结构以设置电荷和多重度
        complex_structure=complex_struct,  # 使用对接后的复合物结构
        name="complex",
        functional="B3LYP",
        basis_set="6-311++G(d,p)",
        dispersion="GD3BJ"
    )
    
    # 步骤6: 提取结果
    print("\n步骤6: 提取和分析结果")
    final_results = pipeline.extract_and_save_results(
        complex_log=complex_files['log'],
        output_name="benzene_methane_results"
    )
    
    print("\n最终结果:")
    print(f"  相互作用能 (BSSE校正): {final_results['complexation_energy_corrected']:.2f} kcal/mol")
    print(f"  BSSE能量: {final_results['bsse_energy']:.6f} Hartree")


def example_4_without_docking():
    """
    示例4: 不使用分子对接
    
    某些情况下，你可能已经有了复合物的初始构象，
    或者想要使用简单的几何组合而不是对接。
    """
    print("\n" + "="*80)
    print("示例4: 不使用分子对接")
    print("="*80)
    
    pipeline = InteractionEnergyPipeline(
        gaussian_root="/opt/share/gaussian/g16",
        work_dir="./example_calculations/no_docking"
    )
    
    # 设置use_docking=False
    results = pipeline.run_full_pipeline(
        molecule_a_file="../example/benzene.xyz",
        molecule_b_file="../example/methane.xyz",
        name_a="benzene",
        name_b="methane",
        use_docking=False  # 不使用对接
    )
    
    print(f"\n不使用对接计算的相互作用能: {results['complexation_energy_corrected']:.2f} kcal/mol")


def example_5_batch_calculation():
    """
    示例5: 批量计算多对分子
    
    这个示例展示如何批量处理多对分子的相互作用能计算。
    """
    print("\n" + "="*80)
    print("示例5: 批量计算")
    print("="*80)
    
    # 定义要计算的分子对列表
    molecule_pairs = [
        ("benzene.xyz", "methane.xyz", "benzene", "methane"),
        # 可以添加更多分子对
        # ("molecule_c.xyz", "molecule_d.xyz", "mol_c", "mol_d"),
    ]
    
    results_summary = []
    
    for mol_a, mol_b, name_a, name_b in molecule_pairs:
        print(f"\n处理分子对: {name_a} + {name_b}")
        
        # 为每对分子创建独立的工作目录
        work_dir = f"./example_calculations/batch/{name_a}_{name_b}"
        
        pipeline = InteractionEnergyPipeline(
            gaussian_root="/opt/share/gaussian/g16",
            work_dir=work_dir
        )
        
        try:
            results = pipeline.run_full_pipeline(
                molecule_a_file=f"../example/{mol_a}",
                molecule_b_file=f"../example/{mol_b}",
                name_a=name_a,
                name_b=name_b
            )
            
            results_summary.append({
                'pair': f"{name_a}-{name_b}",
                'energy': results['complexation_energy_corrected'],
                'bsse': results['bsse_energy']
            })
            
        except Exception as e:
            print(f"  错误: {e}")
            results_summary.append({
                'pair': f"{name_a}-{name_b}",
                'energy': None,
                'bsse': None,
                'error': str(e)
            })
    
    # 打印汇总结果
    print("\n" + "="*80)
    print("批量计算结果汇总")
    print("="*80)
    print(f"{'分子对':<20} {'相互作用能 (kcal/mol)':<25} {'BSSE (Hartree)':<20}")
    print("-"*80)
    for result in results_summary:
        if result['energy'] is not None:
            print(f"{result['pair']:<20} {result['energy']:>20.2f}     {result['bsse']:>15.6f}")
        else:
            print(f"{result['pair']:<20} {'计算失败':<25}")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "="*80)
    print("MEPS使用教程示例")
    print("="*80)
    print("\n本脚本包含5个示例:")
    print("  1. 基本用法")
    print("  2. 自定义计算参数")
    print("  3. 分步执行流程")
    print("  4. 不使用分子对接")
    print("  5. 批量计算多对分子")
    print("\n请选择要运行的示例 (1-5)，或输入 0 运行所有示例:")
    
    try:
        choice = int(input("\n请输入选择: "))
    except (ValueError, KeyboardInterrupt):
        print("\n已取消")
        return
    
    examples = {
        1: example_1_basic_usage,
        2: example_2_custom_parameters,
        3: example_3_step_by_step,
        4: example_4_without_docking,
        5: example_5_batch_calculation
    }
    
    if choice == 0:
        # 运行所有示例
        for i in range(1, 6):
            try:
                examples[i]()
            except Exception as e:
                print(f"\n示例{i}运行出错: {e}")
                import traceback
                traceback.print_exc()
    elif choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"\n示例运行出错: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n无效的选择")


if __name__ == '__main__':
    main()
