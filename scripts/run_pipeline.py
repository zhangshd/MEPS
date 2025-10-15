#!/usr/bin/env python3
"""
MEPS主流程脚本 - 分子间相互作用能自动化计算
Author: zhangshd
Date: 2025-10-12

使用示例:
    python run_pipeline.py molecule_a.xyz molecule_b.xyz --name_a benzene --name_b methane
"""

import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gaussian_runner import InteractionEnergyPipeline


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='分子间相互作用能自动化计算流程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python run_pipeline.py molecule_a.xyz molecule_b.xyz
  
  # 指定分子名称
  python run_pipeline.py benzene.xyz methane.xyz --name_a benzene --name_b methane
  
  # 自定义计算参数
  python run_pipeline.py mol_a.pdb mol_b.pdb --functional M06-2X --basis def2-TZVP
  
  # 不使用分子对接
  python run_pipeline.py mol_a.xyz mol_b.xyz --no-docking
        """
    )
    
    # 必选参数
    parser.add_argument(
        'molecule_a',
        help='分子A的结构文件 (支持.xyz, .pdb格式)'
    )
    parser.add_argument(
        'molecule_b',
        help='分子B的结构文件 (支持.xyz, .pdb格式)'
    )
    
    # 可选参数 - 分子信息
    parser.add_argument(
        '--name_a',
        default='molecule_a',
        help='分子A的名称 (默认: molecule_a)'
    )
    parser.add_argument(
        '--name_b',
        default='molecule_b',
        help='分子B的名称 (默认: molecule_b)'
    )
    
    # 可选参数 - 计算设置
    parser.add_argument(
        '--functional',
        default='B3LYP',
        choices=['B3LYP', 'M06-2X', 'wB97X-D', 'B2PLYP'],
        help='密度泛函理论方法 (默认: B3LYP)'
    )
    parser.add_argument(
        '--basis',
        default='6-311++G(d,p)',
        help='基组 (默认: 6-311++G(d,p))'
    )
    parser.add_argument(
        '--dispersion',
        default='GD3BJ',
        choices=['GD3', 'GD3BJ', 'None'],
        help='色散校正方法 (默认: GD3BJ)'
    )
    
    # 可选参数 - 计算资源
    parser.add_argument(
        '--mem',
        default='100GB',
        help='Gaussian计算内存 (默认: 100GB)'
    )
    parser.add_argument(
        '--nproc',
        type=int,
        default=96,
        help='Gaussian计算使用的CPU核心数 (默认: 96)'
    )
    
    # 可选参数 - 对接设置
    parser.add_argument(
        '--no-docking',
        action='store_true',
        help='不使用AutoDock Vina对接，直接使用优化后的单体构建复合物'
    )
    parser.add_argument(
        '--exhaustiveness',
        type=int,
        default=8,
        help='Vina对接的搜索精度 (默认: 8)'
    )
    
    # 可选参数 - 路径设置
    parser.add_argument(
        '--gaussian_root',
        default='/opt/share/gaussian/g16',
        help='Gaussian安装根目录 (默认: /opt/share/gaussian/g16)'
    )
    parser.add_argument(
        '--work_dir',
        default='./meps_calculations',
        help='工作目录 (默认: ./meps_calculations)'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.molecule_a):
        print(f"错误: 找不到分子A的文件: {args.molecule_a}")
        sys.exit(1)
    
    if not os.path.exists(args.molecule_b):
        print(f"错误: 找不到分子B的文件: {args.molecule_b}")
        sys.exit(1)
    
    # 处理色散校正参数
    dispersion = args.dispersion if args.dispersion != 'None' else ''
    
    # 初始化流程管理器
    try:
        pipeline = InteractionEnergyPipeline(
            gaussian_root=args.gaussian_root,
            work_dir=args.work_dir
        )
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("请检查Gaussian是否正确安装，路径是否正确")
        sys.exit(1)
    
    # 运行完整流程
    try:
        results = pipeline.run_full_pipeline(
            molecule_a_file=args.molecule_a,
            molecule_b_file=args.molecule_b,
            name_a=args.name_a,
            name_b=args.name_b,
            functional=args.functional,
            basis_set=args.basis,
            dispersion=dispersion,
            mem=args.mem,
            nproc=args.nproc,
            use_docking=not args.no_docking,
            docking_exhaustiveness=args.exhaustiveness
        )
        
        # 打印最终结果总结
        print("\n" + "="*80)
        print("计算结果总结")
        print("="*80)
        print(f"分子对: {args.name_a} + {args.name_b}")
        print(f"理论方法: {args.functional}/{args.basis}")
        if dispersion:
            print(f"色散校正: {dispersion}")
        print("-"*80)
        
        if results['complexation_energy_corrected'] is not None:
            print(f"\n相互作用能 (BSSE校正): {results['complexation_energy_corrected']:.2f} kcal/mol")
            print(f"相互作用能 (未校正):   {results['complexation_energy_raw']:.2f} kcal/mol")
            print(f"BSSE能量:             {results['bsse_energy']:.6f} Hartree")
            print(f"                      {results['bsse_energy'] * 627.509:.2f} kcal/mol")
            
            # 判断相互作用类型
            energy = results['complexation_energy_corrected']
            if energy < -5:
                interaction_type = "强吸引性相互作用"
            elif energy < -2:
                interaction_type = "中等吸引性相互作用"
            elif energy < 0:
                interaction_type = "弱吸引性相互作用"
            else:
                interaction_type = "排斥性相互作用"
            
            print(f"\n相互作用类型: {interaction_type}")
            
            # BSSE大小评估
            bsse_kcal = abs(results['bsse_energy'] * 627.509)
            if bsse_kcal > 3:
                print(f"\n⚠️  警告: BSSE较大 ({bsse_kcal:.2f} kcal/mol)")
                print("   建议使用更大的基组以获得更可靠的结果")
            elif bsse_kcal > 2:
                print(f"\n注意: BSSE中等 ({bsse_kcal:.2f} kcal/mol)")
                print("   结果基本可靠，但使用更大基组可能更好")
            else:
                print(f"\n✓ BSSE较小 ({bsse_kcal:.2f} kcal/mol)，结果可靠")
        else:
            print("\n⚠️  警告: 未能提取相互作用能结果")
            print("   请检查计算日志文件")
        
        print("\n详细结果已保存至:")
        print(f"  文本报告: {args.work_dir}/results/interaction_energy_results.txt")
        print(f"  JSON数据: {args.work_dir}/results/interaction_energy_results.json")
        print("="*80)
        
    except Exception as e:
        print(f"\n错误: 计算过程中出现异常")
        print(f"详细信息: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
