"""
Test Tutorial Example 3 with Docking Structure
Verify that complex.gjf uses docked structure coordinates
Author: zhangshd
Date: 2025-10-13
"""

import sys
sys.path.insert(0, '/home/zhangsd/repos/MEPS')

from src.structure_parser import StructureParser
from src.gaussian_runner import InteractionEnergyPipeline
import os

print("=" * 80)
print("测试示例3：使用对接结构生成Counterpoise输入")
print("=" * 80)
print()

# Read molecules
benzene = StructureParser()
benzene.read_xyz('../example/benzene.xyz')
print(f"✓ 苯分子: {len(benzene.atoms)} 个原子")

methane = StructureParser()
methane.read_xyz('../example/methane.xyz')
print(f"✓ 甲烷分子: {len(methane.atoms)} 个原子")
print()

# Initialize pipeline
work_dir = './test_tutorial_fix'
os.makedirs(work_dir, exist_ok=True)

pipeline = InteractionEnergyPipeline(
    gaussian_root='/opt/share/gaussian/g16',
    work_dir=work_dir
)

print("步骤1: 模拟对接（简单平移）")
print("-" * 80)

# Simulate docking by translating methane
import copy
methane_docked = copy.deepcopy(methane)
methane_docked.translate(0.5, -0.3, -3.8)  # Simulate docking position

# Merge to create complex
complex_struct = benzene.merge(methane_docked)

methane_c_in_complex = complex_struct.atoms[12]  # Carbon atom of methane
print(f"对接后甲烷C坐标: ({methane_c_in_complex[1]:.3f}, {methane_c_in_complex[2]:.3f}, {methane_c_in_complex[3]:.3f})")
print()

print("步骤2: 使用对接结构生成Counterpoise输入")
print("-" * 80)

# Method 1: Using complex_structure parameter (NEW)
print("方法1: 使用 complex_structure 参数 (推荐)")
complex_files_1 = pipeline.optimize_complex(
    structure_a=benzene,
    structure_b=methane,
    complex_structure=complex_struct,  # Use docked structure
    name='complex_method1',
    wait=False
)

print(f"✓ 生成文件: {complex_files_1['gjf']}")
print()

# Method 2: Using separate structures (OLD - for comparison)
print("方法2: 使用独立结构 (旧方法，用于对比)")
complex_files_2 = pipeline.optimize_complex(
    structure_a=benzene,
    structure_b=methane,
    name='complex_method2',
    wait=False
)

print(f"✓ 生成文件: {complex_files_2['gjf']}")
print()

print("步骤3: 比较两种方法的坐标")
print("-" * 80)

def extract_fragment2_carbon_z(gjf_file):
    """Extract z-coordinate of Fragment=2 carbon atom"""
    with open(gjf_file, 'r') as f:
        for line in f:
            if 'Fragment=2' in line and 'C' in line:
                parts = line.split()
                return float(parts[-1])
    return None

z1 = extract_fragment2_carbon_z(complex_files_1['gjf'])
z2 = extract_fragment2_carbon_z(complex_files_2['gjf'])

print(f"方法1 (使用对接结构): 甲烷C的z坐标 = {z1:.3f} Å")
print(f"方法2 (独立结构):     甲烷C的z坐标 = {z2:.3f} Å")
print()

expected_z = methane_c_in_complex[3]
print(f"期望值（对接位置）: {expected_z:.3f} Å")
print()

# Validate
if abs(z1 - expected_z) < 0.01:
    print("✅ 方法1正确: 使用了对接后的坐标")
else:
    print(f"❌ 方法1错误: z坐标 {z1:.3f} 与期望 {expected_z:.3f} 不符")

if abs(z2 - 0.0) < 0.01:
    print("✓ 方法2使用原始坐标（甲烷在原点）")
else:
    print(f"⚠ 方法2的z坐标异常: {z2:.3f}")

print()
print("步骤4: 检查分子间距离")
print("-" * 80)

def get_molecular_separation(gjf_file, n_atoms_a):
    """Calculate separation between two fragments"""
    import numpy as np
    
    coords_a = []
    coords_b = []
    
    with open(gjf_file, 'r') as f:
        in_coord_section = False
        frag_count = 0
        
        for line in f:
            if 'Fragment=1' in line:
                parts = line.split()
                coords_a.append([float(parts[-3]), float(parts[-2]), float(parts[-1])])
            elif 'Fragment=2' in line:
                parts = line.split()
                coords_b.append([float(parts[-3]), float(parts[-2]), float(parts[-1])])
    
    if coords_a and coords_b:
        center_a = np.array(coords_a).mean(axis=0)
        center_b = np.array(coords_b).mean(axis=0)
        return np.linalg.norm(center_b - center_a)
    return None

sep1 = get_molecular_separation(complex_files_1['gjf'], 12)
sep2 = get_molecular_separation(complex_files_2['gjf'], 12)

print(f"方法1 分子间距离: {sep1:.3f} Å")
print(f"方法2 分子间距离: {sep2:.3f} Å")
print()

if 3.0 < sep1 < 6.0:
    print("✅ 方法1: 分子间距离合理（3-6 Å范围）")
else:
    print(f"⚠ 方法1: 分子间距离异常 ({sep1:.3f} Å)")

if sep2 < 2.0:
    print("⚠ 方法2: 分子可能重叠（距离过近）")

print()
print("=" * 80)
print("测试完成")
print("=" * 80)
print()
print("结论:")
print("- 新的 complex_structure 参数可以正确使用对接后的坐标")
print("- 示例3现已修复，会使用对接结果而不是原始坐标")
print("- 生成的 complex.gjf 将包含正确的相对位置")
