#!/usr/bin/env python3
"""
Installation Test Script
This script tests if all required dependencies are properly installed.
Author: zhangshd
Date: 2025-10-12
"""

import sys
import os
from pathlib import Path


def test_python_version():
    """测试Python版本"""
    print("测试Python版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"  ✓ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("    需要Python 3.8或更高版本")
        return False


def test_import_packages():
    """测试必需的Python包是否可以导入"""
    print("\n测试Python包...")
    
    required_packages = {
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'openbabel': 'Open Babel',
        # 'rdkit': 'RDKit',  # RDKit可能安装失败，暂时可选
        # 'vina': 'AutoDock Vina',  # Vina可能需要特殊安装
    }
    
    all_success = True
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - 未安装")
            all_success = False
    
    return all_success


def test_optional_packages():
    """测试可选的Python包"""
    print("\n测试可选包...")
    
    optional_packages = {
        'rdkit': 'RDKit',
        'vina': 'AutoDock Vina Python绑定',
        'meeko': 'Meeko',
    }
    
    all_success = True
    for package, name in optional_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ⚠ {name} - 未安装 (可选)")
            all_success = False
    
    return all_success


def test_gaussian():
    """测试Gaussian是否可用"""
    print("\n测试Gaussian 16...")
    
    gaussian_paths = [
        "/opt/share/gaussian/g16",
        os.path.expanduser("~/g16"),
        "/usr/local/gaussian/g16"
    ]
    
    found = False
    for path in gaussian_paths:
        g16_exe = os.path.join(path, "g16")
        if os.path.exists(g16_exe):
            print(f"  ✓ 找到Gaussian 16: {path}")
            found = True
            break
    
    if not found:
        print("  ⚠ 未在常见位置找到Gaussian 16")
        print("    如果已安装，请手动指定路径")
    
    return found


def test_obabel():
    """测试Open Babel命令行工具"""
    print("\n测试Open Babel命令行工具...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['obabel', '-V'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✓ {version_line}")
            return True
        else:
            print("  ✗ obabel命令执行失败")
            return False
    except FileNotFoundError:
        print("  ✗ obabel命令未找到")
        return False
    except Exception as e:
        print(f"  ✗ 测试obabel时出错: {e}")
        return False


def test_vina_command():
    """测试Vina命令行工具"""
    print("\n测试AutoDock Vina命令行工具...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['vina', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 or 'AutoDock Vina' in result.stdout:
            print(f"  ✓ Vina已安装")
            return True
        else:
            print("  ⚠ Vina命令可能未正确安装")
            return False
    except FileNotFoundError:
        print("  ⚠ vina命令未找到 (对接功能将不可用)")
        return False
    except Exception as e:
        print(f"  ⚠ 测试vina时出错: {e}")
        return False


def test_meps_modules():
    """测试MEPS模块是否可以导入"""
    print("\n测试MEPS模块...")
    
    # 添加src目录到路径
    src_path = Path(__file__).parent.parent / 'src'
    sys.path.insert(0, str(src_path))
    
    modules = [
        'structure_parser',
        'gaussian_io',
        'gaussian_runner',
        'result_extractor',
        'vina_docking'
    ]
    
    all_success = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module} - 导入失败: {e}")
            all_success = False
    
    return all_success


def test_create_sample_structure():
    """测试创建示例结构文件"""
    print("\n测试创建示例结构...")
    
    src_path = Path(__file__).parent.parent / 'src'
    sys.path.insert(0, str(src_path))
    
    try:
        from structure_parser import StructureParser
        
        # 创建一个简单的水分子
        parser = StructureParser()
        parser.atoms = [
            ('O', 0.0, 0.0, 0.0),
            ('H', 0.957, 0.0, 0.0),
            ('H', -0.240, 0.927, 0.0)
        ]
        
        # 测试写入XYZ
        test_dir = Path(__file__).parent / 'test_output'
        test_dir.mkdir(exist_ok=True)
        
        xyz_file = test_dir / 'water.xyz'
        parser.write_xyz(str(xyz_file), comment="Test water molecule")
        
        if xyz_file.exists():
            print(f"  ✓ 成功创建测试文件: {xyz_file}")
            return True
        else:
            print("  ✗ 创建测试文件失败")
            return False
            
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("MEPS安装测试")
    print("="*60)
    
    tests = [
        ("Python版本", test_python_version),
        ("必需Python包", test_import_packages),
        ("可选Python包", test_optional_packages),
        ("Gaussian 16", test_gaussian),
        ("Open Babel命令", test_obabel),
        ("AutoDock Vina命令", test_vina_command),
        ("MEPS模块", test_meps_modules),
        ("创建示例结构", test_create_sample_structure),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n测试'{test_name}'时发生异常: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:<25} {status}")
    
    print("-"*60)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过! 系统已准备就绪。")
        return 0
    else:
        print("\n⚠️  部分测试未通过。请检查上述错误信息。")
        print("注意: 某些可选功能(如Vina对接)的测试失败不影响基本功能。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
