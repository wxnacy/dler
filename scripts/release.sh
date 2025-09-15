#!/bin/bash

# release.sh - 用于创建和推送版本标签的脚本

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在 Git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "当前目录不是 Git 仓库"
    exit 1
fi

# 获取当前版本号
VERSION=$(grep -E 'var Version = "([^"]+)"' version.go | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$VERSION" ]; then
    print_error "无法从 version.go 文件中提取版本号"
    exit 1
fi

print_info "当前版本号: $VERSION"

# 创建带 v 前缀的标签
TAG="v$VERSION"

# 检查标签是否已存在
if git rev-parse "$TAG" >/dev/null 2>&1; then
    print_error "标签 $TAG 已存在"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    print_warning "存在未提交的更改:"
    git status --porcelain
    echo ""
    read -p "是否继续发布? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "已取消发布"
        exit 0
    fi
else
    print_info "工作区干净，可以发布"
fi

# 创建标签
print_info "正在创建标签 $TAG..."
git tag -a "$TAG" -m "Release version $VERSION"

# 推送标签到远程仓库
print_info "正在推送标签到 GitHub..."
git push origin "$TAG"

print_info "成功创建并推送标签 $TAG"

# 可选：询问是否推送所有标签
echo ""
read -p "是否同时推送所有标签到 GitHub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "正在推送所有标签到 GitHub..."
    git push origin --tags
    print_info "所有标签已推送完成"
fi

print_info "版本发布完成！"