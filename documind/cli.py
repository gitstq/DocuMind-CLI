#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocuMind CLI - 命令行界面
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional

from .core import DocuMindEngine
from . import __version__


class Colors:
    """终端颜色"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'


def print_banner():
    """打印欢迎横幅"""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   📚 DocuMind-CLI v{__version__} - 本地文档智能分析引擎              ║
║                                                              ║
║   🧠 智能提取 · 📊 深度分析 · 🔒 本地优先 · 🚀 零依赖        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def print_progress(message: str, done: bool = False):
    """打印进度信息"""
    if done:
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
    else:
        print(f"{Colors.BLUE}⏳{Colors.RESET} {message}...", end='', flush=True)


def print_error(message: str):
    """打印错误信息"""
    print(f"\n{Colors.RED}✗ 错误: {message}{Colors.RESET}")


def print_success(message: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_info(label: str, value: str):
    """打印信息行"""
    print(f"  {Colors.CYAN}{label}:{Colors.RESET} {value}")


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{title}{Colors.RESET}")
    print(f"{Colors.GRAY}{'─' * 50}{Colors.RESET}")


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def run_analyze(args):
    """执行分析命令"""
    print_banner()

    file_path = args.file
    if not os.path.exists(file_path):
        print_error(f"文件不存在: {file_path}")
        sys.exit(1)

    print_progress(f"正在分析文档: {os.path.basename(file_path)}")

    engine = DocuMindEngine()

    try:
        report = engine.analyze(file_path)
        print_progress(f"正在分析文档: {os.path.basename(file_path)}", done=True)
    except Exception as e:
        print_error(f"分析失败: {str(e)}")
        sys.exit(1)

    # 输出分析结果
    print_section("📄 文档信息")
    print_info("文件名", report.document_info.filename)
    print_info("文件类型", report.document_info.file_type)
    print_info("文件大小", format_size(report.document_info.file_size))
    print_info("字符数", f"{report.document_info.char_count:,}")
    print_info("词数", f"{report.document_info.word_count:,}")
    print_info("行数", f"{report.document_info.line_count:,}")
    print_info("语言", report.language)

    print_section("📈 统计概览")
    print_info("文本块数", str(report.statistics['block_count']))
    print_info("知识单元数", str(report.statistics['knowledge_count']))

    if report.statistics['block_types']:
        print(f"\n  {Colors.CYAN}块类型分布:{Colors.RESET}")
        for btype, count in report.statistics['block_types'].items():
            bar = '█' * min(count, 20)
            print(f"    {btype:12} {bar} {count}")

    print_section("🎯 质量评分")
    readability = report.readability_score
    readability_color = Colors.GREEN if readability > 60 else Colors.YELLOW if readability > 40 else Colors.RED
    print_info("可读性分数", f"{readability_color}{readability:.1f}/100{Colors.RESET}")

    sentiment = report.sentiment_score
    sentiment_text = "正面 😊" if sentiment > 0.1 else "负面 😔" if sentiment < -0.1 else "中性 😐"
    sentiment_color = Colors.GREEN if sentiment > 0.1 else Colors.RED if sentiment < -0.1 else Colors.YELLOW
    print_info("情感倾向", f"{sentiment_color}{sentiment:+.3f} ({sentiment_text}){Colors.RESET}")

    print_section("🏷️ 主题分布")
    for topic, score in report.topic_distribution.items():
        bar = '█' * int(score * 30)
        print(f"  {topic:15} {Colors.MAGENTA}{bar}{Colors.RESET} {score:.1%}")

    print_section("🧠 提取的知识")

    # 摘要
    summary = next((k for k in report.knowledge_units if k.knowledge_type == 'summary'), None)
    if summary:
        print(f"\n  {Colors.BOLD}📝 摘要:{Colors.RESET}")
        print(f"  {Colors.GRAY}>{Colors.RESET} {summary.content[:300]}...")

    # 关键词
    keywords = [k for k in report.knowledge_units if k.knowledge_type == 'keyword']
    if keywords:
        print(f"\n  {Colors.BOLD}🔑 关键词:{Colors.RESET}")
        for k in keywords[:10]:
            print(f"    • {k.content} {Colors.GRAY}(置信度: {k.confidence:.3f}){Colors.RESET}")

    # 实体
    entities = [k for k in report.knowledge_units if k.knowledge_type == 'entity']
    if entities:
        print(f"\n  {Colors.BOLD}📌 实体:{Colors.RESET}")
        for k in entities[:8]:
            entity_type = k.metadata.get('entity_type', 'unknown')
            print(f"    • [{entity_type}] {k.content}")

    # 概念
    concepts = [k for k in report.knowledge_units if k.knowledge_type == 'concept']
    if concepts:
        print(f"\n  {Colors.BOLD}💡 核心概念:{Colors.RESET}")
        for k in concepts[:8]:
            level = k.metadata.get('level', 0)
            indent = '  ' * level
            print(f"    {indent}• {k.content}")

    # 导出报告
    if args.output:
        output_path = args.output
        output_format = args.format or 'json'

        print_progress(f"正在导出报告: {output_path}")
        try:
            engine.export_report(report, output_path, output_format)
            print_progress(f"正在导出报告: {output_path}", done=True)
            print_success(f"报告已导出: {output_path}")
        except Exception as e:
            print_error(f"导出失败: {str(e)}")

    print(f"\n{Colors.GREEN}{'='*50}{Colors.RESET}")
    print(f"{Colors.GREEN}✨ 分析完成!{Colors.RESET}")
    print(f"{Colors.GRAY}使用 --output 参数导出详细报告{Colors.RESET}")


def run_batch(args):
    """执行批量分析"""
    print_banner()

    directory = args.directory
    if not os.path.isdir(directory):
        print_error(f"目录不存在: {directory}")
        sys.exit(1)

    # 获取支持的文件
    supported_exts = {'.txt', '.md', '.markdown', '.json', '.csv', '.html', '.htm',
                      '.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.ts',
                      '.sh', '.yaml', '.yml', '.xml'}

    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if Path(filename).suffix.lower() in supported_exts:
                files.append(os.path.join(root, filename))

    if not files:
        print_error(f"目录中未找到支持的文档: {directory}")
        sys.exit(1)

    print(f"{Colors.CYAN}📁 找到 {len(files)} 个文档{Colors.RESET}\n")

    engine = DocuMindEngine()
    results = []

    for i, file_path in enumerate(files, 1):
        rel_path = os.path.relpath(file_path, directory)
        print(f"[{i}/{len(files)}] {Colors.BLUE}{rel_path}{Colors.RESET}", end=' ')

        try:
            report = engine.analyze(file_path)
            results.append({
                'file': rel_path,
                'status': 'success',
                'language': report.language,
                'word_count': report.document_info.word_count,
                'readability': report.readability_score,
                'sentiment': report.sentiment_score
            })
            print(f"{Colors.GREEN}✓{Colors.RESET}")
        except Exception as e:
            results.append({
                'file': rel_path,
                'status': 'error',
                'error': str(e)
            })
            print(f"{Colors.RED}✗{Colors.RESET}")

    # 输出汇总
    print_section("📊 批量分析汇总")
    success_count = sum(1 for r in results if r['status'] == 'success')
    print_info("成功", f"{Colors.GREEN}{success_count}{Colors.RESET}")
    print_info("失败", f"{Colors.RED}{len(results) - success_count}{Colors.RESET}")
    print_info("总计", str(len(results)))

    # 导出汇总
    if args.output:
        output_path = args.output
        print_progress(f"正在导出汇总: {output_path}")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'summary': {
                        'total': len(results),
                        'success': success_count,
                        'failed': len(results) - success_count
                    },
                    'results': results
                }, f, ensure_ascii=False, indent=2)
            print_progress(f"正在导出汇总: {output_path}", done=True)
        except Exception as e:
            print_error(f"导出失败: {str(e)}")


def run_compare(args):
    """执行文档对比"""
    print_banner()

    file1, file2 = args.files
    if not os.path.exists(file1):
        print_error(f"文件不存在: {file1}")
        sys.exit(1)
    if not os.path.exists(file2):
        print_error(f"文件不存在: {file2}")
        sys.exit(1)

    engine = DocuMindEngine()

    print_progress(f"正在分析文档1: {os.path.basename(file1)}")
    report1 = engine.analyze(file1)
    print_progress(f"正在分析文档1: {os.path.basename(file1)}", done=True)

    print_progress(f"正在分析文档2: {os.path.basename(file2)}")
    report2 = engine.analyze(file2)
    print_progress(f"正在分析文档2: {os.path.basename(file2)}", done=True)

    print_section("📊 文档对比")

    # 基础信息对比
    print(f"\n  {Colors.BOLD}📄 基础信息:{Colors.RESET}")
    print(f"  {'指标':<20} {'文档1':<20} {'文档2':<20}")
    print(f"  {'─'*60}")
    print(f"  {'文件名':<20} {report1.document_info.filename:<20} {report2.document_info.filename:<20}")
    print(f"  {'字符数':<20} {report1.document_info.char_count:<20,} {report2.document_info.char_count:<20,}")
    print(f"  {'词数':<20} {report1.document_info.word_count:<20,} {report2.document_info.word_count:<20,}")
    print(f"  {'行数':<20} {report1.document_info.line_count:<20,} {report2.document_info.line_count:<20,}")

    # 质量对比
    print(f"\n  {Colors.BOLD}🎯 质量对比:{Colors.RESET}")
    diff_readability = report1.readability_score - report2.readability_score
    diff_sentiment = report1.sentiment_score - report2.sentiment_score

    print(f"  {'可读性':<20} {report1.readability_score:.1f} {'↑' if diff_readability > 0 else '↓'} {abs(diff_readability):.1f}")
    print(f"  {'情感倾向':<20} {report1.sentiment_score:+.3f} {'↑' if diff_sentiment > 0 else '↓'} {abs(diff_sentiment):.3f}")

    # 关键词重叠
    keywords1 = {k.content for k in report1.knowledge_units if k.knowledge_type == 'keyword'}
    keywords2 = {k.content for k in report2.knowledge_units if k.knowledge_type == 'keyword'}
    common = keywords1 & keywords2

    print(f"\n  {Colors.BOLD}🔑 关键词重叠:{Colors.RESET}")
    print(f"  文档1关键词: {len(keywords1)}")
    print(f"  文档2关键词: {len(keywords2)}")
    print(f"  共同关键词: {len(common)} ({len(common)/max(len(keywords1), len(keywords2))*100:.1f}%)")
    if common:
        print(f"  {Colors.GRAY}共同: {', '.join(list(common)[:10])}{Colors.RESET}")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        prog='documind',
        description='📚 DocuMind-CLI - 本地文档智能分析与知识提取引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  documind analyze document.md              # 分析单个文档
  documind analyze doc.txt -o report.json   # 分析并导出JSON报告
  documind analyze doc.md -o report.html -f html  # 导出HTML报告
  documind batch ./docs -o summary.json     # 批量分析目录
  documind compare a.md b.md                # 对比两个文档

支持格式: txt, md, json, csv, html, py, js, java, cpp, go, rust, ts, yaml, xml
        """
    )

    parser.add_argument('--version', action='version', version=f'DocuMind-CLI v{__version__}')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析单个文档')
    analyze_parser.add_argument('file', help='要分析的文档路径')
    analyze_parser.add_argument('-o', '--output', help='输出报告路径')
    analyze_parser.add_argument('-f', '--format', choices=['json', 'markdown', 'html'],
                                help='输出格式 (默认: json)')

    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量分析目录')
    batch_parser.add_argument('directory', help='要分析的目录路径')
    batch_parser.add_argument('-o', '--output', help='输出汇总报告路径')

    # compare 命令
    compare_parser = subparsers.add_parser('compare', help='对比两个文档')
    compare_parser.add_argument('files', nargs=2, help='要对比的两个文档路径')

    args = parser.parse_args()

    if args.command == 'analyze':
        run_analyze(args)
    elif args.command == 'batch':
        run_batch(args)
    elif args.command == 'compare':
        run_compare(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
