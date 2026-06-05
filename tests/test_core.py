#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocuMind 核心模块测试
"""

import os
import tempfile
import unittest
from pathlib import Path

from documind.core import (
    DocumentParser, TextAnalyzer, KnowledgeExtractor,
    DocuMindEngine, DocumentInfo, TextBlock, ExtractedKnowledge
)


class TestDocumentParser(unittest.TestCase):
    """测试文档解析器"""

    def setUp(self):
        self.parser = DocumentParser()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_temp_file(self, content: str, suffix: str = '.txt') -> str:
        """创建临时文件"""
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.temp_dir)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def test_parse_txt(self):
        """测试解析纯文本"""
        content = "这是第一段。\n\n这是第二段。\n\n这是第三段。"
        path = self._create_temp_file(content, '.txt')
        doc_info, blocks = self.parser.parse(path)

        self.assertEqual(doc_info.file_type, 'text')
        self.assertGreater(doc_info.char_count, 0)
        self.assertEqual(len(blocks), 3)

    def test_parse_markdown(self):
        """测试解析Markdown"""
        content = """# 标题1

这是正文段落。

## 标题2

- 列表项1
- 列表项2

> 引用内容

```python
print("hello")
```
"""
        path = self._create_temp_file(content, '.md')
        doc_info, blocks = self.parser.parse(path)

        self.assertEqual(doc_info.file_type, 'markdown')
        self.assertTrue(any(b.block_type == 'heading' for b in blocks))
        self.assertTrue(any(b.block_type == 'list' for b in blocks))
        self.assertTrue(any(b.block_type == 'quote' for b in blocks))
        self.assertTrue(any(b.block_type == 'code' for b in blocks))

    def test_parse_code(self):
        """测试解析代码文件"""
        content = "def hello():\n    print('world')\n"
        path = self._create_temp_file(content, '.py')
        doc_info, blocks = self.parser.parse(path)

        self.assertEqual(doc_info.file_type, 'code')
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].metadata['language'], 'python')

    def test_detect_encoding(self):
        """测试编码检测"""
        content = "中文内容测试"
        path = self._create_temp_file(content, '.txt')
        encoding = self.parser.detect_encoding(path)
        self.assertIn(encoding, ['utf-8', 'gbk', 'gb2312'])


class TestTextAnalyzer(unittest.TestCase):
    """测试文本分析器"""

    def setUp(self):
        self.analyzer = TextAnalyzer()

    def test_detect_language_zh(self):
        """测试中文检测"""
        text = "这是一段中文文本，用于测试语言检测功能。"
        result = self.analyzer.detect_language(text)
        self.assertEqual(result, 'zh')

    def test_detect_language_en(self):
        """测试英文检测"""
        text = "This is an English text for testing language detection."
        result = self.analyzer.detect_language(text)
        self.assertEqual(result, 'en')

    def test_extract_keywords_zh(self):
        """测试中文关键词提取"""
        text = "Python是一种流行的编程语言。Python广泛应用于数据分析、人工智能和Web开发。Python的语法简洁优雅。"
        keywords = self.analyzer.extract_keywords(text, top_k=5)
        self.assertGreater(len(keywords), 0)
        self.assertTrue(all(isinstance(k, tuple) and len(k) == 2 for k in keywords))

    def test_extract_keywords_en(self):
        """测试英文关键词提取"""
        text = "Python is a popular programming language. Python is widely used in data analysis, artificial intelligence, and web development."
        keywords = self.analyzer.extract_keywords(text, top_k=5)
        self.assertGreater(len(keywords), 0)

    def test_extract_entities(self):
        """测试实体提取"""
        text = "Contact us at test@example.com or visit https://example.com. Server IP: 192.168.1.1. Version: v1.2.3"
        entities = self.analyzer.extract_entities(text)

        entity_types = [e.metadata.get('entity_type') for e in entities]
        self.assertIn('email', entity_types)
        self.assertIn('url', entity_types)
        self.assertIn('ip_address', entity_types)
        self.assertIn('version', entity_types)

    def test_generate_summary(self):
        """测试摘要生成"""
        text = "第一段介绍背景。第二段说明方法。第三段展示结果。第四段讨论影响。第五段总结结论。"
        summary = self.analyzer.generate_summary(text, max_sentences=2)
        self.assertGreater(len(summary), 0)
        # 验证摘要不为空且从原文中提取
        self.assertIn(summary[:5], text)

    def test_analyze_sentiment(self):
        """测试情感分析"""
        positive = "This is great and wonderful!"
        negative = "This is terrible and awful."
        neutral = "This is a book."

        self.assertGreater(self.analyzer.analyze_sentiment(positive), 0)
        self.assertLess(self.analyzer.analyze_sentiment(negative), 0)

    def test_calculate_readability(self):
        """测试可读性计算"""
        text = "The cat sat on the mat. It was a sunny day."
        score = self.analyzer.calculate_readability(text)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_extract_topics(self):
        """测试主题提取"""
        text = "Python programming software development API database server cloud technology code"
        topics = self.analyzer.extract_topics(text)
        self.assertIn('technology', topics)


class TestKnowledgeExtractor(unittest.TestCase):
    """测试知识提取器"""

    def setUp(self):
        self.analyzer = TextAnalyzer()
        self.extractor = KnowledgeExtractor(self.analyzer)

    def test_extract_all(self):
        """测试提取所有知识"""
        blocks = [
            TextBlock(content="Python编程指南", block_type="heading", level=1),
            TextBlock(content="Python是一种强大的编程语言。", block_type="paragraph"),
            TextBlock(content="联系: test@example.com", block_type="paragraph"),
        ]

        knowledge = self.extractor.extract_all(blocks)
        self.assertGreater(len(knowledge), 0)

        types = [k.knowledge_type for k in knowledge]
        self.assertIn('keyword', types)
        self.assertIn('summary', types)

    def test_build_knowledge_graph(self):
        """测试构建知识图谱"""
        knowledge = [
            ExtractedKnowledge('keyword', 'Python', 0.9, [0]),
            ExtractedKnowledge('keyword', '编程', 0.8, [0, 1]),
            ExtractedKnowledge('entity', 'test@example.com', 1.0, [1]),
        ]

        graph = self.extractor.build_knowledge_graph(knowledge)
        self.assertIn('nodes', graph)
        self.assertIn('edges', graph)
        self.assertEqual(len(graph['nodes']), 3)


class TestDocuMindEngine(unittest.TestCase):
    """测试DocuMind主引擎"""

    def setUp(self):
        self.engine = DocuMindEngine()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_temp_file(self, content: str, suffix: str = '.txt') -> str:
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.temp_dir)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def test_analyze(self):
        """测试完整分析流程"""
        content = """# 测试文档

这是一个用于测试的文档。

## 功能介绍

- 功能1：文本分析
- 功能2：知识提取

联系: test@example.com
"""
        path = self._create_temp_file(content, '.md')
        report = self.engine.analyze(path)

        self.assertIsNotNone(report.document_info)
        self.assertEqual(report.document_info.file_type, 'markdown')
        self.assertGreater(len(report.text_blocks), 0)
        self.assertGreater(len(report.knowledge_units), 0)
        self.assertIn('block_count', report.statistics)
        self.assertIn('readability_score', report.__dict__)
        self.assertIn('sentiment_score', report.__dict__)

    def test_export_report_json(self):
        """测试导出JSON报告"""
        content = "测试内容"
        path = self._create_temp_file(content, '.txt')
        report = self.engine.analyze(path)

        output_path = os.path.join(self.temp_dir, 'report.json')
        self.engine.export_report(report, output_path, 'json')

        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_export_report_markdown(self):
        """测试导出Markdown报告"""
        content = "# 标题\n\n正文内容"
        path = self._create_temp_file(content, '.md')
        report = self.engine.analyze(path)

        output_path = os.path.join(self.temp_dir, 'report.md')
        self.engine.export_report(report, output_path, 'markdown')

        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('DocuMind', content)

    def test_export_report_html(self):
        """测试导出HTML报告"""
        content = "测试HTML导出"
        path = self._create_temp_file(content, '.txt')
        report = self.engine.analyze(path)

        output_path = os.path.join(self.temp_dir, 'report.html')
        self.engine.export_report(report, output_path, 'html')

        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<html', content)
        self.assertIn('</html>', content)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_pipeline(self):
        """测试完整流程"""
        engine = DocuMindEngine()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文档
            doc_path = os.path.join(tmpdir, 'test.md')
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write("""# 项目文档

## 概述

本项目是一个文档分析工具，支持多种格式。

## 功能

- 智能分析
- 知识提取
- 报告生成

联系: dev@example.com
官网: https://example.com
""")

            # 分析
            report = engine.analyze(doc_path)

            # 验证
            self.assertEqual(report.document_info.filename, 'test.md')
            self.assertTrue(any(b.block_type == 'heading' for b in report.text_blocks))
            self.assertTrue(any(b.block_type == 'list' for b in report.text_blocks))

            # 导出各种格式
            for fmt in ['json', 'markdown', 'html']:
                output_path = os.path.join(tmpdir, f'report.{fmt}')
                engine.export_report(report, output_path, fmt)
                self.assertTrue(os.path.exists(output_path))


if __name__ == '__main__':
    unittest.main()
