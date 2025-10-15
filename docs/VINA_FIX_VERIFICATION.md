# 验证 Vina 解析修复的步骤

## 快速验证

### 1. 运行解析测试
```bash
cd /home/zhangsd/repos/MEPS
conda activate meps
python tests/test_vina_parsing.py
```

预期输出：
```
✅ 所有测试通过! Vina 输出解析功能已修复
```

### 2. 重新运行失败的示例
```bash
cd /home/zhangsd/repos/MEPS/examples
conda activate meps
python tutorial_example.py
# 选择 3 (分步执行流程)
```

这次应该能正常通过分子对接步骤。

### 3. 单独测试 Vina 对接功能
```bash
cd /home/zhangsd/repos/MEPS
conda activate meps

python -c "
import sys
sys.path.insert(0, '/home/zhangsd/repos/MEPS')

from src.vina_docking import VinaDocking
from src.structure_parser import StructureParser

# 读取结构
benzene = StructureParser()
benzene.read_xyz('example/benzene.xyz')

methane = StructureParser()
methane.read_xyz('example/methane.xyz')

# 创建对接器
docker = VinaDocking()

# 准备文件
import os
os.makedirs('test_vina/vina', exist_ok=True)
benzene.write_pdb('test_vina/vina/receptor.pdb')
methane.write_pdb('test_vina/vina/ligand.pdb')

# 计算搜索框
center, size = docker.calculate_search_box(
    'test_vina/vina/receptor.pdb',
    'test_vina/vina/ligand.pdb'
)

print(f'✓ 搜索框计算成功')
print(f'  中心: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})')
print(f'  尺寸: ({size[0]:.2f}, {size[1]:.2f}, {size[2]:.2f})')
print()
print('✅ Vina 对接准备功能正常')
"
```

## 修复的具体内容

### 问题
原来的代码会将 Vina 输出中的进度信息（如 "0%", "10%"）误判为对接结果，导致：
```
ValueError: invalid literal for int() with base 10: '0%'
```

### 解决方案
1. **区域检测**: 只在找到 "mode | affinity" 标题后才开始解析
2. **格式验证**: 检查数据不包含 '%' 符号
3. **异常处理**: 添加 try-except 捕获解析错误

### 修改的文件
- `src/vina_docking.py` - 修复 `_parse_vina_output()` 方法

### 新增的文件
- `tests/test_vina_parsing.py` - Vina 输出解析测试
- `docs/VINA_PARSING_FIX.md` - 详细修复报告

### 更新的文件
- `TEST_REPORT.md` - 添加 Vina 解析测试章节

## 预期行为

修复后，Vina 输出解析应该：
- ✅ 忽略所有进度百分比（0%, 10%, 100% 等）
- ✅ 正确识别结果区域（"mode | affinity" 之后）
- ✅ 准确提取对接模式数据（mode, affinity, RMSD）
- ✅ 处理各种 Vina 版本的输出格式

## 故障排除

如果仍然遇到问题：

1. **检查 Vina 版本**
```bash
conda run -n meps vina --version
```

2. **查看实际的 Vina 输出**
在对接失败时，检查终端输出或日志文件，看是否有意外的格式

3. **运行调试模式**
```python
from src.vina_docking import VinaDocking
docker = VinaDocking()

# 手动解析某个 Vina 输出
with open('vina_output.txt', 'r') as f:
    output = f.read()
    
results = docker._parse_vina_output(output)
print(f"找到 {len(results['modes'])} 个对接模式")
for mode in results['modes']:
    print(mode)
```

## 联系支持

如果问题持续存在，请提供：
- Vina 版本信息
- 完整的错误堆栈
- Vina 的原始输出（如果可能）
