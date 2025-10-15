# 验证 Tutorial 对接坐标修复

## 快速验证

### 运行测试脚本
```bash
cd /home/zhangsd/repos/MEPS/tests
conda activate meps
python test_tutorial_docking_fix.py
```

预期输出：
```
✅ 方法1正确: 使用了对接后的坐标
✅ 方法1: 分子间距离合理（3-6 Å范围）
```

### 检查示例3生成的文件

运行示例3（可选，需要实际运行Gaussian）：
```bash
cd /home/zhangsd/repos/MEPS/examples
python tutorial_example.py
# 选择 3
```

检查生成的 complex.gjf：
```bash
cat example_calculations/step_by_step/complex/complex.gjf
```

**验证点**：
- ✅ Fragment=2 的 C 原子 **不在** 原点 (0, 0, 0)
- ✅ Fragment=2 的 z 坐标应该在 -3 到 -5 Å 范围
- ✅ 两个分子没有重叠

## 详细检查

### 检查1: 坐标使用

**正确的 complex.gjf**（使用对接坐标）：
```
C(Fragment=1)  -1.211  0.699  0.000  # 苯在原点附近
...
C(Fragment=2)   X.XXX  X.XXX -3.XXX  # 甲烷在对接位置（z<0）
```

**错误的 complex.gjf**（未使用对接）：
```
C(Fragment=1)  -1.211  0.699  0.000  # 苯在原点附近
...
C(Fragment=2)   0.000  0.000  0.000  # 甲烷在原点（与苯重叠！）
```

### 检查2: 分子间距离

使用Python快速检查：
```bash
cd /home/zhangsd/repos/MEPS
conda activate meps

python -c "
import numpy as np

# 读取 complex.gjf
with open('examples/example_calculations/step_by_step/complex/complex.gjf', 'r') as f:
    lines = f.readlines()

# 提取Fragment=1和Fragment=2的坐标
frag1_coords = []
frag2_coords = []

for line in lines:
    if 'Fragment=1' in line:
        parts = line.split()
        frag1_coords.append([float(parts[-3]), float(parts[-2]), float(parts[-1])])
    elif 'Fragment=2' in line:
        parts = line.split()
        frag2_coords.append([float(parts[-3]), float(parts[-2]), float(parts[-1])])

if frag1_coords and frag2_coords:
    center1 = np.array(frag1_coords).mean(axis=0)
    center2 = np.array(frag2_coords).mean(axis=0)
    distance = np.linalg.norm(center2 - center1)
    
    print(f'Fragment 1 中心: ({center1[0]:.3f}, {center1[1]:.3f}, {center1[2]:.3f})')
    print(f'Fragment 2 中心: ({center2[0]:.3f}, {center2[1]:.3f}, {center2[2]:.3f})')
    print(f'分子间距离: {distance:.3f} Å')
    print()
    
    if distance < 1.0:
        print('❌ 错误: 分子重叠（距离 < 1.0 Å）')
        print('   说明: 未使用对接坐标')
    elif 3.0 <= distance <= 6.0:
        print('✅ 正确: 分子间距离合理（3-6 Å）')
        print('   说明: 正确使用了对接坐标')
    else:
        print(f'⚠ 警告: 分子间距离异常（{distance:.3f} Å）')
"
```

## 常见问题

### Q1: 如何确认使用了对接结果？

**A**: 检查 Fragment=2 的第一个原子坐标：
```bash
grep "Fragment=2" complex.gjf | head -1
```

如果输出类似：
```
C(Fragment=2)   0.000  0.000  0.000
```
说明**未使用**对接结果（甲烷在原点）。

如果输出类似：
```
C(Fragment=2)   0.123 -0.456 -3.789
```
说明**正确使用**了对接结果。

### Q2: 旧代码会受影响吗？

**A**: 不会！修复是向后兼容的：
```python
# 旧代码仍然工作
complex_files = pipeline.optimize_complex(
    structure_a=benzene,
    structure_b=methane
)
```

### Q3: 如何使用新功能？

**A**: 添加 `complex_structure` 参数：
```python
# 对接
complex_struct, _ = pipeline.dock_molecules(benzene, methane)

# 使用对接结果
complex_files = pipeline.optimize_complex(
    structure_a=benzene,
    structure_b=methane,
    complex_structure=complex_struct  # 新增这一行
)
```

## 修复验证清单

- [ ] 运行 `test_tutorial_docking_fix.py` 测试通过
- [ ] Fragment=2 坐标不在原点 (0, 0, 0)
- [ ] 分子间距离在 3-6 Å 范围
- [ ] 所有原子数量正确（17个原子）
- [ ] 没有原子重叠警告

如果所有检查都通过，说明修复成功！✅

## 相关文档

- 详细修复报告: `docs/TUTORIAL_DOCKING_FIX.md`
- 测试报告: `TEST_REPORT.md` (2.9节)
- 对接结构对齐: `docs/DOCKING_ALIGNMENT_FIX.md`
- Vina输出解析: `docs/VINA_PARSING_FIX.md`
