#!/bin/bash

# show-version.sh - 用于显示当前版本号的脚本

# 获取当前版本号
VERSION=$(grep -E 'var Version = "([^"]+)"' version.go | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$VERSION" ]; then
    echo "错误：无法从 version.go 文件中提取版本号"
    exit 1
fi

echo "当前版本号: $VERSION"
echo "对应的 Git 标签: v$VERSION"