# MEPS 快速开始指南

本指南将帮助你在5分钟内开始使用MEPS计算分子间相互作用能。

## 1. 环境安装

### 方法A: 自动安装（推荐）

```bash
# 进入项目目录
cd /home/zhangsd/repos/MEPS

# 运行安装脚本
bash setup.sh

# 激活conda环境
conda activate meps
```

### 方法B: 手动安装

```bash
# 创建conda环境
conda env create -f environment.yml

# 激活环境
conda activate meps

# 验证安装
python tests/test_installation.py
```

## 2. 准备输入文件

你需要准备两个分子的结构文件，支持以下格式：
- XYZ格式 (推荐)
- PDB格式

### XYZ文件格式示例 (water.xyz)

```
3
Water molecule
O    0.000000    0.000000    0.000000
H    0.957000    0.000000    0.000000
H   -0.240000    0.927000    0.000000
```

## 3. 运行计算

### 方法1: 使用命令行脚本（最简单）

```bash
# 基本用法
python scripts/run_pipeline.py molecule_a.xyz molecule_b.xyz

# 指定分子名称
python scripts/run_pipeline.py benzene.xyz methane.xyz \
    --name_a benzene --name_b methane

# 自定义计算参数
python scripts/run_pipeline.py mol_a.xyz mol_b.xyz \
    --functional M06-2X \
    --basis "def2-TZVP" \
    --nproc 48 \
    --mem "50GB"

# 查看所有选项
python scripts/run_pipeline.py --help
```

### 方法2: 使用Python API

创建一个Python脚本 `my_calculation.py`:

```python
import sys
sys.path.insert(0, './src')

from gaussian_runner import InteractionEnergyPipeline

# 初始化
pipeline = InteractionEnergyPipeline(
    gaussian_root="/opt/share/gaussian/g16",
    work_dir="./my_calculations"
)

# 运行计算
results = pipeline.run_full_pipeline(
    molecule_a_file="molecule_a.xyz",
    molecule_b_file="molecule_b.xyz",
    name_a="mol_a",
    name_b="mol_b"
)

# 查看结果
print(f"相互作用能: {results['complexation_energy_corrected']:.2f} kcal/mol")
print(f"BSSE能量: {results['bsse_energy']:.6f} Hartree")
```

运行:
```bash
python my_calculation.py
```

## 4. 查看结果

计算完成后，结果保存在工作目录中：

```
meps_calculations/
├── monomers/              # 单体优化结果
│   ├── molecule_a.gjf
│   ├── molecule_a.log
│   ├── molecule_b.gjf
│   └── molecule_b.log
├── complex/               # 复合物计算结果
│   ├── complex.gjf
│   └── complex.log
└── results/               # 提取的结果
    ├── interaction_energy_results.txt   # 文本报告
    └── interaction_energy_results.json  # JSON数据
```

### 文本报告示例

```
================================================================================
分子间相互作用能计算结果报告
================================================================================

【优化过程摘要】
  收敛状态: 已收敛
  优化步数: 15
  虚频检查: 无虚频
  最终能量: -272.86830628 Hartree

【相互作用能结果】
  相互作用能 (未校正): 3.78 kcal/mol
  相互作用能 (BSSE校正后): 4.03 kcal/mol
  BSSE能量: 0.00024039 Hartree
            0.15 kcal/mol
  CP校正能量: -272.86830628 Hartree
```

## 5. 常见问题

### Q1: Gaussian没有安装在默认位置怎么办？

使用 `--gaussian_root` 参数指定路径：
```bash
python scripts/run_pipeline.py mol_a.xyz mol_b.xyz \
    --gaussian_root /your/gaussian/path
```

### Q2: 计算需要多长时间？

- 小分子(< 20原子): 几分钟到几十分钟
- 中等分子(20-50原子): 几小时
- 大分子(> 50原子): 可能需要数小时到数天

时间取决于：
- 分子大小
- 基组选择
- 是否计算频率
- 可用CPU核心数

### Q3: 如何不使用分子对接？

添加 `--no-docking` 参数：
```bash
python scripts/run_pipeline.py mol_a.xyz mol_b.xyz --no-docking
```

### Q4: 计算失败怎么办？

1. 检查Gaussian日志文件中的错误信息
2. 尝试减小基组或使用更少的CPU核心
3. 确保输入分子结构合理
4. 查看 `results/*.txt` 中的错误报告

### Q5: 如何选择合适的泛函和基组？

| 目的 | 推荐设置 |
|-----|---------|
| 快速测试 | B3LYP/6-31G(d,p) |
| 常规计算 | B3LYP/6-311++G(d,p) + GD3BJ |
| 高精度 | M06-2X/def2-TZVP |

## 6. 进阶使用

### 批量计算

创建脚本 `batch_calculation.py`:

```python
import sys
sys.path.insert(0, './src')

from gaussian_runner import InteractionEnergyPipeline

# 定义分子对列表
pairs = [
    ("benzene.xyz", "methane.xyz", "benzene", "methane"),
    ("benzene.xyz", "water.xyz", "benzene", "water"),
    # 添加更多...
]

# 批量计算
for mol_a, mol_b, name_a, name_b in pairs:
    print(f"\n计算 {name_a}-{name_b}...")
    
    pipeline = InteractionEnergyPipeline(
        work_dir=f"./batch/{name_a}_{name_b}"
    )
    
    results = pipeline.run_full_pipeline(
        molecule_a_file=mol_a,
        molecule_b_file=mol_b,
        name_a=name_a,
        name_b=name_b
    )
    
    print(f"结果: {results['complexation_energy_corrected']:.2f} kcal/mol")
```

### 分步控制

如果需要更精细的控制，可以分步执行：

```python
# 1. 优化单体
monomer_a = pipeline.optimize_monomer(structure_a, "mol_a")
monomer_b = pipeline.optimize_monomer(structure_b, "mol_b")

# 2. 对接
complex_struct, docking = pipeline.dock_molecules(opt_a, opt_b)

# 3. 优化复合物
complex_files = pipeline.optimize_complex(opt_a, opt_b)

# 4. 提取结果
results = pipeline.extract_and_save_results(complex_files['log'])
```

## 7. 获取帮助

- 查看完整文档: `README.md`
- 运行示例: `python examples/tutorial_example.py`
- 查看教程: `Gaussian+Multiwfn计算ΔE_int教程.md`
- 检查安装: `python tests/test_installation.py`

## 8. 引用

如果你在研究中使用了本工具，请引用相关的理论方法：

- Gaussian 16
- Boys-Bernardi Counterpoise方法
- 使用的密度泛函和基组
- AutoDock Vina (如果使用了对接功能)
