# Vina 输出解析 Bug 修复报告

**日期**: 2025-10-12  
**修复模块**: `src/vina_docking.py`  
**影响范围**: AutoDock Vina 分子对接功能

---

## 🐛 问题描述

### 错误信息
```
ValueError: invalid literal for int() with base 10: '0%'
```

### 触发场景
用户在运行 `tutorial_example.py` 示例3（分步执行流程）时，在分子对接步骤遇到此错误。

### 错误堆栈
```python
File "/home/zhangsd/repos/MEPS/src/vina_docking.py", line 229, in _parse_vina_output
    'mode': int(parts[0]),
ValueError: invalid literal for int() with base 10: '0%'
```

---

## 🔍 问题分析

### 根本原因
AutoDock Vina 在运行时会输出进度信息，例如：
```
Refining results ... 0%
Refining results ... 10%
Refining results ... 100%
```

原有的解析逻辑只检查行首是否为数字字符，导致 "0%" 这样的进度行被误判为对接模式数据。

### 原有代码
```python
for line in lines:
    if line.strip() and line[0].isdigit():
        parts = line.split()
        if len(parts) >= 4:
            mode = {
                'mode': int(parts[0]),  # 这里会尝试将 "0%" 转换为整数
                'affinity': float(parts[1]),
                ...
            }
```

---

## ✅ 修复方案

### 改进策略
1. **区域检测**: 只在实际结果区域解析数据
2. **格式验证**: 检查是否包含 '%' 符号
3. **异常处理**: 添加 try-except 容错

### 修复后代码
```python
lines = output.split('\n')
in_results_section = False

for line in lines:
    # Check if we're in the results section
    if 'mode |   affinity' in line.lower() or 'kcal/mol' in line.lower():
        in_results_section = True
        continue
    
    # Parse docking mode information only in results section
    if in_results_section and line.strip() and line.strip()[0].isdigit():
        parts = line.split()
        # Ensure we have valid numeric data (not progress like "0%")
        if len(parts) >= 2 and parts[0].isdigit() and not '%' in parts[0]:
            try:
                mode = {
                    'mode': int(parts[0]),
                    'affinity': float(parts[1]),
                    'rmsd_lb': float(parts[2]) if len(parts) > 2 else None,
                    'rmsd_ub': float(parts[3]) if len(parts) > 3 else None
                }
                results['modes'].append(mode)
            except (ValueError, IndexError):
                continue
```

### 关键改进点
1. ✅ 添加 `in_results_section` 标志，只在检测到结果标题后才开始解析
2. ✅ 检查 `not '%' in parts[0]`，过滤进度百分比
3. ✅ 使用 `parts[0].isdigit()` 确保是纯数字
4. ✅ 添加 try-except 处理意外格式

---

## 🧪 测试验证

### 测试脚本
创建了 `tests/test_vina_parsing.py` 进行全面测试。

### 测试用例

#### 用例1: 带进度指示的输出
```
Computing transformation ... 0%
Computing transformation ... 100%
Performing search ... 0%
Performing search ... 100%
Refining results ... 0%
Refining results ... 100%

mode |   affinity | dist from best mode
     | (kcal/mol) | rmsd l.b.| rmsd u.b.
-----+------------+----------+----------
   1       -5.234      0.000      0.000
   2       -4.892      1.234      2.456
```

**结果**: ✅ 成功解析 2 个对接模式，忽略所有进度行

#### 用例2: 最小输出
```
mode |   affinity | dist from best mode
     | (kcal/mol) | rmsd l.b.| rmsd u.b.
-----+------------+----------+----------
   1       -6.789      0.000      0.000
```

**结果**: ✅ 成功解析 1 个对接模式

#### 用例3: 边界情况
```
Starting calculation at 09:30:00
0% complete
100% complete

mode |   affinity | dist from best mode
     | (kcal/mol) | rmsd l.b.| rmsd u.b.
-----+------------+----------+----------
   1       -7.890      0.000      0.000
```

**结果**: ✅ 成功解析 1 个对接模式，忽略其他以数字开头的非结果行

### 测试通过率
**3/3 测试用例全部通过** ✅

---

## 📊 影响评估

### 影响功能
- `VinaDocking.run_docking()` - 运行分子对接
- `VinaDocking.dock_two_molecules()` - 对接两个分子
- `InteractionEnergyPipeline.dock_molecules()` - 流程中的对接步骤

### 向后兼容性
✅ **完全兼容**
- 修复只改进了解析逻辑，不影响其他功能
- 所有已有测试继续通过
- API 接口无变化

---

## 📝 文档更新

已更新以下文档：
- ✅ `TEST_REPORT.md` - 添加 Vina 解析测试部分
- ✅ 创建 `tests/test_vina_parsing.py` - 专门测试脚本
- ✅ 创建 `VINA_PARSING_FIX.md` - 本文档

---

## 🎯 总结

### 修复状态
✅ **已完成并验证**

### 修复效果
- 彻底解决了 `ValueError: invalid literal for int() with base 10: '0%'` 错误
- 提高了解析的鲁棒性，能处理各种 Vina 输出格式
- 添加了完善的测试覆盖

### 建议
对于类似的文本解析任务，建议：
1. 明确定义解析区域（使用标志位）
2. 验证数据格式（不仅检查类型，还要检查内容）
3. 添加异常处理（容错机制）
4. 编写充分的测试用例（包括边界情况）

---

**修复人**: GitHub Copilot  
**审核人**: zhangsd  
**状态**: ✅ 已合并
