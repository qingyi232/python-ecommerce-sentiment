"""
需求挖掘模块
基于 LDA 主题模型进行用户需求分析
"""
import jieba
from gensim import corpora, models
from collections import Counter


class DemandMiner:
    """需求挖掘器"""

    STOP_WORDS = set([
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
        '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
        '着', '没有', '看', '好', '自己', '这', '他', '她', '我们', '你们',
        '那', '这个', '什么', '怎么', '吧', '吗', '呢', '啊', '呀', '嗯',
        '但是', '但', '然后', '所以', '因为', '如果', '虽然', '而且', '还是',
        '可以', '可能', '应该', '已经', '这样', '非常', '比较', '特别', '真的',
        '确实', '一直', '还', '又', '再', '更', '最', '越', '太', '挺',
    ])

    def __init__(self, num_topics=5, passes=15):
        self.num_topics = num_topics
        self.passes = passes

    def preprocess(self, texts):
        """文本预处理：分词 + 去停用词"""
        processed = []
        for text in texts:
            words = jieba.lcut(text)
            words = [w for w in words if len(w) > 1 and w not in self.STOP_WORDS]
            if len(words) >= 2:
                processed.append(words)
        return processed

    def extract_topics(self, texts):
        """提取主题"""
        processed = self.preprocess(texts)
        if len(processed) < 3:
            return {'topics': [], 'keywords': []}

        dictionary = corpora.Dictionary(processed)
        dictionary.filter_extremes(no_below=2, no_above=0.8)
        corpus = [dictionary.doc2bow(doc) for doc in processed]

        if not corpus or len(dictionary) < 3:
            return {'topics': [], 'keywords': []}

        num_topics = min(self.num_topics, len(dictionary), len(processed))
        lda = models.LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            passes=self.passes,
            random_state=42,
            alpha='auto',
            eta='auto',
        )

        topics = []
        for i in range(num_topics):
            terms = lda.show_topic(i, topn=10)
            topics.append({
                'topic_id': i,
                'words': [w for w, _ in terms],
                'weights': [float(p) for _, p in terms],
            })

        all_words = Counter()
        for doc in processed:
            all_words.update(doc)

        return {
            'topics': topics,
            'keywords': [{'word': w, 'count': c} for w, c in all_words.most_common(50)],
        }

    def get_document_topics(self, texts, lda_model=None, dictionary=None):
        """获取每个文档的主题分布"""
        processed = self.preprocess(texts)
        if not dictionary or not lda_model:
            return []

        result = []
        for doc in processed:
            bow = dictionary.doc2bow(doc)
            topics = lda_model.get_document_topics(bow)
            result.append(topics)
        return result
