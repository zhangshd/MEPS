# MEPS 项目文件结构说明

本文档详细说明了MEPS项目中每个文件和目录的作用。

```
MEPS/
│
├── README.md                          # 项目主文档，包含项目介绍、安装和使用说明
├── QUICKSTART.md                      # 快速开始指南，5分钟上手
├── MANUAL.md                          # 详细使用手册，包含所有功能和参数说明
├── Gaussian+Multiwfn计算ΔE_int教程.md  # 理论背景和方法介绍（原有文档）
│
├── environment.yml                    # Conda环境配置文件，定义所有Python依赖
├── config.ini                         # 项目配置文件，包含默认参数设置
├── setup.sh                          # 自动化安装脚本
├── .gitignore                        # Git忽略文件配置
│
├── src/                              # 源代码目录
│   ├── __init__.py                   # 包初始化文件
│   ├── structure_parser.py           # 分子结构解析模块
│   │                                 # - 读写XYZ, PDB, Gaussian输出等格式
│   │                                 # - 结构操作：平移、旋转、合并
│   │                                 # - 几何分析：质心、边界盒等
│   │
│   ├── gaussian_io.py                # Gaussian输入输出模块
│   │                                 # - GaussianInputGenerator: 生成gjf输入文件
│   │                                 # - GaussianOutputParser: 解析log输出文件
│   │
│   ├── gaussian_runner.py            # Gaussian计算管理模块
│   │                                 # - GaussianRunner: 运行和监控Gaussian计算
│   │                                 # - InteractionEnergyPipeline: 完整流程管理
│   │
│   ├── result_extractor.py           # 结果提取模块
│   │                                 # - 提取Counterpoise结果
│   │                                 # - 生成TXT和JSON报告
│   │
│   └── vina_docking.py               # 分子对接模块
│                                     # - 使用AutoDock Vina进行分子对接
│                                     # - 自动准备PDBQT文件和搜索盒
│
├── scripts/                          # 可执行脚本目录
│   └── run_pipeline.py               # 主流程命令行脚本
│                                     # 用法: python run_pipeline.py mol_a.xyz mol_b.xyz
│
├── examples/                         # 示例代码目录
│   └── tutorial_example.py           # 详细的使用教程和示例
│                                     # 包含5个不同的使用场景示例
│
├── tests/                            # 测试目录
│   └── test_installation.py          # 安装测试脚本
│                                     # 检查所有依赖是否正确安装
│
├── data/                             # 数据目录
│   ├── input/                        # 输入文件目录
│   │   ├── water.xyz                 # 示例：水分子结构
│   │   ├── methane.xyz               # 示例：甲烷结构
│   │   └── .gitkeep                  # 保持目录结构
│   │
│   └── output/                       # 输出文件目录
│       └── .gitkeep                  # 保持目录结构
│
└── example/                          # 原有的Gaussian计算示例
    ├── benzene.gjf                   # 苯的输入文件
    ├── benzene.chk                   # 苯的检查点文件
    ├── benzene.out                   # 苯的输出文件
    ├── methane.gjf                   # 甲烷的输入文件
    ├── methane.chk                   # 甲烷的检查点文件
    ├── methane.out                   # 甲烷的输出文件
    ├── complex.gjf                   # 复合物的输入文件
    ├── complex.chk                   # 复合物的检查点文件
    ├── complex.log                   # 复合物的输出日志
    ├── complex.fchk                  # 复合物的格式化检查点文件
    └── run.sh                        # 运行脚本
```

## 核心模块详解

### 1. structure_parser.py (297行)

**作用**: 处理分子结构的读取、写入和操作

**主要类**: `StructureParser`

**核心功能**:
- `read_xyz()`: 读取XYZ格式文件
- `read_pdb()`: 读取PDB格式文件
- `read_gaussian_output()`: 从Gaussian输出提取优化后的结构
- `write_xyz()`, `write_pdb()`: 写入各种格式
- `merge()`: 合并两个分子
- `get_center_of_mass()`: 计算质心
- `get_bounding_box()`: 获取边界盒

**使用场景**:
- 读取用户提供的输入结构
- 从Gaussian优化结果提取最终结构
- 为对接准备PDB文件
- 合并单体构建复合物

### 2. gaussian_io.py (241行)

**作用**: 生成Gaussian输入文件和解析输出文件

**主要类**:
- `GaussianInputGenerator`: 生成.gjf输入文件
- `GaussianOutputParser`: 解析.log输出文件

**核心功能**:
- `generate_optimization_input()`: 生成单体优化输入
- `generate_counterpoise_input()`: 生成Counterpoise计算输入
- `is_normal_termination()`: 检查计算是否正常结束
- `get_scf_energy()`: 提取SCF能量
- `check_imaginary_frequencies()`: 检查虚频

**使用场景**:
- 自动生成格式正确的Gaussian输入文件
- 检查计算是否成功完成
- 提取基本能量数据

### 3. result_extractor.py (231行)

**作用**: 从Gaussian输出中提取详细的相互作用能结果

**主要类**: `ResultExtractor`

**核心功能**:
- `extract_counterpoise_results()`: 提取CP结果（最重要）
- `extract_monomer_energy()`: 提取单体能量
- `get_optimization_summary()`: 获取优化摘要
- `generate_summary_report()`: 生成可读报告

**提取的数据**:
- 相互作用能（原始和校正后）
- BSSE能量
- 优化步骤详情
- 收敛状态
- 错误信息

**使用场景**:
- 从复杂的Gaussian输出中提取关键数据
- 生成用户友好的结果报告
- 批量处理时自动提取数据

### 4. vina_docking.py (271行)

**作用**: 使用AutoDock Vina进行分子对接

**主要类**: `VinaDocking`

**核心功能**:
- `prepare_receptor()`: 准备受体PDBQT文件
- `prepare_ligand()`: 准备配体PDBQT文件
- `calculate_search_box()`: 自动计算搜索盒
- `run_docking()`: 运行Vina对接
- `extract_best_pose()`: 提取最佳对接姿态
- `dock_two_molecules()`: 完整对接流程（便捷方法）

**使用场景**:
- 自动找到两个分子的合理相互作用构象
- 适用于不知道分子如何组合的情况
- 生成复合物的初始结构

### 5. gaussian_runner.py (490行，最复杂)

**作用**: 管理Gaussian计算和完整的计算流程

**主要类**:
- `GaussianRunner`: 基础的Gaussian运行器
- `InteractionEnergyPipeline`: 完整流程管理（核心）

**GaussianRunner功能**:
- `run_gaussian()`: 运行Gaussian计算
- `monitor_calculation()`: 监控计算进度
- `convert_chk_to_fchk()`: 转换检查点文件
- `check_calculation_status()`: 检查计算状态

**InteractionEnergyPipeline功能**:
- `optimize_monomer()`: 优化单个分子
- `dock_molecules()`: 对接两个分子
- `optimize_complex()`: 优化复合物
- `extract_and_save_results()`: 提取并保存结果
- `run_full_pipeline()`: 运行完整流程（最常用）

**使用场景**:
- 这是用户主要交互的模块
- 提供从输入到结果的完整自动化流程
- 管理所有中间步骤和文件

## 脚本和工具

### scripts/run_pipeline.py (203行)

**作用**: 命令行接口

**功能**:
- 解析命令行参数
- 调用InteractionEnergyPipeline
- 打印友好的结果摘要
- 错误处理和用户提示

**使用方式**:
```bash
python scripts/run_pipeline.py mol_a.xyz mol_b.xyz [选项]
```

**适用场景**:
- 快速计算，无需编写Python代码
- 批处理脚本中调用
- 标准化的计算流程

### examples/tutorial_example.py (308行)

**作用**: 教程和示例代码

**包含5个示例**:
1. 基本用法
2. 自定义参数
3. 分步执行
4. 不使用对接
5. 批量计算

**适用场景**:
- 学习如何使用API
- 参考复杂用法
- 自定义计算流程

### tests/test_installation.py (209行)

**作用**: 验证安装

**测试内容**:
- Python版本
- 必需的Python包
- 可选的Python包
- Gaussian可用性
- Open Babel命令
- Vina命令
- MEPS模块导入
- 创建测试文件

**使用方式**:
```bash
python tests/test_installation.py
```

## 文档文件

### README.md
- 项目总览和介绍
- 安装说明
- 基本使用方法
- 项目结构
- 背景理论简介

### QUICKSTART.md
- 5分钟快速开始
- 最简单的使用示例
- 常见问题解答
- 适合新手

### MANUAL.md
- 完整的使用手册
- 所有功能详解
- 参数调优指南
- 故障排除
- 高级技巧

### Gaussian+Multiwfn计算ΔE_int教程.md
- 理论背景
- Counterpoise方法详解
- 手动计算步骤
- 适合深入理解原理

## 配置文件

### environment.yml
```yaml
name: meps
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy
  - scipy
  - openbabel
  - rdkit
  - vina
  - biopython
```

### config.ini
- 默认Gaussian路径
- 默认计算参数
- 对接参数
- 输出设置

## 数据目录

### data/input/
- 存放输入分子结构文件
- 提供了water.xyz和methane.xyz作为示例

### data/output/
- 存放计算结果
- 由程序自动生成

### example/
- 包含实际运行过的Gaussian计算示例
- 可以用来验证安装和学习

## 工作流程中的文件流转

```
用户输入: molecule_a.xyz, molecule_b.xyz
    ↓
StructureParser读取
    ↓
GaussianInputGenerator生成: monomer_a.gjf, monomer_b.gjf
    ↓
GaussianRunner运行: → monomer_a.log, monomer_b.log
    ↓
GaussianOutputParser提取优化结构
    ↓
VinaDocking对接: → docked.pdbqt
    ↓
GaussianInputGenerator生成: complex.gjf (带Counterpoise)
    ↓
GaussianRunner运行: → complex.log
    ↓
ResultExtractor提取: → results.txt, results.json
```

## 如何扩展项目

### 添加新的文件格式支持
在`structure_parser.py`中添加新的读写方法

### 支持新的量子化学程序
创建新的模块，参考`gaussian_io.py`的结构

### 添加新的分析方法
在`result_extractor.py`中添加新的提取函数

### 支持更多片段的Counterpoise
修改`gaussian_io.py`中的`generate_counterpoise_input()`方法

### 添加新的对接程序
创建新的对接模块，参考`vina_docking.py`

## 性能优化建议

1. **并行计算**: Gaussian已使用多核，无需额外并行
2. **批量处理**: 使用示例5的批量计算方法
3. **缓存结果**: 保留.chk文件可以续算
4. **分步执行**: 可以暂停后继续，不必重新开始

## 维护和更新

- 所有代码注释使用英文
- 用户文档使用中文
- 遵循PEP 8代码规范
- 模块化设计便于维护
- 详细的错误处理和日志

## 总结

MEPS项目包含约2000行Python代码，实现了从分子结构输入到相互作用能结果输出的完整自动化流程。项目结构清晰，模块化设计良好，易于使用和扩展。
