# MOL Format Support - 更新说明

## 版本 v1.1.0 (2025-10-16)

### 新增功能

✅ **MOL/SDF格式支持**
- 支持读取 `.mol` 和 `.sdf` 格式文件
- 支持写入 `.mol` 格式文件
- 自动提取原子坐标、电荷和自旋多重度

### 修改的文件

- `src/structure_parser.py` - 添加 `read_mol()` 和 `write_mol()` 方法
- `src/gaussian_runner.py` - Pipeline集成MOL格式
- `scripts/run_pipeline.py` - 命令行支持MOL文件
- `README.md` - 更新文档说明

### 新增文件

- `docs/MOL_FORMAT.md` - MOL格式使用文档
- `examples/mol_format_example.py` - 使用示例（125行）
- `tests/test_mol_format.py` - 测试套件（184行）

### 使用方法

```python
# 读取MOL文件
from src.structure_parser import StructureParser
parser = StructureParser()
parser.read_mol("molecule.mol")

# Pipeline中使用
from src.gaussian_runner import InteractionEnergyPipeline
pipeline = InteractionEnergyPipeline()
results = pipeline.run_full_pipeline(
    molecule_a_file="mol_a.mol",
    molecule_b_file="mol_b.mol"
)
```

### 详细文档

请参考 [`docs/MOL_FORMAT.md`](docs/MOL_FORMAT.md)

---

**所有测试通过 ✓**
