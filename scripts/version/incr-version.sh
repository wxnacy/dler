#!/bin/bash

# incr-version.sh - 用于递增版本号的脚本

set -e # 遇到错误时退出

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

# 获取当前版本号
CURRENT_VERSION=$(grep -E 'var Version = "([^"]+)"' version.go | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$CURRENT_VERSION" ]; then
    print_error "无法从 version.go 文件中提取版本号"
    exit 1
fi

print_info "当前版本号: $CURRENT_VERSION"

# 解析版本号
IFS='.' read -ra VERSION_PARTS <<<"$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# 显示版本号组成部分
echo "主版本号: $MAJOR"
echo "次版本号: $MINOR"
echo "修订号: $PATCH"

# 获取当前分支名称
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# 询问要递增的部分
echo ""
echo "选择要递增的版本部分:"
echo "1) 主版本号 (MAJOR) - 不兼容的API变更"
echo "2) 次版本号 (MINOR) - 向后兼容的功能性新增"
echo "3) 修订号 (PATCH) - 向后兼容的问题修正"
echo "4) 取消"
echo ""
read -p "请输入选项 (1-4): " -n 1 -r
echo

case $REPLY in
1)
    NEW_VERSION="$((MAJOR + 1)).0.0"
    ;;
2)
    NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
    ;;
3)
    NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
    ;;
4)
    print_info "已取消操作"
    exit 0
    ;;
*)
    print_error "无效选项"
    exit 1
    ;;
esac

print_info "新版本号: $NEW_VERSION"

# 确认更新
echo ""
read -p "确认更新版本号到 $NEW_VERSION? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "已取消操作"
    exit 0
fi

# 更新 version.go 文件
print_info "正在更新 version.go 文件..."
sed -i.bak "s/var Version = \"$CURRENT_VERSION\"/var Version = \"$NEW_VERSION\"/" version.go

# 删除备份文件
rm version.go.bak

# 显示更改
echo ""
print_info "版本号已更新:"
echo "  从: $CURRENT_VERSION"
echo "  到: $NEW_VERSION"

# 提示提交更改
echo ""
print_info "请记得提交更改:"
echo "  git add version.go"
echo "  git commit -m \"chore(version): Incr version to $NEW_VERSION\""
echo "  git push origin $CURRENT_BRANCH"
echo ""
print_info "然后运行发布脚本:"
echo "  ./bin/release.sh"

# 询问是否自动执行git命令
echo ""
read -p "是否自动执行git提交和推送操作? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "正在执行git操作..."
    
    # 检查是否有未提交的更改
    if ! git diff --quiet version.go || ! git diff --cached --quiet version.go; then
        print_info "添加 version.go 到暂存区..."
        git add version.go
        
        print_info "提交更改..."
        git commit -m "chore(version): Incr version to $NEW_VERSION"
        
        print_info "推送到 $CURRENT_BRANCH 分支..."
        git push origin $CURRENT_BRANCH
        
        print_info "Git操作已完成!"
    else
        print_warning "version.go 文件没有更改，无需提交"
    fi
else
    print_info "请手动执行以下命令提交更改:"
    echo "  git add version.go"
    echo "  git commit -m \"chore(version): Incr version to $NEW_VERSION\""
    echo "  git push origin $CURRENT_BRANCH"
fi
