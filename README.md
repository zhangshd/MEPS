# MEPS - 分子间相互作用能自动化计算流程

## 项目简介

MEPS (Molecular Interaction Energy Pipeline System) 是一个基于Python的自动化工具，用于计算和分析分子间的相互作用能。本项目整合了Gaussian量子化学计算和AutoDock Vina分子对接，提供了一个端到端的自动化工作流程。

## 主要功能

1. **单体结构优化**: 自动生成和运行单个分子的Gaussian结构优化任务
   - **🚀 NEW**: 支持并行优化多个单体分子，大幅提升计算效率（节省约50%时间）
2. **分子对接**: 使用AutoDock Vina对两个优化后的分子进行对接，获得初始复合物构象
3. **复合物优化**: 自动生成带Counterpoise校正的复合物输入文件并运行优化
4. **结果提取**: 自动从Gaussian输出文件中提取相互作用能、BSSE能量等关键信息
5. **批量并行处理**: 自动化批量计算多对分子的相互作用能，支持并行计算
6. **多格式支持**: 支持XYZ, PDB, MOL, SDF, MOL2等多种分子结构文件格式

## 理论背景

本项目基于超分子方法计算分子间相互作用能(ΔE_int)，并使用Boys-Bernardi反向校正方法(Counterpoise)消除基组重叠误差(BSSE)。

相互作用能计算公式：
```
ΔE_int = E_complex - E_monomerA - E_monomerB
```

经过BSSE校正后的相互作用能更加准确可靠，适用于：
- 药物设计中的配体-受体相互作用分析
- 共晶工程中的分子间作用力研究
- 超分子化学中的非共价相互作用研究

## 项目结构

```
MEPS/
├── README.md                      # 项目说明文档
├── environment.yml                # Conda环境配置文件
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── gaussian_io.py            # Gaussian输入输出处理
│   ├── gaussian_runner.py        # Gaussian任务运行管理
│   ├── vina_docking.py           # AutoDock Vina对接模块
│   ├── structure_parser.py       # 分子结构解析
│   └── result_extractor.py       # 结果提取模块
├── scripts/                      # 脚本目录
│   ├── run_pipeline.py           # 单对分子计算脚本
│   └── batch_interaction_energy.py  # 批量并行计算脚本
├── examples/                     # 示例文件
│   ├── tutorial_example.py       # 使用教程示例
│   ├── batch_calculation_example.py  # 批处理示例
│   └── mol_format_example.py     # MOL格式使用示例
├── data/                         # 数据目录
│   ├── input/                    # 输入文件
│   └── output/                   # 输出结果
└── tests/                        # 测试目录
```

## 环境配置

### 前置要求

1. **Gaussian 16**: 已安装在 `/opt/share/gaussian/g16`
2. **Conda**: 用于管理Python环境
3. **操作系统**: Linux (推荐)

### 安装步骤

1. 克隆或下载本项目到本地

2. 创建并激活conda环境：
```bash
conda env create -f environment.yml
conda activate meps
```

3. 验证安装：
```bash
python -c "import openbabel; import vina; print('环境配置成功!')"
```

## 使用方法

### 支持的文件格式

MEPS支持以下分子结构文件格式：
- **XYZ** (.xyz): 笛卡尔坐标格式
- **PDB** (.pdb): 蛋白质数据库格式
- **MOL/SDF** (.mol, .sdf): MDL MOL格式
- **MOL2** (.mol2): Tripos MOL2格式
- **Gaussian输出** (.log, .out): 优化后的结构

> 详细的MOL/MOL2格式使用说明请参考 [`docs/MOL_FORMAT.md`](docs/MOL_FORMAT.md)

### 快速开始

```python
from src.gaussian_runner import InteractionEnergyPipeline

# 初始化流程
pipeline = InteractionEnergyPipeline(
    gaussian_root="/opt/share/gaussian/g16",
    work_dir="./data/output/my_calculation"
)

# 运行完整流程（支持.xyz, .pdb, .mol, .sdf, .mol2格式）
results = pipeline.run_full_pipeline(
    molecule_a="path/to/molecule_a.xyz",
    molecule_b="path/to/molecule_b.xyz",
    functional="B3LYP",
    basis_set="6-311++G(d,p)",
    dispersion="GD3BJ"
)

# 查看结果
print(f"相互作用能 (校正后): {results['complexation_energy_corrected']} kcal/mol")
print(f"BSSE能量: {results['bsse_energy']} Hartree")
```

> **🚀 性能提升**: `run_full_pipeline` 方法已自动启用并行优化，两个单体分子将同时进行优化计算，相比串行方式可节省约50%的计算时间。详见 [并行优化文档](docs/PARALLEL_OPTIMIZATION.md)。

### 并行优化功能

新增的并行优化功能可以同时优化多个单体分子，显著提升计算效率：

```python
from src.gaussian_runner import InteractionEnergyPipeline
from src.structure_parser import StructureParser

pipeline = InteractionEnergyPipeline(work_dir="./calculations")

# 准备多个分子结构
structures = []
for xyz_file, name in [("mol1.xyz", "mol1"), ("mol2.xyz", "mol2")]:
    struct = StructureParser()
    struct.read_xyz(xyz_file)
    structures.append((struct, name))

# 并行优化所有单体（注意合理分配CPU和内存资源）
monomer_files = pipeline.optimize_monomers_parallel(
    structures=structures,
    nproc=48,   # 每个任务48核，2个任务共需96核
    mem="90GB"  # 每个任务90GB，2个任务共需180GB
)
```

**资源配置建议**：
- 对于96核系统运行2个并行任务：每任务 `nproc=48`
- 对于200GB内存系统：每任务 `mem="90GB"`（预留系统内存）
- 更多信息请参考 [并行优化详细文档](docs/PARALLEL_OPTIMIZATION.md)

### 使用命令行脚本

#### 单个分子对计算

```bash
# 基本用法（支持.xyz, .pdb, .mol, .sdf, .mol2格式）
python scripts/run_pipeline.py molecule_a.xyz molecule_b.xyz

# 指定计算参数
python scripts/run_pipeline.py benzene.mol methane.mol \
    --name_a benzene --name_b methane \
    --functional M06-2X --basis def2-TZVP \
    --mem 50GB --nproc 48

# 查看所有选项
python scripts/run_pipeline.py --help
```

#### 批量并行计算

对于需要计算多个分子对的场景，使用批处理脚本可以自动发现文件并并行计算：

```bash
# 基本用法：自动并行计算molA和molB文件夹中所有分子的两两组合
python scripts/batch_interaction_energy.py molA/ molB/ results/

# 控制并行度：每个任务96核，最多同时运行4个任务
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --nproc 96 --max-jobs 4

# 指定计算参数
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --functional M06-2X --basis def2-TZVP --mem 50GB

# 仅处理特定格式
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --extensions .mol .mol2

# 查看使用示例和CPU配置建议
python examples/batch_calculation_example.py
```

**批处理脚本特点**：
- 自动发现两个文件夹中的所有分子文件
- 生成所有可能的分子对组合（笛卡尔积）
- 根据系统CPU数量和单任务核数自动配置并行度
- 每个分子对的结果保存在独立文件夹中
- 生成 `batch_summary.json` 汇总所有计算结果
- 支持失败重试和错误报告

**输出结构示例**：
```
results/
├── batch_summary.json          # 总体汇总文件
├── water_methane/              # 第一对分子的结果
│   ├── complex.log
│   ├── results.json
│   └── ...
├── water_ethane/               # 第二对分子的结果
│   └── ...
└── benzene_methane/            # 第三对分子的结果
    └── ...
```

### 分步运行

```python
# 1. 单体优化
pipeline.optimize_monomer(
    molecule_file="molecule_a.xyz",
    output_name="monomer_a"
)

# 2. 分子对接
pipeline.dock_molecules(
    receptor="monomer_a_opt.pdb",
    ligand="monomer_b_opt.pdb"
)

# 3. 复合物优化
pipeline.optimize_complex(
    complex_structure="docked_complex.pdb"
)

# 4. 提取结果
results = pipeline.extract_results("complex.log")
```

## 计算参数说明

### 泛函选择

- **B3LYP-D3(BJ)**: 经济高效，适合大体系初步筛选
- **M06-2X**: 稳健可靠，适合中等大小体系
- **ωB97X-D**: 长程校正泛函，适合非共价相互作用

### 基组选择

- **6-311++G(d,p)**: 平衡精度与成本，推荐用于常规计算
- **def2-TZVP**: 现代高效基组，性能优异
- **aug-cc-pVTZ**: 高精度计算，计算成本较高

### Counterpoise校正

默认启用Counterpoise=2校正，消除双分子体系的基组重叠误差。对于三个或更多片段，修改为Counterpoise=N。

## 输出结果

计算完成后，将在输出目录生成以下文件：

- `monomer_a.log`: 单体A优化输出
- `monomer_b.log`: 单体B优化输出
- `complex.log`: 复合物优化输出
- `docking_results.pdbqt`: 对接结果
- `results_summary.json`: 结果汇总JSON文件
- `results_summary.txt`: 可读的结果汇总文本

结果文件包含：
- 相互作用能 (原始值和BSSE校正值)
- BSSE能量
- 各优化步骤的能量
- 最终优化构象

## 注意事项

1. **计算资源**: 大体系的优化和频率计算需要较多内存和CPU，建议根据实际情况调整%mem和%nproc参数
2. **收敛问题**: 某些体系可能难以收敛，可尝试调整优化算法或初始构象
3. **BSSE大小**: BSSE > 2-3 kcal/mol时，建议使用更大的基组
4. **气相近似**: 本流程计算的是气相中的相互作用能，实际溶液或晶体环境需要额外处理

## 参考文献

详细的理论背景和计算方法说明，请参考项目中的 `Gaussian+Multiwfn计算ΔE_int教程.md`。

## 许可证

本项目仅用于学术研究目的。使用Gaussian软件需要相应的商业许可。

## 作者

zhangshd

## 更新日志

- **v1.2.0** (2025-10-16): 添加批量并行计算功能
  - 新增 `batch_interaction_energy.py` 批处理脚本
  - 支持自动发现文件并生成所有分子对组合
  - 智能配置并行计算资源
  - 详见 [`docs/BATCH_CALCULATION.md`](docs/BATCH_CALCULATION.md)

- **v1.1.0** (2025-10-16): 添加MOL/MOL2格式支持
  - 支持读写MOL/SDF/MOL2格式文件
  - 完整的Pipeline集成
  - 详见 [`docs/MOL_FORMAT.md`](docs/MOL_FORMAT.md)
  
- **v1.0.0** (2025-10-12): 初始版本发布
  - 完整的相互作用能计算流程
  - 自动BSSE校正
  - 支持批量计算
