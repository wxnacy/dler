# 版本管理脚本

这个目录包含了用于管理项目版本的脚本。

## 脚本说明

### 1. show-version.sh
显示当前版本号和对应的 Git 标签。

```bash
./scripts/show-version.sh
```

### 2. bump-version.sh
递增版本号并更新 version.go 文件。

```bash
./scripts/bump-version.sh
```

支持三种版本号递增方式：
- 主版本号 (MAJOR) - 不兼容的API变更
- 次版本号 (MINOR) - 向后兼容的功能性新增
- 修订号 (PATCH) - 向后兼容的问题修正

### 3. release.sh
创建 Git 标签并推送到 GitHub。

```bash
./scripts/release.sh
```

## 使用流程

1. 使用 `bump-version.sh` 更新版本号
2. 提交版本号更改
3. 使用 `release.sh` 创建并推送标签

## 示例

```bash
# 查看当前版本
./scripts/show-version.sh

# 递增版本号
./scripts/bump-version.sh

# 提交更改
git add version.go
git commit -m "Bump version to 0.8.1"
git push origin dev_golang

# 创建并推送标签
./scripts/release.sh
```