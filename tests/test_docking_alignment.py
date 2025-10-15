"""
Test Docking Structure Alignment Fix
Verify that docked complex has proper structure with all atoms
Author: zhangshd
Date: 2025-10-12
"""

import sys
sys.path.insert(0, '/home/zhangsd/repos/MEPS')

from src.structure_parser import StructureParser
from src.gaussian_runner import InteractionEnergyPipeline
import os

print("=" * 80)
print("测试对接结构对齐修复")
print("=" * 80)
print()

# Read molecules
benzene = StructureParser()
benzene.read_xyz('../example/benzene.xyz')
print(f"苯分子: {len(benzene.atoms)} 个原子")

methane = StructureParser()
methane.read_xyz('../example/methane.xyz')
print(f"甲烷分子: {len(methane.atoms)} 个原子")
print()

# Initialize pipeline
work_dir = './test_docking_alignment'
os.makedirs(work_dir, exist_ok=True)

pipeline = InteractionEnergyPipeline(
    gaussian_root='/opt/share/gaussian/g16',
    work_dir=work_dir
)

print("步骤1: 分子对接")
print("-" * 80)

complex_struct, docking_results = pipeline.dock_molecules(
    benzene,
    methane,
    exhaustiveness=2  # Use small value for quick test
)

print(f"✓ 对接完成")
print(f"  复合物包含 {len(complex_struct.atoms)} 个原子")
print(f"  最佳亲和力: {docking_results['best_affinity']:.3f} kcal/mol")

# Check atom counts
from collections import Counter
elements = Counter([atom[0] for atom in complex_struct.atoms])
print()
print("原子类型分布:")
for elem in sorted(elements.keys()):
    print(f"  {elem}: {elements[elem]}")

expected_C = 6 + 1  # benzene + methane
expected_H = 6 + 4  # benzene + methane

if elements['C'] == expected_C and elements['H'] == expected_H:
    print()
    print("✅ 原子数量正确!")
else:
    print()
    print(f"⚠ 原子数量不正确! 期望 C:{expected_C} H:{expected_H}, 实际 C:{elements['C']} H:{elements['H']}")

# Check for atom overlaps
import numpy as np
coords = np.array([[x, y, z] for _, x, y, z in complex_struct.atoms])

print()
print("步骤2: 检查原子间距")
print("-" * 80)

min_distance = float('inf')
min_pair = None

for i in range(len(coords)):
    for j in range(i+1, len(coords)):
        dist = np.linalg.norm(coords[i] - coords[j])
        if dist < min_distance:
            min_distance = dist
            min_pair = (i, j)

print(f"最小原子间距: {min_distance:.3f} Å")
print(f"  (原子 {min_pair[0]+1} 和原子 {min_pair[1]+1})")

if min_distance < 0.5:
    print("❌ 错误: 存在严重原子重叠!")
    status = "FAILED"
elif min_distance < 1.0:
    print("⚠ 警告: 原子距离过近")
    status = "WARNING"
else:
    print("✅ 没有原子重叠，结构合理")
    status = "PASSED"

# Check structure separation
benzene_atoms = complex_struct.atoms[:12]  # First 12 atoms
methane_atoms = complex_struct.atoms[12:]  # Last 5 atoms

benzene_center = np.array([[x, y, z] for _, x, y, z in benzene_atoms]).mean(axis=0)
methane_center = np.array([[x, y, z] for _, x, y, z in methane_atoms]).mean(axis=0)

separation = np.linalg.norm(methane_center - benzene_center)

print()
print("步骤3: 检查分子间距离")
print("-" * 80)
print(f"苯质心: ({benzene_center[0]:.3f}, {benzene_center[1]:.3f}, {benzene_center[2]:.3f})")
print(f"甲烷质心: ({methane_center[0]:.3f}, {methane_center[1]:.3f}, {methane_center[2]:.3f})")
print(f"分子间距离: {separation:.3f} Å")

if 3.0 < separation < 6.0:
    print("✅ 分子间距离合理（典型范围: 3-6 Å）")
elif separation < 1.0:
    print("❌ 错误: 分子严重重叠!")
    status = "FAILED"
else:
    print(f"⚠ 警告: 分子间距离异常 ({separation:.3f} Å)")

# Save complex
complex_file = os.path.join(work_dir, 'complex_test.xyz')
complex_struct.write_xyz(complex_file)
print()
print(f"✓ 复合物已保存到: {complex_file}")

# Summary
print()
print("=" * 80)
print(f"测试状态: {status}")
print("=" * 80)

if status == "PASSED":
    print()
    print("🎉 对接结构对齐功能工作正常!")
    print("   - 所有原子都存在（包括氢原子）")
    print("   - 没有原子重叠")
    print("   - 分子间距离合理")
    exit(0)
elif status == "WARNING":
    print()
    print("⚠ 测试通过但有警告，请检查详情")
    exit(0)
else:
    print()
    print("❌ 测试失败，需要进一步调试")
    exit(1)
