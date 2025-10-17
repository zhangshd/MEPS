# MOL Format Support - 更新说明

## 版本 v1.1.1 (2025-10-17)

### 重要Bug修复 🐛

✅ **MOL2解析错误修复**
- **问题**: MOL2文件解析时错误地使用了原子类型（N.ar, C.ar, C.3等）而非元素符号
- **影响**: 生成的Gaussian输入文件包含无效的原子标签，导致计算失败
- **修复**: 将 `atom.GetType()` 改为 `ob.GetSymbol(atom.GetAtomicNum())`
- **修改文件**: 
  - `src/structure_parser.py` - `_read_mol_openbabel()` 和 `read_mol2()` 方法
- **详细文档**: [`docs/MOL2_PARSING_FIX.md`](docs/MOL2_PARSING_FIX.md)

### 修复前后对比

**修复前** (错误的原子类型):
```
 Nar      -0.050900       0.051700       0.012900
 Car      -1.389700       0.000000      -0.008000
 C3      -1.989300      -1.374700       0.060200
 Npl       3.119200       0.935000      -1.817900
```

**修复后** (正确的元素符号):
```
 N       -0.050900       0.051700       0.012900
 C       -1.389700       0.000000      -0.008000
 C       -1.989300      -1.374700       0.060200
 N        3.119200       0.935000      -1.817900
```

---

## 版本 v1.1.0 (2025-10-16)

### 新增功能

✅ **MOL/SDF/MOL2格式支持**
- 支持读取 `.mol`, `.sdf` 和 `.mol2` 格式文件
- 支持写入 `.mol` 和 `.mol2` 格式文件
- 自动提取原子坐标、电荷和自旋多重度
- MOL/SDF: 支持OpenBabel和RDKit双后端
- MOL2: 使用OpenBabel处理

### 修改的文件

- `src/structure_parser.py` - 添加 `read_mol()`, `write_mol()`, `read_mol2()`, `write_mol2()` 方法
- `src/gaussian_runner.py` - Pipeline集成MOL/MOL2格式
- `scripts/run_pipeline.py` - 命令行支持MOL/MOL2文件
- `README.md` - 更新文档说明

### 新增文件

- `docs/MOL_FORMAT.md` - MOL格式使用文档
- `examples/mol_format_example.py` - 使用示例（125行）
- `tests/test_mol_format.py` - 测试套件（184行）

### 使用方法

```python
# 读取MOL/MOL2文件
from src.structure_parser import StructureParser
parser = StructureParser()
parser.read_mol("molecule.mol")
parser.read_mol2("molecule.mol2")

# 写入MOL/MOL2文件
parser.write_mol("output.mol")
parser.write_mol2("output.mol2")

# Pipeline中使用
from src.gaussian_runner import InteractionEnergyPipeline
pipeline = InteractionEnergyPipeline()
results = pipeline.run_full_pipeline(
    molecule_a_file="mol_a.mol2",
    molecule_b_file="mol_b.mol2"
)
```

### 详细文档

请参考 [`docs/MOL_FORMAT.md`](docs/MOL_FORMAT.md)

---

**所有测试通过 ✓**
