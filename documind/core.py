#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocuMind Core Engine
文档智能分析核心引擎

提供文档解析、文本分析、知识提取、语义理解等核心能力
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import Counter
import urllib.request
import urllib.parse


@dataclass
class DocumentInfo:
    """文档基本信息"""
    filename: str
    file_type: str
    file_size: int
    char_count: int
    word_count: int
    line_count: int
    md5_hash: str


@dataclass
class TextBlock:
    """文本块"""
    content: str
    block_type: str  # paragraph, heading, list, code, quote, table
    level: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ExtractedKnowledge:
    """提取的知识单元"""
    knowledge_type: str  # entity, relation, concept, keyword, summary
    content: str
    confidence: float
    source_blocks: List[int]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AnalysisReport:
    """分析报告"""
    document_info: DocumentInfo
    text_blocks: List[TextBlock]
    knowledge_units: List[ExtractedKnowledge]
    statistics: Dict[str, Any]
    readability_score: float
    sentiment_score: float
    topic_distribution: Dict[str, float]
    language: str


class DocumentParser:
    """文档解析器 - 支持多种格式"""

    SUPPORTED_FORMATS = {
        '.txt': 'text',
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.json': 'json',
        '.csv': 'csv',
        '.html': 'html',
        '.htm': 'html',
        '.py': 'code',
        '.js': 'code',
        '.java': 'code',
        '.cpp': 'code',
        '.c': 'code',
        '.go': 'code',
        '.rs': 'code',
        '.ts': 'code',
        '.sh': 'code',
        '.yaml': 'code',
        '.yml': 'code',
        '.xml': 'code',
    }

    def __init__(self):
        self.encoding_fallbacks = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'cp1252']

    def detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        for encoding in self.encoding_fallbacks:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        return 'utf-8'

    def parse(self, file_path: str) -> Tuple[DocumentInfo, List[TextBlock]]:
        """解析文档"""
        path = Path(file_path)
        ext = path.suffix.lower()
        file_type = self.SUPPORTED_FORMATS.get(ext, 'unknown')

        # 读取文件内容
        encoding = self.detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()

        # 计算文件信息
        file_size = path.stat().st_size
        char_count = len(content)
        word_count = len(content.split())
        line_count = content.count('\n') + 1
        md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

        doc_info = DocumentInfo(
            filename=path.name,
            file_type=file_type,
            file_size=file_size,
            char_count=char_count,
            word_count=word_count,
            line_count=line_count,
            md5_hash=md5_hash
        )

        # 根据文件类型解析
        if file_type == 'markdown':
            blocks = self._parse_markdown(content)
        elif file_type == 'json':
            blocks = self._parse_json(content)
        elif file_type == 'csv':
            blocks = self._parse_csv(content)
        elif file_type == 'html':
            blocks = self._parse_html(content)
        elif file_type == 'code':
            blocks = self._parse_code(content, ext)
        else:
            blocks = self._parse_text(content)

        return doc_info, blocks

    def _parse_markdown(self, content: str) -> List[TextBlock]:
        """解析Markdown文档"""
        blocks = []
        lines = content.split('\n')
        current_block = []
        current_type = 'paragraph'
        in_code_block = False
        code_language = ''

        for line in lines:
            # 代码块处理
            if line.startswith('```'):
                if in_code_block:
                    # 结束代码块
                    if current_block:
                        blocks.append(TextBlock(
                            content='\n'.join(current_block),
                            block_type='code',
                            metadata={'language': code_language}
                        ))
                    current_block = []
                    in_code_block = False
                    code_language = ''
                else:
                    # 开始代码块
                    if current_block:
                        blocks.append(TextBlock(
                            content='\n'.join(current_block),
                            block_type=current_type
                        ))
                    current_block = []
                    in_code_block = True
                    code_language = line[3:].strip()
                continue

            if in_code_block:
                current_block.append(line)
                continue

            # 标题
            if line.startswith('#'):
                if current_block:
                    blocks.append(TextBlock(
                        content='\n'.join(current_block),
                        block_type=current_type
                    ))
                level = len(line) - len(line.lstrip('#'))
                blocks.append(TextBlock(
                    content=line.lstrip('#').strip(),
                    block_type='heading',
                    level=level
                ))
                current_block = []
                current_type = 'paragraph'
                continue

            # 列表
            if re.match(r'^\s*[-*+]\s', line) or re.match(r'^\s*\d+\.\s', line):
                if current_block and current_type != 'list':
                    blocks.append(TextBlock(
                        content='\n'.join(current_block),
                        block_type=current_type
                    ))
                    current_block = []
                current_type = 'list'
                current_block.append(line)
                continue

            # 引用
            if line.startswith('>'):
                if current_block and current_type != 'quote':
                    blocks.append(TextBlock(
                        content='\n'.join(current_block),
                        block_type=current_type
                    ))
                    current_block = []
                current_type = 'quote'
                current_block.append(line.lstrip('>').strip())
                continue

            # 空行分隔
            if line.strip() == '':
                if current_block:
                    blocks.append(TextBlock(
                        content='\n'.join(current_block),
                        block_type=current_type
                    ))
                    current_block = []
                    current_type = 'paragraph'
                continue

            current_block.append(line)

        # 处理最后一块
        if current_block:
            blocks.append(TextBlock(
                content='\n'.join(current_block),
                block_type=current_type
            ))

        return blocks

    def _parse_text(self, content: str) -> List[TextBlock]:
        """解析纯文本"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return [TextBlock(content=p, block_type='paragraph') for p in paragraphs]

    def _parse_json(self, content: str) -> List[TextBlock]:
        """解析JSON文档"""
        try:
            data = json.loads(content)
            return [TextBlock(
                content=json.dumps(data, ensure_ascii=False, indent=2),
                block_type='code',
                metadata={'language': 'json'}
            )]
        except json.JSONDecodeError:
            return self._parse_text(content)

    def _parse_csv(self, content: str) -> List[TextBlock]:
        """解析CSV文档"""
        lines = content.strip().split('\n')
        if len(lines) > 0:
            return [TextBlock(
                content=content,
                block_type='table',
                metadata={'rows': len(lines), 'delimiter': ','}
            )]
        return []

    def _parse_html(self, content: str) -> List[TextBlock]:
        """解析HTML文档 - 简单标签去除"""
        # 移除script和style
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        # 移除标签
        text = re.sub(r'<[^>]+>', ' ', content)
        # 规范化空白
        text = re.sub(r'\s+', ' ', text).strip()
        return self._parse_text(text)

    def _parse_code(self, content: str, ext: str) -> List[TextBlock]:
        """解析代码文件"""
        language_map = {
            '.py': 'python', '.js': 'javascript', '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.go': 'go',
            '.rs': 'rust', '.ts': 'typescript', '.sh': 'bash',
            '.yaml': 'yaml', '.yml': 'yaml', '.xml': 'xml'
        }
        return [TextBlock(
            content=content,
            block_type='code',
            metadata={'language': language_map.get(ext, 'unknown')}
        )]


class TextAnalyzer:
    """文本分析器"""

    # 中文停用词
    CHINESE_STOPWORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也',
        '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
        '之', '与', '及', '等', '或', '但', '而', '因为', '所以', '如果', '虽然', '但是', '可以',
        '这个', '那个', '这些', '那些', '什么', '怎么', '为什么', '如何', '哪里', '谁', '多少',
        '为', '以', '于', '则', '乃', '即', '若', '且', '既', '因', '故', '所', '被', '把', '将',
        '对', '向', '从', '自', '由', '按', '照', '依', '据', '随', '同', '共', '给', '让', '叫',
        '使', '令', '得', '着', '过', '了', '来', '去', '起', '出', '入', '进', '退', '开', '关'
    }

    # 英文停用词
    ENGLISH_STOPWORDS = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
        'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
        'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'between', 'under', 'and', 'but', 'or', 'yet', 'so', 'if',
        'because', 'although', 'though', 'while', 'where', 'when', 'that',
        'which', 'who', 'whom', 'whose', 'what', 'this', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'mine',
        'yours', 'hers', 'ours', 'theirs', 'myself', 'yourself', 'himself',
        'herself', 'itself', 'ourselves', 'yourselves', 'themselves'
    }

    def __init__(self):
        self.stopwords = self.CHINESE_STOPWORDS | self.ENGLISH_STOPWORDS

    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(re.sub(r'\s', '', text))
        if total_chars == 0:
            return 'unknown'
        ratio = chinese_chars / total_chars
        if ratio > 0.3:
            return 'zh'
        elif ratio > 0.05:
            return 'mixed'
        else:
            return 'en'

    def extract_keywords(self, text: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """提取关键词"""
        language = self.detect_language(text)

        if language == 'zh':
            # 中文分词 - 基于规则
            words = self._chinese_tokenize(text)
        else:
            # 英文分词
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        # 过滤停用词和短词
        filtered = [w for w in words if len(w) > 1 and w.lower() not in self.stopwords]

        # 统计词频
        word_counts = Counter(filtered)
        total = sum(word_counts.values())

        # 计算TF分数
        keywords = [(word, count / total) for word, count in word_counts.most_common(top_k * 2)]

        # 简单过滤：去除纯数字
        keywords = [(w, s) for w, s in keywords if not w.isdigit()]

        return keywords[:top_k]

    def _chinese_tokenize(self, text: str) -> List[str]:
        """中文分词 - 基于字典和规则的简单实现"""
        # 移除标点
        text = re.sub(r'[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffefa-zA-Z0-9\s]', '', text)

        words = []
        i = 0
        while i < len(text):
            char = text[i]
            if '\u4e00' <= char <= '\u9fff':
                # 中文字符 - 尝试提取2-4字词组
                found = False
                for length in range(min(4, len(text) - i), 1, -1):
                    candidate = text[i:i + length]
                    if all('\u4e00' <= c <= '\u9fff' for c in candidate):
                        words.append(candidate)
                        i += length
                        found = True
                        break
                if not found:
                    words.append(char)
                    i += 1
            elif char.isalnum():
                # 英文数字
                j = i
                while j < len(text) and text[j].isalnum():
                    j += 1
                words.append(text[i:j].lower())
                i = j
            else:
                i += 1

        return words

    def extract_entities(self, text: str) -> List[ExtractedKnowledge]:
        """提取命名实体"""
        entities = []

        # 邮箱
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        for email in emails:
            entities.append(ExtractedKnowledge(
                knowledge_type='entity',
                content=email,
                confidence=1.0,
                source_blocks=[],
                metadata={'entity_type': 'email'}
            ))

        # URL
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
        for url in urls:
            entities.append(ExtractedKnowledge(
                knowledge_type='entity',
                content=url,
                confidence=1.0,
                source_blocks=[],
                metadata={'entity_type': 'url'}
            ))

        # IP地址
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
        for ip in ips:
            entities.append(ExtractedKnowledge(
                knowledge_type='entity',
                content=ip,
                confidence=0.9,
                source_blocks=[],
                metadata={'entity_type': 'ip_address'}
            ))

        # 版本号
        versions = re.findall(r'\bv?\d+\.\d+(?:\.\d+)?(?:[-.]?[a-zA-Z0-9]+)?\b', text)
        for version in versions:
            entities.append(ExtractedKnowledge(
                knowledge_type='entity',
                content=version,
                confidence=0.8,
                source_blocks=[],
                metadata={'entity_type': 'version'}
            ))

        return entities

    def generate_summary(self, text: str, max_sentences: int = 5) -> str:
        """生成文本摘要 - 基于句子重要性"""
        # 分句
        if self.detect_language(text) == 'zh':
            sentences = re.split(r'[。！？\n]+', text)
        else:
            sentences = re.split(r'[.!?\n]+', text)

        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if len(sentences) == 0:
            return text[:200] if text else ""

        if len(sentences) <= max_sentences:
            return ' '.join(sentences)

        # 计算句子重要性（基于关键词覆盖）
        keywords = dict(self.extract_keywords(text, top_k=30))
        sentence_scores = []

        for i, sentence in enumerate(sentences):
            words = sentence.lower().split() if self.detect_language(sentence) != 'zh' else self._chinese_tokenize(sentence)
            score = sum(keywords.get(word, 0) for word in words)
            # 位置权重 - 开头和结尾的句子更重要
            if i < 2:
                score *= 1.5
            elif i > len(sentences) - 3:
                score *= 1.3
            sentence_scores.append((i, score))

        # 选择得分最高的句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        selected = sorted([s[0] for s in sentence_scores[:max_sentences]])

        summary = ' '.join([sentences[i] for i in selected])
        return summary

    def analyze_sentiment(self, text: str) -> float:
        """情感分析 - 返回-1到1之间的分数"""
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'awesome', 'perfect', 'best', 'love', 'like', 'happy', 'positive',
            'success', 'easy', 'simple', 'fast', 'efficient', 'powerful',
            '好', '棒', '优秀', '出色', '完美', '喜欢', '爱', '快乐',
            '成功', '简单', '容易', '快速', '高效', '强大', '推荐'
        }

        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike',
            'difficult', 'hard', 'complex', 'slow', 'bug', 'error', 'fail',
            'problem', 'issue', 'wrong', 'broken', 'useless', 'poor',
            '坏', '差', '糟糕', '讨厌', '难', '复杂', '慢', '错误',
            '失败', '问题', 'bug', '无用', '垃圾'
        }

        words = text.lower().split() if self.detect_language(text) != 'zh' else self._chinese_tokenize(text)

        positive_count = sum(1 for w in words if w in positive_words)
        negative_count = sum(1 for w in words if w in negative_words)
        total = positive_count + negative_count

        if total == 0:
            return 0.0

        return (positive_count - negative_count) / total

    def calculate_readability(self, text: str) -> float:
        """计算可读性分数 (0-100)"""
        sentences = re.split(r'[.!?。！？]+', text)
        sentences = [s for s in sentences if s.strip()]

        if not sentences:
            return 50.0

        words = text.split()
        if not words:
            return 50.0

        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(w) for w in words) / len(words)

        # 简化版Flesch阅读分数
        score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_word_length
        return max(0, min(100, score))

    def extract_topics(self, text: str, top_k: int = 5) -> Dict[str, float]:
        """提取主题分布"""
        keywords = self.extract_keywords(text, top_k=top_k * 3)

        # 主题分类映射
        topic_keywords = {
            'technology': ['code', 'program', 'software', 'api', 'database', 'server', 'cloud',
                          '技术', '代码', '程序', '软件', '数据库', '服务器', '云'],
            'business': ['market', 'business', 'company', 'product', 'service', 'customer',
                        '市场', '商业', '公司', '产品', '服务', '客户'],
            'science': ['research', 'study', 'data', 'analysis', 'experiment', 'theory',
                       '研究', '数据', '分析', '实验', '理论'],
            'education': ['learn', 'course', 'tutorial', 'guide', 'education', 'student',
                         '学习', '教程', '指南', '教育', '学生'],
            'health': ['health', 'medical', 'doctor', 'patient', 'treatment',
                      '健康', '医疗', '医生', '病人', '治疗'],
            'finance': ['money', 'finance', 'invest', 'stock', 'price', 'economy',
                       '金融', '投资', '股票', '价格', '经济'],
        }

        topic_scores = {topic: 0.0 for topic in topic_keywords}
        for word, score in keywords:
            for topic, t_keywords in topic_keywords.items():
                if word.lower() in [tk.lower() for tk in t_keywords]:
                    topic_scores[topic] += score

        # 归一化
        total = sum(topic_scores.values())
        if total > 0:
            topic_scores = {k: v / total for k, v in topic_scores.items()}

        # 返回前K个主题
        sorted_topics = dict(sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:top_k])
        return sorted_topics


class KnowledgeExtractor:
    """知识提取器"""

    def __init__(self, analyzer: TextAnalyzer):
        self.analyzer = analyzer

    def extract_all(self, blocks: List[TextBlock]) -> List[ExtractedKnowledge]:
        """从文本块中提取所有知识"""
        knowledge = []

        # 合并所有文本
        full_text = '\n'.join([b.content for b in blocks])

        # 提取关键词
        keywords = self.analyzer.extract_keywords(full_text, top_k=20)
        for word, score in keywords:
            knowledge.append(ExtractedKnowledge(
                knowledge_type='keyword',
                content=word,
                confidence=score,
                source_blocks=[]
            ))

        # 提取实体
        entities = self.analyzer.extract_entities(full_text)
        knowledge.extend(entities)

        # 生成摘要
        summary = self.analyzer.generate_summary(full_text, max_sentences=5)
        knowledge.append(ExtractedKnowledge(
            knowledge_type='summary',
            content=summary,
            confidence=0.95,
            source_blocks=[]
        ))

        # 提取概念（基于标题）
        concepts = self._extract_concepts(blocks)
        knowledge.extend(concepts)

        return knowledge

    def _extract_concepts(self, blocks: List[TextBlock]) -> List[ExtractedKnowledge]:
        """从标题中提取概念"""
        concepts = []
        for i, block in enumerate(blocks):
            if block.block_type == 'heading':
                concepts.append(ExtractedKnowledge(
                    knowledge_type='concept',
                    content=block.content,
                    confidence=0.9 - (block.level * 0.1),
                    source_blocks=[i],
                    metadata={'level': block.level}
                ))
        return concepts

    def build_knowledge_graph(self, knowledge: List[ExtractedKnowledge]) -> Dict[str, Any]:
        """构建知识图谱"""
        nodes = []
        edges = []

        # 创建节点
        for i, k in enumerate(knowledge):
            nodes.append({
                'id': i,
                'type': k.knowledge_type,
                'content': k.content[:100],  # 限制长度
                'confidence': k.confidence
            })

        # 创建边（基于共现）
        for i in range(len(knowledge)):
            for j in range(i + 1, len(knowledge)):
                ki, kj = knowledge[i], knowledge[j]
                # 如果共享source_blocks则建立连接
                if ki.source_blocks and kj.source_blocks:
                    common = set(ki.source_blocks) & set(kj.source_blocks)
                    if common:
                        edges.append({
                            'source': i,
                            'target': j,
                            'weight': len(common)
                        })

        return {'nodes': nodes, 'edges': edges}


class DocuMindEngine:
    """DocuMind主引擎"""

    def __init__(self):
        self.parser = DocumentParser()
        self.analyzer = TextAnalyzer()
        self.extractor = KnowledgeExtractor(self.analyzer)

    def analyze(self, file_path: str) -> AnalysisReport:
        """分析文档"""
        # 解析文档
        doc_info, blocks = self.parser.parse(file_path)

        # 合并文本用于分析
        full_text = '\n'.join([b.content for b in blocks])

        # 提取知识
        knowledge = self.extractor.extract_all(blocks)

        # 统计分析
        block_types = Counter([b.block_type for b in blocks])
        heading_levels = Counter([b.level for b in blocks if b.block_type == 'heading'])

        statistics = {
            'block_count': len(blocks),
            'block_types': dict(block_types),
            'heading_levels': dict(heading_levels),
            'knowledge_count': len(knowledge),
            'knowledge_types': dict(Counter([k.knowledge_type for k in knowledge]))
        }

        # 可读性和情感
        readability = self.analyzer.calculate_readability(full_text)
        sentiment = self.analyzer.analyze_sentiment(full_text)

        # 主题
        topics = self.analyzer.extract_topics(full_text)

        # 语言
        language = self.analyzer.detect_language(full_text)

        return AnalysisReport(
            document_info=doc_info,
            text_blocks=blocks,
            knowledge_units=knowledge,
            statistics=statistics,
            readability_score=readability,
            sentiment_score=sentiment,
            topic_distribution=topics,
            language=language
        )

    def export_report(self, report: AnalysisReport, output_path: str, format: str = 'json'):
        """导出分析报告"""
        if format == 'json':
            data = {
                'document_info': asdict(report.document_info),
                'statistics': report.statistics,
                'readability_score': report.readability_score,
                'sentiment_score': report.sentiment_score,
                'topic_distribution': report.topic_distribution,
                'language': report.language,
                'text_blocks': [
                    {
                        'content': b.content[:500],  # 限制长度
                        'block_type': b.block_type,
                        'level': b.level,
                        'metadata': b.metadata
                    }
                    for b in report.text_blocks
                ],
                'knowledge_units': [
                    {
                        'knowledge_type': k.knowledge_type,
                        'content': k.content[:500],
                        'confidence': k.confidence,
                        'metadata': k.metadata
                    }
                    for k in report.knowledge_units
                ]
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        elif format == 'markdown':
            self._export_markdown(report, output_path)

        elif format == 'html':
            self._export_html(report, output_path)

    def _export_markdown(self, report: AnalysisReport, output_path: str):
        """导出Markdown报告"""
        lines = []
        lines.append(f"# 📊 DocuMind 分析报告")
        lines.append(f"")
        lines.append(f"## 📄 文档信息")
        lines.append(f"")
        lines.append(f"- **文件名**: {report.document_info.filename}")
        lines.append(f"- **文件类型**: {report.document_info.file_type}")
        lines.append(f"- **文件大小**: {report.document_info.file_size:,} bytes")
        lines.append(f"- **字符数**: {report.document_info.char_count:,}")
        lines.append(f"- **词数**: {report.document_info.word_count:,}")
        lines.append(f"- **行数**: {report.document_info.line_count:,}")
        lines.append(f"- **MD5**: `{report.document_info.md5_hash}`")
        lines.append(f"")
        lines.append(f"## 📈 统计概览")
        lines.append(f"")
        lines.append(f"- **文本块数**: {report.statistics['block_count']}")
        lines.append(f"- **知识单元数**: {report.statistics['knowledge_count']}")
        lines.append(f"")
        lines.append(f"### 块类型分布")
        for btype, count in report.statistics['block_types'].items():
            lines.append(f"- {btype}: {count}")
        lines.append(f"")
        lines.append(f"## 🎯 可读性与情感")
        lines.append(f"")
        lines.append(f"- **可读性分数**: {report.readability_score:.2f}/100")
        lines.append(f"- **情感分数**: {report.sentiment_score:.3f} (-1=负面, 0=中性, 1=正面)")
        lines.append(f"")
        lines.append(f"## 🏷️ 主题分布")
        lines.append(f"")
        for topic, score in report.topic_distribution.items():
            bar = '█' * int(score * 20)
            lines.append(f"- {topic}: {score:.2%} {bar}")
        lines.append(f"")
        lines.append(f"## 🧠 提取的知识")
        lines.append(f"")

        for k in report.knowledge_units:
            if k.knowledge_type == 'summary':
                lines.append(f"### 📝 摘要")
                lines.append(f"> {k.content}")
                lines.append(f"")
            elif k.knowledge_type == 'keyword':
                if 'keywords' not in [l for l in lines[-5:]]:
                    lines.append(f"### 🔑 关键词")
                lines.append(f"- {k.content} (置信度: {k.confidence:.3f})")
            elif k.knowledge_type == 'entity':
                if 'entities' not in [l for l in lines[-5:]]:
                    lines.append(f"### 📌 实体")
                entity_type = k.metadata.get('entity_type', 'unknown')
                lines.append(f"- [{entity_type}] {k.content}")
            elif k.knowledge_type == 'concept':
                if 'concepts' not in [l for l in lines[-5:]]:
                    lines.append(f"### 💡 概念")
                level = k.metadata.get('level', 0)
                indent = '  ' * level
                lines.append(f"{indent}- {k.content}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _export_html(self, report: AnalysisReport, output_path: str):
        """导出HTML报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuMind 分析报告 - {report.document_info.filename}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        h1 {{ color: #2563eb; margin-bottom: 10px; }}
        h2 {{ color: #374151; margin: 30px 0 15px; padding-bottom: 10px; border-bottom: 2px solid #e5e7eb; }}
        h3 {{ color: #4b5563; margin: 20px 0 10px; }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .info-card {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
        }}
        .info-card label {{ display: block; color: #6b7280; font-size: 12px; text-transform: uppercase; }}
        .info-card value {{ display: block; font-size: 18px; font-weight: 600; color: #1f2937; margin-top: 5px; }}
        .score-bar {{
            background: #e5e7eb;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #2563eb, #3b82f6);
            border-radius: 10px;
            transition: width 0.3s;
        }}
        .keyword-tag {{
            display: inline-block;
            background: #dbeafe;
            color: #1e40af;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            margin: 5px;
        }}
        .entity-tag {{
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            margin: 5px;
        }}
        .summary-box {{
            background: #f0fdf4;
            border-left: 4px solid #22c55e;
            padding: 20px;
            border-radius: 8px;
            font-style: italic;
            margin: 20px 0;
        }}
        .topic-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}
        .topic-bar {{
            flex: 1;
            height: 24px;
            background: #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            margin: 0 10px;
        }}
        .topic-fill {{
            height: 100%;
            background: linear-gradient(90deg, #8b5cf6, #a78bfa);
            border-radius: 12px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #9ca3af;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 DocuMind 分析报告</h1>
        <p style="color: #6b7280;">生成时间: 2026-06-05</p>

        <h2>📄 文档信息</h2>
        <div class="info-grid">
            <div class="info-card">
                <label>文件名</label>
                <value>{report.document_info.filename}</value>
            </div>
            <div class="info-card">
                <label>文件类型</label>
                <value>{report.document_info.file_type}</value>
            </div>
            <div class="info-card">
                <label>文件大小</label>
                <value>{report.document_info.file_size:,} bytes</value>
            </div>
            <div class="info-card">
                <label>字符数</label>
                <value>{report.document_info.char_count:,}</value>
            </div>
            <div class="info-card">
                <label>词数</label>
                <value>{report.document_info.word_count:,}</value>
            </div>
            <div class="info-card">
                <label>语言</label>
                <value>{report.language}</value>
            </div>
        </div>

        <h2>📈 质量评分</h2>
        <div style="margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>可读性</span>
                <span>{report.readability_score:.1f}/100</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {report.readability_score}%"></div>
            </div>
        </div>
        <div style="margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>情感倾向</span>
                <span>{report.sentiment_score:+.3f} ({'正面' if report.sentiment_score > 0.1 else '负面' if report.sentiment_score < -0.1 else '中性'})</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {(report.sentiment_score + 1) * 50}%; background: {'#22c55e' if report.sentiment_score > 0.1 else '#ef4444' if report.sentiment_score < -0.1 else '#6b7280'}"></div>
            </div>
        </div>

        <h2>🏷️ 主题分布</h2>
"""
        for topic, score in report.topic_distribution.items():
            html += f"""
        <div class="topic-item">
            <span style="width: 100px;">{topic}</span>
            <div class="topic-bar">
                <div class="topic-fill" style="width: {score * 100}%"></div>
            </div>
            <span style="width: 60px; text-align: right;">{score:.1%}</span>
        </div>
"""

        html += "<h2>🧠 提取的知识</h2>"

        # 摘要
        summary = next((k for k in report.knowledge_units if k.knowledge_type == 'summary'), None)
        if summary:
            html += f'<div class="summary-box">{summary.content}</div>'

        # 关键词
        keywords = [k for k in report.knowledge_units if k.knowledge_type == 'keyword']
        if keywords:
            html += '<h3>🔑 关键词</h3><div>'
            for k in keywords[:15]:
                html += f'<span class="keyword-tag">{k.content}</span>'
            html += '</div>'

        # 实体
        entities = [k for k in report.knowledge_units if k.knowledge_type == 'entity']
        if entities:
            html += '<h3>📌 实体</h3><div>'
            for k in entities[:10]:
                entity_type = k.metadata.get('entity_type', 'unknown')
                html += f'<span class="entity-tag">[{entity_type}] {k.content}</span>'
            html += '</div>'

        html += """
        <div class="footer">
            <p>Powered by DocuMind-CLI v1.0.0 | 本地文档智能分析引擎</p>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
