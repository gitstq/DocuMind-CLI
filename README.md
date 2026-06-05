<div align="center">

# 📚 DocuMind-CLI

**轻量级本地文档智能分析与知识提取引擎**

*Lightweight Local Document Intelligent Analysis & Knowledge Extraction Engine*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](.)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-orange)](.)

[简体中文](#简体中文) · [繁體中文](#繁體中文) · [English](#english)

</div>

---

## 简体中文

### 🎉 项目介绍

DocuMind-CLI 是一款**零依赖、本地优先**的命令行文档智能分析工具。它能够自动解析多种格式的文档，提取关键信息、生成智能摘要、分析情感倾向、构建知识图谱，并以美观的报告形式呈现分析结果。

**灵感来源**：在日常开发和学习中，我们经常需要快速理解大量文档内容。现有的文档分析工具要么需要联网调用API（存在隐私风险），要么依赖庞大的机器学习框架（安装复杂）。DocuMind-CLI 致力于提供一个**开箱即用、隐私安全、轻量高效**的本地文档分析解决方案。

**自研差异化亮点**：
- 🚀 **纯标准库实现**：零外部依赖，单文件可执行
- 🔒 **完全本地运行**：文档内容不上传云端，保护隐私
- 🌐 **多语言支持**：原生支持中文和英文文档分析
- 📊 **多格式报告**：支持 JSON / Markdown / HTML 三种导出格式
- 🎯 **智能分析**：关键词提取、实体识别、情感分析、可读性评分

### ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 📄 **多格式解析** | 支持 TXT / Markdown / JSON / CSV / HTML / 代码文件 | ✅ |
| 🔑 **关键词提取** | 基于 TF 算法智能提取文档关键词 | ✅ |
| 📌 **实体识别** | 自动识别邮箱、URL、IP地址、版本号 | ✅ |
| 📝 **智能摘要** | 基于句子重要性算法自动生成摘要 | ✅ |
| 😊 **情感分析** | 分析文档情感倾向（正面/负面/中性） | ✅ |
| 📊 **可读性评分** | 计算文档可读性分数 | ✅ |
| 🏷️ **主题分类** | 自动识别文档所属主题领域 | ✅ |
| 💡 **知识图谱** | 构建文档知识结构图谱 | ✅ |
| 🖥️ **美观 CLI** | 彩色终端输出，进度提示 | ✅ |
| 📦 **批量处理** | 支持目录批量分析 | ✅ |
| ⚖️ **文档对比** | 对比两份文档的相似度 | ✅ |

### 🚀 快速开始

#### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows / macOS / Linux

#### 安装方式

**方式一：pip 安装（推荐）**

```bash
pip install documind-cli
```

**方式二：从源码安装**

```bash
git clone https://github.com/gitstq/DocuMind-CLI.git
cd DocuMind-CLI
pip install -e .
```

**方式三：使用可执行文件**

从 [Releases](https://github.com/gitstq/DocuMind-CLI/releases) 页面下载对应平台的可执行文件。

#### 基本使用

```bash
# 分析单个文档
documind analyze document.md

# 分析并导出 JSON 报告
documind analyze document.txt -o report.json

# 导出 HTML 可视化报告
documind analyze document.md -o report.html -f html

# 批量分析目录
documind batch ./docs -o summary.json

# 对比两个文档
documind compare doc1.md doc2.md
```

### 📖 详细使用指南

#### 支持的文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| 纯文本 | `.txt` | 通用文本文件 |
| Markdown | `.md`, `.markdown` | 支持标题、列表、代码块解析 |
| JSON | `.json` | 结构化数据文件 |
| CSV | `.csv` | 表格数据文件 |
| HTML | `.html`, `.htm` | 网页文件（自动提取正文） |
| Python | `.py` | Python 源代码 |
| JavaScript | `.js`, `.ts` | JS/TS 源代码 |
| Java | `.java` | Java 源代码 |
| C/C++ | `.c`, `.cpp` | C/C++ 源代码 |
| Go | `.go` | Go 源代码 |
| Rust | `.rs` | Rust 源代码 |
| Shell | `.sh` | Shell 脚本 |
| YAML | `.yaml`, `.yml` | YAML 配置文件 |
| XML | `.xml` | XML 文件 |

#### 报告格式说明

**JSON 格式**：包含完整的分析数据，适合程序化处理
```bash
documind analyze doc.md -o report.json
```

**Markdown 格式**：适合阅读和人编辑
```bash
documind analyze doc.md -o report.md -f markdown
```

**HTML 格式**：可视化报告，可在浏览器中查看
```bash
documind analyze doc.md -o report.html -f html
```

### 💡 设计思路与迭代规划

#### 技术选型原因

- **纯标准库实现**：避免依赖冲突，确保长期可维护性
- **正则表达式分词**：无需安装 NLP 库即可实现中文分词
- **TF 关键词算法**：简单高效，无需预训练模型
- **位置加权摘要**：利用文档结构信息提升摘要质量

#### 后续迭代计划

- [ ] 支持 PDF 文档解析
- [ ] 支持 Word 文档解析
- [ ] 引入 TF-IDF 改进关键词提取
- [ ] 支持自定义停用词表
- [ ] 添加词云图生成
- [ ] 支持文档相似度计算（余弦相似度）

### 📦 打包与部署

#### 构建可执行文件

```bash
python build.py
```

构建完成后，可执行文件位于 `dist/documind`。

#### 跨平台发布

```bash
python build.py --release
```

### 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

- 提交 Issue 请描述清楚问题和复现步骤
- 提交 PR 请确保通过所有单元测试
- 遵循现有代码风格

### 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 繁體中文

### 🎉 項目介紹

DocuMind-CLI 是一款**零依賴、本地優先**的命令列文件智能分析工具。它能夠自動解析多種格式的文件，提取關鍵資訊、生成智能摘要、分析情感傾向、建構知識圖譜，並以美觀的報告形式呈現分析結果。

**自研差異化亮點**：
- 🚀 **純標準庫實現**：零外部依賴，單文件可執行
- 🔒 **完全本地運行**：文件內容不上傳雲端，保護隱私
- 🌐 **多語言支援**：原生支援中文和英文文件分析
- 📊 **多格式報告**：支援 JSON / Markdown / HTML 三種匯出格式
- 🎯 **智能分析**：關鍵詞提取、實體識別、情感分析、可讀性評分

### ✨ 核心特性

| 特性 | 描述 | 狀態 |
|------|------|------|
| 📄 **多格式解析** | 支援 TXT / Markdown / JSON / CSV / HTML / 程式碼文件 | ✅ |
| 🔑 **關鍵詞提取** | 基於 TF 演算法智能提取文件關鍵詞 | ✅ |
| 📌 **實體識別** | 自動識別電子郵件、URL、IP位址、版本號 | ✅ |
| 📝 **智能摘要** | 基於句子重要性演算法自動生成摘要 | ✅ |
| 😊 **情感分析** | 分析文件情感傾向（正面/負面/中性） | ✅ |
| 📊 **可讀性評分** | 計算文件可讀性分數 | ✅ |
| 🏷️ **主題分類** | 自動識別文件所屬主題領域 | ✅ |
| 💡 **知識圖譜** | 建構文件知識結構圖譜 | ✅ |

### 🚀 快速開始

#### 安裝

```bash
pip install documind-cli
```

#### 基本使用

```bash
# 分析單個文件
documind analyze document.md

# 分析並匯出 JSON 報告
documind analyze document.txt -o report.json

# 匯出 HTML 視覺化報告
documind analyze document.md -o report.html -f html

# 批量分析目錄
documind batch ./docs -o summary.json

# 對比兩個文件
documind compare doc1.md doc2.md
```

### 📄 開源協議

本項目採用 [MIT License](LICENSE) 開源協議。

---

## English

### 🎉 Introduction

DocuMind-CLI is a **zero-dependency, privacy-first** command-line document intelligence analysis tool. It automatically parses documents in multiple formats, extracts key information, generates intelligent summaries, analyzes sentiment, builds knowledge graphs, and presents analysis results in beautiful reports.

**Key Differentiators**:
- 🚀 **Pure Standard Library**: Zero external dependencies, single-file executable
- 🔒 **Fully Local**: Document content never leaves your machine
- 🌐 **Multi-language**: Native support for Chinese and English documents
- 📊 **Multiple Formats**: Export to JSON / Markdown / HTML
- 🎯 **Intelligent Analysis**: Keywords, entities, sentiment, readability scoring

### ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| 📄 **Multi-format Parsing** | TXT / Markdown / JSON / CSV / HTML / Code files | ✅ |
| 🔑 **Keyword Extraction** | TF-based intelligent keyword extraction | ✅ |
| 📌 **Entity Recognition** | Auto-detect emails, URLs, IPs, versions | ✅ |
| 📝 **Smart Summary** | Sentence importance-based summarization | ✅ |
| 😊 **Sentiment Analysis** | Document sentiment scoring | ✅ |
| 📊 **Readability Score** | Flesch-style readability calculation | ✅ |
| 🏷️ **Topic Classification** | Auto-identify document topics | ✅ |
| 💡 **Knowledge Graph** | Build document knowledge structure | ✅ |

### 🚀 Quick Start

#### Installation

```bash
pip install documind-cli
```

#### Usage

```bash
# Analyze a single document
documind analyze document.md

# Export JSON report
documind analyze document.txt -o report.json

# Export HTML visualization
documind analyze document.md -o report.html -f html

# Batch analyze directory
documind batch ./docs -o summary.json

# Compare two documents
documind compare doc1.md doc2.md
```

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ by DocuMind Team**

[⭐ Star us on GitHub](https://github.com/gitstq/DocuMind-CLI) · [🐛 Report Issue](https://github.com/gitstq/DocuMind-CLI/issues)

</div>
