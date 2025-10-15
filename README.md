# MEPS - 分子间相互作用能自动化计算流程

## 项目简介

MEPS (Molecular Interaction Energy Pipeline System) 是一个基于Python的自动化工具，用于计算和分析分子间的相互作用能。本项目整合了Gaussian量子化学计算和AutoDock Vina分子对接，提供了一个端到端的自动化工作流程。

## 主要功能

1. **单体结构优化**: 自动生成和运行单个分子的Gaussian结构优化任务
2. **分子对接**: 使用AutoDock Vina对两个优化后的分子进行对接，获得初始复合物构象
3. **复合物优化**: 自动生成带Counterpoise校正的复合物输入文件并运行优化
4. **结果提取**: 自动从Gaussian输出文件中提取相互作用能、BSSE能量等关键信息
5. **批量处理**: 支持批量处理多对分子的相互作用能计算

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
│   └── run_pipeline.py           # 主流程脚本
├── examples/                     # 示例文件
│   └── tutorial_example.py       # 使用教程示例
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

### 快速开始

```python
from src.gaussian_runner import InteractionEnergyPipeline

# 初始化流程
pipeline = InteractionEnergyPipeline(
    gaussian_root="/opt/share/gaussian/g16",
    work_dir="./data/output/my_calculation"
)

# 运行完整流程
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

- v1.0.0 (2025-10-12): 初始版本发布
  - 实现单体优化、分子对接、复合物优化的完整流程
  - 自动提取相互作用能和BSSE能量
  - 支持批量计算
