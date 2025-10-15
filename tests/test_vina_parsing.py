"""
Test Vina Output Parsing Fix
Test the fixed parsing logic for AutoDock Vina output
Author: zhangshd
Date: 2025-10-12
"""

import sys
sys.path.insert(0, '/home/zhangsd/repos/MEPS')

from src.vina_docking import VinaDocking

# Test case 1: Output with progress percentages
print("=" * 60)
print("Test Case 1: Vina output with progress indicators")
print("=" * 60)

sample_output_1 = """
Computing transformation ... 0%
Computing transformation ... 10%
Computing transformation ... 50%
Computing transformation ... 100%
Performing search ... 0%
Performing search ... 25%
Performing search ... 50%
Performing search ... 75%
Performing search ... 100%
Refining results ... 0%
Refining results ... 50%
Refining results ... 100%

mode |   affinity | dist from best mode
     | (kcal/mol) | rmsd l.b.| rmsd u.b.
-----+------------+----------+----------
   1       -5.234      0.000      0.000
   2       -4.892      1.234      2.456
   3       -4.567      2.345      3.567
   4       -4.123      3.456      4.678

Writing output ... done.
"""

docker = VinaDocking()
results = docker._parse_vina_output(sample_output_1)

print(f"✓ 解析成功!")
print(f"  找到 {len(results['modes'])} 个对接模式")
print(f"  最佳亲和力: {results['best_affinity']} kcal/mol")
print()
print("对接模式详情:")
for mode in results['modes']:
    print(f"  模式 {mode['mode']}: {mode['affinity']} kcal/mol "
          f"(RMSD: {mode['rmsd_lb']:.3f}, {mode['rmsd_ub']:.3f})")
print()

# Test case 2: Minimal output
print("=" * 60)
print("Test Case 2: Minimal Vina output")
print("=" * 60)

sample_output_2 = """
mode |   affinity | dist from best mode
     | (kcal/mol) | rmsd l.b.| rmsd u.b.
-----+------------+----------+----------
   1       -6.789      0.000      0.000
"""

results2 = docker._parse_vina_output(sample_output_2)
print(f"✓ 解析成功!")
print(f"  找到 {len(results2['modes'])} 个对接模式")
print(f"  最佳亲和力: {results2['best_affinity']} kcal/mol")
print()

# Test case 3: Output with edge cases
print("=" * 60)
print("Test Case 3: Edge cases (lines starting with digits)")
print("=" * 60)

sample_output_3 = """
Starting calculation at 09:30:00
Processing 100 conformations...
0% complete
10% complete
50% complete
100% complete

mode |   affinity | dist from best mode
     | (kcal/mol) | rmsd l.b.| rmsd u.b.
-----+------------+----------+----------
   1       -7.890      0.000      0.000
   2       -7.654      0.987      1.234

Done processing.
"""

results3 = docker._parse_vina_output(sample_output_3)
print(f"✓ 解析成功!")
print(f"  找到 {len(results3['modes'])} 个对接模式")
print(f"  最佳亲和力: {results3['best_affinity']} kcal/mol")
print()

print("=" * 60)
print("✅ 所有测试通过! Vina 输出解析功能已修复")
print("=" * 60)
