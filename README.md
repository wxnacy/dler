# dler - 文件下载器

dler 是一个用 Go 语言编写的文件下载器，支持以下功能：
- 基本的 HTTP/HTTPS 文件下载
- M3U8 流媒体下载
- Range 异步批量下载
- 自动解压 gzip 压缩内容
- 自动补全支持

## 安装

### 使用 Go 安装
```bash
go install github.com/wxnacy/dler@latest
```

### 从源码构建
```bash
git clone https://github.com/wxnacy/dler.git
cd dler
make build
```

### 安装到 GOPATH
```bash
# 构建并安装二进制文件和脚本到 GOPATH
make install

# 现在您可以直接使用 dler 命令
dler https://example.com/file.zip
```

## 使用方法

### 基本下载
```bash
# 下载文件到当前目录
dler https://example.com/file.zip

# 下载文件到指定目录
dler https://example.com/file.zip -d /path/to/download

# 下载文件到指定文件路径
dler https://example.com/file.zip -o /path/to/download/file.zip
```

### 使用 Makefile 运行
```bash
# 使用 make 运行程序（需要传递参数）
make run ARGS="https://example.com/file.zip"

# 或者使用 run-args 目标
make run-args ARGS="https://example.com/file.zip"
```

### M3U8 流媒体下载
```bash
# 下载 M3U8 流媒体
dler https://example.com/video.m3u8 --to-m3u8
```

### Range 异步批量下载
```bash
# 使用指定分片大小进行 Range 下载
dler https://example.com/largefile.zip -s 4194304  # 4MB 分片
```

### 环境变量配置

dler 支持通过环境变量配置默认下载目录：

```bash
export DLER_OUTPUT_DIR="$HOME/Downloads"
```

或者使用 [direnv](https://direnv.net/) 工具：

1. 复制示例配置文件：
   ```bash
   cp .envrc.example .envrc
   ```

2. 允许 direnv 配置：
   ```bash
   direnv allow
   ```

这样，所有下载将默认保存到 `$HOME/Downloads` 目录，除非使用 `-d` 或 `-o` 参数指定了其他路径。

## 自动补全

dler 支持 Zsh shell 的自动补全：

#### Zsh
```bash
# 使用安装脚本自动安装（推荐）
./scripts/completion/install_completion.sh

# 或者手动安装
# 将补全脚本复制到 ~/.zsh/completions 目录
mkdir -p ~/.zsh/completions
cp ./scripts/completion/dler.zsh ~/.zsh/completions/_dler

# 确保 ~/.zshrc 中包含以下配置
echo "fpath=(\$HOME/.zsh/completions \$fpath)" >> ~/.zshrc
echo "autoload -U compinit && compinit" >> ~/.zshrc
```

### 使用 Makefile 安装
```bash
# 安装 zsh 自动补全脚本到用户目录（无需管理员权限）
make install-completion

# 重新加载 shell 配置以使补全生效
# 对于 zsh:
source ~/.zshrc && compinit

# 或者简单地重新启动 shell
```

## 开发

### 构建
```bash
make build
```

### 测试
```bash
make test
```

### 代码检查
```bash
make check
```

### 版本管理
版本管理脚本已移至 `scripts/version/` 目录：

```bash
# 查看当前版本
./scripts/version/show-version.sh

# 递增版本号
./scripts/version/incr-version.sh

# 发布新版本（创建并推送 Git 标签）
./scripts/version/release.sh
```

也可以使用 Makefile 命令：

```bash
# 查看当前版本
make version

# 递增版本号
make incr-version

# 发布新版本
make release
```

## 许可证

[MIT](LICENSE)