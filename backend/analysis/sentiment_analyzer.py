"""
情感分析模块
支持 SnowNLP 和 BERT 两种算法
"""
from snownlp import SnowNLP


class SentimentAnalyzer:
    """情感分析器"""

    @staticmethod
    def snownlp_analyze(text):
        """基于 SnowNLP 的情感分析"""
        try:
            s = SnowNLP(text)
            score = s.sentiments  # 0-1, 越接近1越正面
            return {
                'score': score,
                'label': SentimentAnalyzer._score_to_label(score),
                'algorithm': 'snownlp',
            }
        except Exception:
            return {'score': 0.5, 'label': 'neutral', 'algorithm': 'snownlp'}

    @staticmethod
    def bert_analyze(text):
        """
        基于 BERT 的情感分析
        需要安装 transformers 和 torch
        此处提供简化版本，使用 SnowNLP 作为后备
        """
        try:
            from transformers import pipeline
            classifier = pipeline(
                'sentiment-analysis',
                model='uer/roberta-base-finetuned-jd-binary-chinese',
                tokenizer='uer/roberta-base-finetuned-jd-binary-chinese',
            )
            result = classifier(text[:512])[0]
            score = result['score'] if result['label'] == 'positive' else 1 - result['score']
            return {
                'score': score,
                'label': SentimentAnalyzer._score_to_label(score),
                'algorithm': 'bert',
            }
        except ImportError:
            return SentimentAnalyzer.snownlp_analyze(text)

    @staticmethod
    def analyze(text, algorithm='snownlp'):
        if algorithm == 'bert':
            return SentimentAnalyzer.bert_analyze(text)
        return SentimentAnalyzer.snownlp_analyze(text)

    @staticmethod
    def batch_analyze(texts, algorithm='snownlp'):
        return [SentimentAnalyzer.analyze(t, algorithm) for t in texts]

    @staticmethod
    def _score_to_label(score):
        if score >= 0.6:
            return 'positive'
        elif score <= 0.4:
            return 'negative'
        return 'neutral'
