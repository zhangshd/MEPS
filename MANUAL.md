# MEPS 使用手册

## 目录

1. [项目概述](#项目概述)
2. [工作流程](#工作流程)
3. [模块说明](#模块说明)
4. [使用示例](#使用示例)
5. [参数调优](#参数调优)
6. [常见问题](#常见问题)
7. [故障排除](#故障排除)

## 项目概述

MEPS (Molecular Interaction Energy Pipeline System) 是一个完整的分子间相互作用能自动化计算流程，整合了以下功能：

- ✅ 单体分子结构优化 (Gaussian)
- ✅ 分子对接获取初始构象 (AutoDock Vina)
- ✅ 复合物优化与Counterpoise校正 (Gaussian)
- ✅ 自动提取相互作用能和BSSE能量
- ✅ 批量计算支持
- ✅ 结果可视化和报告生成

## 工作流程

```
输入分子A, B (XYZ/PDB)
    ↓
单体结构优化 (Gaussian)
    ↓
分子对接 (Vina, 可选)
    ↓
复合物优化 + Counterpoise校正 (Gaussian)
    ↓
提取相互作用能、BSSE等结果
    ↓
生成报告 (TXT + JSON)
```

### 详细步骤说明

#### 步骤1: 单体优化

对两个分子分别进行几何优化和频率计算：
- 优化得到能量最低构象
- 频率计算确认无虚频（真实极小点）
- 获得热力学校正数据

关键输出：
- 优化后的结构坐标
- SCF能量
- 零点能、焓、自由能等

#### 步骤2: 分子对接（可选）

使用AutoDock Vina进行分子对接：
- 自动计算搜索盒大小和位置
- 生成多个对接姿态
- 选择最佳亲和力的构象

优势：
- 自动寻找合理的复合物初始构象
- 适用于不知道分子如何相互作用的情况

何时跳过：
- 已知复合物结构
- 想要测试特定相对位置
- 计算资源有限

#### 步骤3: 复合物优化

使用Counterpoise方法计算相互作用能：
- 自动生成两片段(Fragment)输入文件
- 执行带BSSE校正的优化
- 每步优化都计算CP校正能量

关键参数：
- `Counterpoise=2`: 两个片段的BSSE校正
- 电荷和多重度格式：总电荷 总多重度 片段1电荷 片段1多重度 片段2电荷 片段2多重度

#### 步骤4: 结果提取

自动提取以下信息：
- 相互作用能（原始值和BSSE校正值）
- BSSE能量（Hartree和kcal/mol）
- 优化步骤的能量变化
- 收敛状态和虚频检查

## 模块说明

### 1. structure_parser.py - 分子结构解析模块

**主要功能:**
- 读取多种格式: XYZ, PDB, Gaussian输出
- 写入多种格式: XYZ, PDB, Gaussian坐标
- 结构操作: 平移、旋转、合并
- 几何分析: 质心、边界盒

**常用方法:**
```python
parser = StructureParser()
parser.read_xyz("molecule.xyz")          # 读取XYZ
parser.read_gaussian_output("opt.log")   # 从Gaussian输出读取优化结构
parser.write_pdb("output.pdb")           # 写入PDB

# 几何操作
center = parser.get_center_of_mass()     # 获取质心
parser.center_at_origin()                # 移动到原点
bbox = parser.get_bounding_box()         # 获取边界盒

# 合并分子
complex_parser = parser_a.merge(parser_b)
```

### 2. gaussian_io.py - Gaussian输入输出模块

**主要功能:**
- 生成单体优化输入文件
- 生成Counterpoise输入文件
- 解析Gaussian输出文件
- 提取能量和结构数据

**常用方法:**
```python
# 生成输入文件
gen = GaussianInputGenerator()
gen.generate_optimization_input(
    structure=parser,
    output_file="opt.gjf",
    checkpoint_file="opt.chk",
    job_title="Optimization",
    functional="B3LYP",
    basis_set="6-311++G(d,p)"
)

# 解析输出
parser = GaussianOutputParser("opt.log")
is_normal = parser.is_normal_termination()
energy = parser.get_scf_energy()
has_imag, num_imag = parser.check_imaginary_frequencies()
```

### 3. vina_docking.py - 分子对接模块

**主要功能:**
- 准备受体和配体PDBQT文件
- 自动计算搜索盒
- 运行Vina对接
- 提取最佳姿态

**常用方法:**
```python
docker = VinaDocking(work_dir="./vina_work")

# 完整对接流程
complex_struct, results = docker.dock_two_molecules(
    molecule_a=receptor_parser,
    molecule_b=ligand_parser,
    exhaustiveness=8
)

print(f"最佳亲和力: {results['best_affinity']} kcal/mol")
```

### 4. result_extractor.py - 结果提取模块

**主要功能:**
- 提取Counterpoise结果
- 提取优化摘要
- 生成文本报告
- 导出JSON数据

**常用方法:**
```python
extractor = ResultExtractor("complex.log")

# 提取结果
cp_results = extractor.extract_counterpoise_results()
print(f"相互作用能: {cp_results['complexation_energy_corrected']} kcal/mol")

# 生成报告
extractor.generate_summary_report("report.txt")
```

### 5. gaussian_runner.py - 计算管理模块

**主要功能:**
- 运行Gaussian计算
- 监控计算进度
- 转换chk到fchk
- 完整流程管理

**核心类:**
```python
# GaussianRunner - 基础运行器
runner = GaussianRunner(gaussian_root="/opt/share/gaussian/g16")
runner.run_gaussian("input.gjf", "output.log")
status = runner.check_calculation_status("output.log")

# InteractionEnergyPipeline - 完整流程
pipeline = InteractionEnergyPipeline(work_dir="./calculations")
results = pipeline.run_full_pipeline(
    molecule_a_file="mol_a.xyz",
    molecule_b_file="mol_b.xyz"
)
```

## 使用示例

### 示例1: 基本计算

```bash
# 使用命令行
python scripts/run_pipeline.py \
    data/input/benzene.xyz \
    data/input/methane.xyz \
    --name_a benzene \
    --name_b methane
```

### 示例2: 自定义参数

```bash
python scripts/run_pipeline.py \
    molecule_a.xyz molecule_b.xyz \
    --functional M06-2X \
    --basis "def2-TZVP" \
    --nproc 48 \
    --mem "50GB" \
    --no-docking
```

### 示例3: Python API

```python
import sys
sys.path.insert(0, './src')

from gaussian_runner import InteractionEnergyPipeline
from structure_parser import StructureParser

# 读取结构
mol_a = StructureParser()
mol_a.read_xyz("molecule_a.xyz")

mol_b = StructureParser()
mol_b.read_xyz("molecule_b.xyz")

# 初始化流程
pipeline = InteractionEnergyPipeline(
    gaussian_root="/opt/share/gaussian/g16",
    work_dir="./my_calculation"
)

# 分步执行
# 1. 优化单体
print("优化单体A...")
files_a = pipeline.optimize_monomer(mol_a, "mol_a")

print("优化单体B...")
files_b = pipeline.optimize_monomer(mol_b, "mol_b")

# 2. 获取优化后的结构
opt_a = StructureParser()
opt_a.read_gaussian_output(files_a['log'])

opt_b = StructureParser()
opt_b.read_gaussian_output(files_b['log'])

# 3. 对接
print("分子对接...")
complex_struct, dock_results = pipeline.dock_molecules(opt_a, opt_b)

# 4. 优化复合物
print("优化复合物...")
complex_files = pipeline.optimize_complex(opt_a, opt_b)

# 5. 提取结果
print("提取结果...")
results = pipeline.extract_and_save_results(complex_files['log'])

print(f"\n最终结果:")
print(f"相互作用能: {results['complexation_energy_corrected']:.2f} kcal/mol")
print(f"BSSE: {results['bsse_energy']:.6f} Hartree")
```

## 参数调优

### 泛函选择指南

| 泛函 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| B3LYP-D3(BJ) | 常规计算、大体系 | 快速、可靠 | 精度中等 |
| M06-2X | 非共价相互作用 | 平衡精度和速度 | 比B3LYP慢 |
| ωB97X-D | 长程相互作用 | 精度高 | 计算慢 |
| B2PLYP-D3 | 高精度基准 | 非常精确 | 非常慢 |

### 基组选择指南

| 基组 | 适用场景 | 相对速度 | BSSE大小 |
|------|---------|---------|---------|
| 6-31G(d,p) | 初步测试 | 很快 | 较大 |
| 6-311++G(d,p) | 常规计算 | 中等 | 中等 |
| def2-TZVP | 高质量计算 | 较慢 | 较小 |
| aug-cc-pVTZ | 基准计算 | 很慢 | 很小 |

**重要提示:**
- 弥散函数(+, ++, aug-)对非共价相互作用**必不可少**
- 极化函数(d, p)提高精度
- 三ζ基组(TZVP, aug-cc-pVTZ)优于双ζ

### 计算资源配置

```bash
# 小体系 (< 20原子)
--nproc 24 --mem 20GB

# 中等体系 (20-50原子)
--nproc 48 --mem 50GB

# 大体系 (> 50原子)
--nproc 96 --mem 100GB
```

## 常见问题

### Q1: 如何判断结果是否可靠？

检查以下指标：

1. **收敛状态**: 必须显示"Normal termination"
2. **虚频检查**: 优化后应该无虚频
3. **BSSE大小**: 
   - < 1 kcal/mol: 优秀
   - 1-2 kcal/mol: 良好
   - 2-3 kcal/mol: 可接受
   - \> 3 kcal/mol: 需要更大基组

### Q2: 相互作用能为正值，正常吗？

**正常情况:**
- 正值表示排斥性相互作用
- 分子在该构象下不稳定
- 可能是初始构象不合理

**解决方法:**
- 使用Vina对接获取更好的初始构象
- 尝试手动调整分子相对位置
- 检查是否有空间位阻

### Q3: 计算很慢怎么办？

**优化策略:**

1. 使用更小的基组进行初步筛选
2. 先不计算频率(频率计算很慢)
3. 减少CPU核心数(某些情况下反而更快)
4. 使用更快的泛函(如B3LYP而非ωB97X-D)

### Q4: Vina对接失败怎么办？

**可能原因:**
- Vina未正确安装
- Open Babel未安装
- 分子过小导致搜索盒问题

**解决方法:**
```bash
# 跳过对接
python scripts/run_pipeline.py mol_a.xyz mol_b.xyz --no-docking

# 或手动准备复合物初始构象
```

## 故障排除

### 错误1: "Gaussian not found"

**解决方法:**
```bash
# 检查Gaussian路径
ls /opt/share/gaussian/g16/g16

# 使用正确路径
python scripts/run_pipeline.py mol_a.xyz mol_b.xyz \
    --gaussian_root /your/gaussian/path
```

### 错误2: "SCF convergence failure"

**可能原因:**
- 初始结构不合理
- 体系有电荷转移
- 基组线性依赖

**解决方法:**
- 检查输入结构合理性
- 尝试不同的SCF算法: 在gjf中添加`SCF=QC`
- 使用更小的基组测试

### 错误3: "Optimization not converged"

**解决方法:**
- 增加优化步数限制: `Opt=MaxCycles=200`
- 使用更宽松的收敛标准
- 检查初始结构是否合理

### 错误4: "Imaginary frequencies found"

**含义:**
- 结构不是真实的极小点
- 可能是过渡态或鞍点

**解决方法:**
- 沿虚频模式扰动结构后重新优化
- 检查是否是对接造成的不合理构象
- 尝试不同的初始构象

### 错误5: "Memory allocation failed"

**解决方法:**
```bash
# 减小内存设置
python scripts/run_pipeline.py mol_a.xyz mol_b.xyz --mem 50GB

# 或增加系统swap空间
```

## 高级技巧

### 1. 使用配置文件

编辑 `config.ini` 设置默认参数：
```ini
[Gaussian]
gaussian_root = /your/gaussian/path
default_functional = M06-2X
default_basis_set = def2-TZVP
```

### 2. 监控长时间计算

```python
from gaussian_runner import GaussianRunner

runner = GaussianRunner()
runner.monitor_calculation("complex.log", check_interval=300)  # 每5分钟检查
```

### 3. 提取中间结果

```python
from result_extractor import ResultExtractor

extractor = ResultExtractor("complex.log")
all_energies = extractor.extract_all_energies()  # 所有SCF能量
errors = extractor.extract_error_messages()       # 错误信息
```

### 4. 自定义报告

```python
results = extractor.extract_counterpoise_results()

# 自定义输出格式
with open("custom_report.csv", 'w') as f:
    f.write("Energy (kcal/mol),BSSE (Hartree)\n")
    f.write(f"{results['complexation_energy_corrected']},")
    f.write(f"{results['bsse_energy']}\n")
```

## 最佳实践

1. **总是先用小基组测试**，确保流程无误
2. **检查虚频**，确保结构是真实极小点
3. **报告BSSE大小**，评估结果可靠性
4. **保存中间文件**，便于问题排查
5. **批量计算使用脚本**，提高效率
6. **定期备份结果**，防止数据丢失

## 参考资料

- Gaussian 16用户手册
- AutoDock Vina文档
- Boys & Bernardi, Mol. Phys. 1970 (Counterpoise方法原文)
- 本项目教程: `Gaussian+Multiwfn计算ΔE_int教程.md`
