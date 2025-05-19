# 图像生成服务

这是一个基于mcp的图像生成服务项目，提供了将html代码图像转换成图片的功能。

## MCP Tools说明
- `save_image_to_file` 工具：将HTML内容转换为图片并保存为本地PNG文件
  - 参数：
    - `html_content`: 完整的HTML代码字符串


- `upload_image_to_s3` 工具：将HTML转换为图片并上传到S3兼容的对象存储（MinIO、OSS、AWS等）
  - 参数：
    - `html_content`: 完整的HTML代码字符串
  - 环境变量依赖：
    - `ENDPOINT_URL`: S3服务端点URL
    - `AWS_ACCESS_KEY`: 访问密钥
    - `AWS_SECRET_KEY`: 秘密密钥
    - `BUCKET_NAME`: 存储桶名称
    - `OBJECT_NAME`: 对象名称（可选，默认使用时间戳命名）
  - 返回值：
    - 上传成功后的文件URL
    - 如果上传失败返回错误信息
  - 功能特点：
    - 自动检查并创建目标存储桶
    - 支持自动安装 Playwright 及其 Chromium 浏览器驱动

## 功能特点
- 支持图像生成和处理
- 集成 AWS S3 和 MinIO 存储服务
- 使用 Playwright 进行自动化操作

## 系统要求

- Python 3.12 或更高版本
- 支持的操作系统：Windows、macOS、Linux

## 安装说明

1. 克隆项目仓库：
```bash
git clone [repository-url]
cd mcp_img_generation
```

2.下载  uv：
```bash
pip install uv
```

3.运行项目：
```bash
uv run main.py
```

> **注意**：项目使用 Playwright 的 Chromium 浏览器驱动，首次运行时会自动从官方源下载浏览器驱动包。
> 若因网络原因可能导致下载失败，建议：
> - 多次重试下载
> - 手动下载：
>  ```bash
>  playwright install-deps（linux系统才需要）
>  playwright install chromium



## 项目依赖

- boto3 >= 1.38.15
- mcp >= 1.7.1
- playwright >= 1.52.0

## 项目结构

```
mcp_img_generation/
├── img_generation/     # 主要代码目录
├── main.py            # 程序入口
├── pyproject.toml     # 项目配置
└── README.md          # 项目文档
```

## 开发说明

1. 确保已安装所有开发依赖
2. 遵循 Python 代码规范
3. 提交代码前进行测试


## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

