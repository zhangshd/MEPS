# 批量并行计算指南

## 概述

`batch_interaction_energy.py` 脚本用于自动化批量计算两组分子之间的所有可能的相互作用能。该脚本会：

1. 自动发现两个文件夹中的所有分子文件
2. 生成所有可能的分子对组合
3. 根据系统资源自动配置并行计算
4. 为每个分子对创建独立的结果文件夹
5. 生成汇总报告

## 使用场景

- **药物筛选**: 评估多个候选药物分子与受体的相互作用
- **共晶筛选**: 筛选多个配体分子与API的成对稳定性
- **溶剂效应研究**: 评估分子在不同溶剂中的相互作用
- **高通量计算**: 批量评估分子库之间的相互作用

## 基本用法

```bash
python scripts/batch_interaction_energy.py molA/ molB/ results/
```

这将：
- 读取 `molA/` 目录下的所有分子文件
- 读取 `molB/` 目录下的所有分子文件
- 计算所有可能的分子对组合 (M × N 对)
- 结果保存在 `results/` 目录下

## 命令行参数

### 必需参数

| 参数 | 说明 |
|------|------|
| `molA_dir` | 包含分子A文件的目录路径 |
| `molB_dir` | 包含分子B文件的目录路径 |
| `output_dir` | 输出结果目录路径 |

### 计算资源参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--nproc` | 96 | 每个Gaussian任务使用的CPU核数 |
| `--max-jobs` | 自动检测 | 最大并行任务数 |
| `--mem` | 100GB | 每个任务的内存分配 |

**自动并行度计算**：
```python
max_parallel_jobs = total_cpus // nproc_per_job
```

例如：
- 384核系统，`--nproc 96`：最多4个并行任务
- 384核系统，`--nproc 48`：最多8个并行任务
- 192核系统，`--nproc 96`：最多2个并行任务

### 计算参数

| 参数 | 默认值 | 可选值 | 说明 |
|------|--------|--------|------|
| `--functional` | B3LYP | B3LYP, M06-2X, wB97X-D, B2PLYP | DFT泛函 |
| `--basis` | 6-311++G(d,p) | 任意Gaussian支持的基组 | 基组 |
| `--dispersion` | GD3BJ | GD3, GD3BJ, None | 色散校正方法 |

### Gaussian设置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--gaussian-root` | /opt/share/gaussian/g16 | Gaussian安装根目录 |

### 对接设置

| 参数 | 说明 |
|------|------|
| `--no-docking` | 禁用分子对接，直接使用输入结构 |

### 文件发现

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--extensions` | .xyz .pdb .mol .sdf .mol2 | 要搜索的文件扩展名 |

## 使用示例

### 1. 基本使用（自动并行）

```bash
python scripts/batch_interaction_energy.py molA/ molB/ results/
```

自动检测系统CPU数量并配置最优并行度。

### 2. 控制计算资源

```bash
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --nproc 48 \
    --max-jobs 4 \
    --mem 50GB
```

- 每个任务使用48个CPU核
- 最多同时运行4个任务
- 每个任务分配50GB内存

### 3. 指定计算参数

```bash
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --functional M06-2X \
    --basis def2-TZVP \
    --dispersion GD3
```

使用M06-2X/def2-TZVP理论级别，GD3色散校正。

### 4. 禁用分子对接

```bash
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --no-docking
```

跳过AutoDock Vina对接步骤，直接使用输入分子结构计算。

### 5. 仅处理特定格式

```bash
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --extensions .mol .mol2
```

仅搜索和处理 `.mol` 和 `.mol2` 格式文件。

### 6. 完整示例

```bash
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --nproc 96 \
    --max-jobs 2 \
    --mem 100GB \
    --functional B3LYP \
    --basis "6-311++G(d,p)" \
    --dispersion GD3BJ \
    --gaussian-root /opt/share/gaussian/g16 \
    --extensions .xyz .pdb .mol
```

## 输出结构

计算完成后，输出目录结构如下：

```
results/
├── batch_summary.json              # 总体汇总文件
├── molA1_molB1/                    # 第一对分子的结果
│   ├── monomer_molA1/
│   │   ├── monomer_molA1.gjf
│   │   └── monomer_molA1.log
│   ├── monomer_molB1/
│   │   ├── monomer_molB1.gjf
│   │   └── monomer_molB1.log
│   ├── vina_docking/
│   │   ├── receptor.pdbqt
│   │   ├── ligand.pdbqt
│   │   └── docked.pdbqt
│   ├── complex/
│   │   ├── complex.gjf
│   │   └── complex.log
│   ├── results.json
│   └── results.txt
├── molA1_molB2/                    # 第二对分子的结果
│   └── ...
├── molA2_molB1/                    # 第三对分子的结果
│   └── ...
└── ...
```

## 汇总文件说明

### batch_summary.json

JSON格式的汇总文件，包含：

```json
{
  "timestamp": "2025-10-16T10:30:00",
  "configuration": {
    "molA_dir": "/path/to/molA",
    "molB_dir": "/path/to/molB",
    "functional": "B3LYP",
    "basis_set": "6-311++G(d,p)",
    "nproc_per_job": 96,
    "max_parallel_jobs": 4
  },
  "statistics": {
    "total_pairs": 12,
    "successful": 11,
    "failed": 1,
    "total_time_seconds": 36000,
    "average_time_per_pair": 3000
  },
  "successful_calculations": [
    {
      "pair_name": "molA1_molB1",
      "results": {
        "complexation_energy_corrected": -5.23,
        "bsse_energy": 0.0012,
        ...
      }
    },
    ...
  ],
  "failed_calculations": [
    {
      "pair_name": "molA3_molB2",
      "error": "SCF convergence failure"
    }
  ]
}
```

## CPU配置建议

使用 `examples/batch_calculation_example.py` 查看系统的推荐配置：

```bash
python examples/batch_calculation_example.py
```

该脚本会显示：
- 系统总CPU核数
- 不同核数配置下的并行度
- CPU利用率
- 推荐配置

**配置原则**：

1. **大分子体系** (>50原子)
   - 使用较多核数 (96核)
   - 减少并行任务数
   - 提高单个任务的计算速度

2. **小分子体系** (<30原子)
   - 使用较少核数 (24-48核)
   - 增加并行任务数
   - 提高整体吞吐量

3. **内存限制**
   - 确保 `--mem` × `--max-jobs` ≤ 系统总内存
   - 大分子建议100GB以上
   - 小分子可用50GB

4. **I/O考虑**
   - 避免过度并行导致磁盘I/O瓶颈
   - 使用SSD存储可提高性能

## 典型使用流程

### 1. 准备输入文件

```bash
# 创建分子目录
mkdir -p molA molB

# 将分子文件复制到相应目录
cp candidate_drugs/*.mol molA/
cp receptors/*.pdb molB/
```

### 2. 预览计算规模

```bash
# 统计文件数量
echo "MolA files: $(ls molA/*.mol | wc -l)"
echo "MolB files: $(ls molB/*.pdb | wc -l)"
echo "Total pairs: $(($(ls molA/*.mol | wc -l) * $(ls molB/*.pdb | wc -l)))"
```

### 3. 测试运行（小规模）

```bash
# 先用小数据集测试
mkdir test_molA test_molB
cp molA/mol1.mol test_molA/
cp molB/receptor1.pdb test_molB/

python scripts/batch_interaction_energy.py \
    test_molA/ test_molB/ test_results/ \
    --nproc 24 --no-docking
```

### 4. 正式运行

```bash
python scripts/batch_interaction_energy.py \
    molA/ molB/ results/ \
    --nproc 96 \
    --max-jobs 4 \
    --functional B3LYP \
    --basis "6-311++G(d,p)"
```

### 5. 监控进度

```bash
# 实时查看进程数
watch -n 10 'ps aux | grep g16 | wc -l'

# 查看已完成的计算
ls results/*/results.json | wc -l

# 查看日志
tail -f results/molA1_molB1/complex/complex.log
```

### 6. 结果分析

```python
import json

# 读取汇总文件
with open('results/batch_summary.json', 'r') as f:
    summary = json.load(f)

# 提取相互作用能
energies = []
for result in summary['successful_calculations']:
    pair = result['pair_name']
    energy = result['results']['complexation_energy_corrected']
    energies.append((pair, energy))

# 排序找出最稳定的分子对
energies.sort(key=lambda x: x[1])
print("Top 5 most stable pairs:")
for pair, energy in energies[:5]:
    print(f"  {pair}: {energy:.2f} kcal/mol")
```

## 错误处理

### 常见错误

1. **SCF收敛失败**
   - 解决：调整初始结构或使用不同泛函
   - 在单个分子对上测试优化参数

2. **内存不足**
   - 解决：增加 `--mem` 参数
   - 减少 `--max-jobs` 避免内存超限

3. **磁盘空间不足**
   - 每对分子约需要1-5GB空间
   - 及时清理中间文件

4. **文件找不到**
   - 检查 `--extensions` 参数
   - 确认文件命名正确

### 重新运行失败的计算

从 `batch_summary.json` 中提取失败的分子对，手动重新计算：

```bash
# 提取失败的分子对名称
python -c "
import json
with open('results/batch_summary.json') as f:
    data = json.load(f)
for item in data['failed_calculations']:
    print(item['pair_name'])
" > failed_pairs.txt

# 重新计算单个失败的分子对
python scripts/run_pipeline.py \
    molA/molA3.mol \
    molB/molB2.pdb \
    --name_a molA3 --name_b molB2
```

## 性能优化建议

1. **使用本地存储**：避免在网络文件系统上运行
2. **合理配置并行度**：避免CPU过度订阅
3. **批量提交**：对于超大规模计算，考虑分批次运行
4. **监控资源**：使用 `htop` 或 `top` 监控CPU和内存使用
5. **使用SSD**：提高I/O性能

## 常见问题

**Q: 如何估算总计算时间？**

A: 先用小规模测试，然后根据 `average_time_per_pair` 估算：
```
总时间 ≈ (总分子对数 / 并行任务数) × 单对平均时间
```

**Q: 可以中断后继续吗？**

A: 当前版本不支持断点续传。建议分批计算或使用任务调度系统。

**Q: 如何处理不同电荷/自旋态的分子？**

A: 当前批处理脚本默认所有分子为中性单重态。如需不同设置，建议使用单对计算脚本 `run_pipeline.py`。

**Q: 支持GPU加速吗？**

A: Gaussian 16支持GPU加速某些计算，需要在配置中手动启用。

## 总结

批量并行计算脚本适用于需要系统性评估大量分子对相互作用的场景。通过合理配置计算资源和参数，可以高效完成高通量筛选任务。

如有问题，请参考：
- 主文档：`README.md`
- 单对计算脚本：`scripts/run_pipeline.py`
- 示例代码：`examples/batch_calculation_example.py`
