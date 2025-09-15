# 脚本目录

这个目录包含了项目的各种脚本工具。

## 目录结构

```
scripts/
├── README.md          # 本文件
├── build.sh           # 构建脚本
├── run.sh             # 运行脚本
├── trans.sh           # 转换脚本
└── version/           # 版本管理脚本
    ├── bump-version.sh    # 版本递增脚本
    ├── release.sh         # 版本发布脚本
    └── show-version.sh    # 显示版本号脚本
```

## 使用说明

### 构建和运行
- `./scripts/build.sh` - 构建项目
- `./scripts/run.sh` - 运行项目

### 版本管理
版本管理脚本已移至 `scripts/version/` 目录：

```bash
# 查看当前版本
./scripts/version/show-version.sh

# 递增版本号
./scripts/version/bump-version.sh

# 发布新版本（创建并推送 Git 标签）
./scripts/version/release.sh
```

也可以使用 Makefile 命令：

```bash
# 查看当前版本
make version

# 递增版本号
make bump-version

# 发布新版本
make release
```