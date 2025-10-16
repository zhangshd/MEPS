# MEPS 快速参考

## 脚本总览

| 脚本 | 用途 | 位置 |
|------|------|------|
| `run_pipeline.py` | 单对分子相互作用能计算 | `scripts/` |
| `batch_interaction_energy.py` | 批量并行计算 | `scripts/` |
| `tutorial_example.py` | 基础使用教程 | `examples/` |
| `batch_calculation_example.py` | 批处理示例和CPU配置建议 | `examples/` |
| `mol_format_example.py` | MOL/MOL2格式使用示例 | `examples/` |

## 常用命令

### 单对分子计算

```bash
# 最简单的使用
python scripts/run_pipeline.py molA.xyz molB.xyz

# 完整参数
python scripts/run_pipeline.py molA.xyz molB.xyz \
    --name_a benzene --name_b methane \
    --functional B3LYP --basis "6-311++G(d,p)" \
    --mem 100GB --nproc 96
```

### 批量并行计算

```bash
# 自动并行
python scripts/batch_interaction_energy.py molA/ molB/ results/

# 控制资源
python scripts/batch_interaction_energy.py molA/ molB/ results/ \
    --nproc 48 --max-jobs 4 --mem 50GB

# 查看CPU配置建议
python examples/batch_calculation_example.py
```

### 查看示例

```bash
# 基础教程
python examples/tutorial_example.py

# MOL格式示例
python examples/mol_format_example.py

# 批处理示例
python examples/batch_calculation_example.py
```

## 支持的文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| XYZ | `.xyz` | 笛卡尔坐标格式 |
| PDB | `.pdb` | 蛋白质数据库格式 |
| MOL | `.mol` | MDL MOL格式 |
| SDF | `.sdf` | 结构数据文件 |
| MOL2 | `.mol2` | Tripos MOL2格式 |

## 理论方法快速选择

| 体系类型 | 推荐方法 | 理由 |
|----------|----------|------|
| 大体系初筛 | B3LYP-D3(BJ)/6-311++G(d,p) | 经济高效 |
| 中等体系 | M06-2X/6-311++G(d,p) | 稳健可靠 |
| 非共价相互作用 | ωB97X-D/6-311++G(d,p) | 长程校正 |
| 高精度计算 | B3LYP-D3(BJ)/def2-TZVP | 现代基组 |

## CPU配置速查表

假设系统有 384 CPU核：

| 核/任务 | 并行任务数 | 总利用核数 | 适用场景 |
|---------|-----------|-----------|----------|
| 96 | 4 | 384 | 大分子 |
| 48 | 8 | 384 | 中等分子 |
| 32 | 12 | 384 | 小分子多任务 |
| 24 | 16 | 384 | 高通量筛选 |

**计算公式**：
```
并行任务数 = 总CPU核数 / 每任务核数
```

## 内存需求参考

| 分子大小 | 原子数 | 推荐内存 |
|----------|--------|----------|
| 小分子 | < 30 | 50GB |
| 中等 | 30-80 | 100GB |
| 大分子 | 80-150 | 200GB |
| 超大 | > 150 | 300GB+ |

## 结果文件说明

### 单对计算输出

```
output_dir/
├── monomer_a/
│   ├── monomer_a.gjf        # Gaussian输入
│   └── monomer_a.log        # Gaussian输出
├── monomer_b/
│   ├── monomer_b.gjf
│   └── monomer_b.log
├── vina_docking/
│   ├── receptor.pdbqt       # 受体
│   ├── ligand.pdbqt         # 配体
│   └── docked.pdbqt         # 对接结果
├── complex/
│   ├── complex.gjf          # 复合物输入
│   └── complex.log          # 复合物输出
├── results.json             # JSON格式结果
└── results.txt              # 文本格式结果
```

### 批量计算输出

```
results/
├── batch_summary.json       # 总汇总
├── molA1_molB1/            # 第一对
│   ├── monomer_molA1/
│   ├── monomer_molB1/
│   ├── vina_docking/
│   ├── complex/
│   ├── results.json
│   └── results.txt
├── molA1_molB2/            # 第二对
└── ...
```

## 关键结果字段

| 字段 | 单位 | 说明 |
|------|------|------|
| `complexation_energy` | kcal/mol | 原始相互作用能 |
| `complexation_energy_corrected` | kcal/mol | BSSE校正后相互作用能 |
| `bsse_energy` | Hartree | BSSE能量 |
| `monomer_a_energy` | Hartree | 单体A能量 |
| `monomer_b_energy` | Hartree | 单体B能量 |
| `complex_energy` | Hartree | 复合物能量 |

## 典型工作流程

### 研究新体系

1. **小规模测试**
   ```bash
   python scripts/run_pipeline.py test_a.xyz test_b.xyz --no-docking
   ```

2. **加入对接**
   ```bash
   python scripts/run_pipeline.py test_a.xyz test_b.xyz
   ```

3. **批量计算**
   ```bash
   python scripts/batch_interaction_energy.py molA/ molB/ results/
   ```

4. **分析结果**
   ```python
   import json
   with open('results/batch_summary.json') as f:
       data = json.load(f)
   ```

### 高通量筛选

1. **准备文件**
   ```bash
   mkdir molA molB
   cp candidates/*.mol molA/
   cp receptors/*.pdb molB/
   ```

2. **查看配置建议**
   ```bash
   python examples/batch_calculation_example.py
   ```

3. **运行批量计算**
   ```bash
   python scripts/batch_interaction_energy.py molA/ molB/ results/ \
       --nproc 48 --max-jobs 8
   ```

4. **提取最佳分子对**
   ```python
   import json
   with open('results/batch_summary.json') as f:
       summary = json.load(f)
   
   energies = [(r['pair_name'], 
                r['results']['complexation_energy_corrected'])
               for r in summary['successful_calculations']]
   energies.sort(key=lambda x: x[1])
   
   print("Top 10 stable pairs:")
   for name, energy in energies[:10]:
       print(f"{name}: {energy:.2f} kcal/mol")
   ```

## 常见问题速查

| 问题 | 解决方案 |
|------|----------|
| SCF不收敛 | 尝试不同泛函或调整初始结构 |
| 内存不足 | 增加 `--mem` 或减少 `--max-jobs` |
| 磁盘空间不足 | 每对约需1-5GB，清理中间文件 |
| 对接失败 | 使用 `--no-docking` 跳过 |
| 速度太慢 | 增加 `--nproc` 或减少基组大小 |

## 性能优化建议

1. **使用本地SSD存储**
2. **合理配置并行度** - 避免CPU过度订阅
3. **监控资源** - `htop` 查看CPU/内存使用
4. **分批计算** - 超大规模任务分批运行
5. **清理中间文件** - 定期删除不需要的文件

## 联系与支持

- **文档**: 查看 `README.md` 和 `docs/` 目录
- **问题**: 检查 `docs/BATCH_CALCULATION.md` 和 `docs/MOL_FORMAT.md`
- **作者**: zhangshd

## 快速命令备忘

```bash
# 查看帮助
python scripts/run_pipeline.py --help
python scripts/batch_interaction_energy.py --help

# 测试安装
python -c "import openbabel; import vina; print('OK')"

# 查看CPU信息
python -c "import multiprocessing as mp; print(f'CPUs: {mp.cpu_count()}')"

# 监控Gaussian进程
watch -n 5 'ps aux | grep g16 | wc -l'

# 统计完成的计算
ls results/*/results.json | wc -l

# 查看磁盘使用
du -sh results/
```
