#!/bin/bash
"""
MEPS安装和环境配置脚本
Author: zhangshd
Date: 2025-10-12

此脚本将帮助你配置MEPS项目的运行环境
"""

echo "=========================================="
echo "MEPS - 分子间相互作用能自动化计算流程"
echo "环境配置脚本"
echo "=========================================="
echo ""

# 检查conda是否已安装
if ! command -v conda &> /dev/null
then
    echo "错误: 未找到conda命令"
    echo "请先安装Anaconda或Miniconda"
    echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✓ 检测到conda: $(conda --version)"
echo ""

# 检查Gaussian是否存在
GAUSSIAN_ROOT="/opt/share/gaussian/g16"
if [ ! -d "$GAUSSIAN_ROOT" ]; then
    echo "警告: 未在默认位置找到Gaussian 16"
    echo "默认路径: $GAUSSIAN_ROOT"
    read -p "请输入Gaussian 16的安装路径 (回车跳过): " USER_GAUSSIAN
    if [ ! -z "$USER_GAUSSIAN" ]; then
        GAUSSIAN_ROOT="$USER_GAUSSIAN"
    fi
fi

if [ -d "$GAUSSIAN_ROOT" ]; then
    echo "✓ 找到Gaussian 16: $GAUSSIAN_ROOT"
else
    echo "⚠️  未找到Gaussian 16，后续可能需要手动配置"
fi
echo ""

# 询问是否创建conda环境
read -p "是否创建名为'meps'的conda环境? (y/n): " CREATE_ENV

if [ "$CREATE_ENV" = "y" ] || [ "$CREATE_ENV" = "Y" ]; then
    echo ""
    echo "创建conda环境..."
    
    # 检查环境是否已存在
    if conda env list | grep -q "^meps "; then
        echo "环境'meps'已存在"
        read -p "是否删除并重新创建? (y/n): " RECREATE
        if [ "$RECREATE" = "y" ] || [ "$RECREATE" = "Y" ]; then
            echo "删除现有环境..."
            conda env remove -n meps -y
        else
            echo "跳过环境创建"
            exit 0
        fi
    fi
    
    echo "从environment.yml创建环境..."
    conda env create -f environment.yml
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ conda环境创建成功!"
        echo ""
        echo "要激活环境，请运行:"
        echo "  conda activate meps"
        echo ""
        echo "激活环境后，可以运行测试:"
        echo "  python tests/test_installation.py"
    else
        echo ""
        echo "✗ 环境创建失败"
        echo "请检查environment.yml文件和网络连接"
        exit 1
    fi
else
    echo "跳过环境创建"
fi

echo ""
echo "=========================================="
echo "配置完成!"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 激活conda环境: conda activate meps"
echo "2. 运行测试: python tests/test_installation.py"
echo "3. 查看示例: python examples/tutorial_example.py"
echo "4. 运行计算: python scripts/run_pipeline.py --help"
echo ""
