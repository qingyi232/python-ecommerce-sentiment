import re
import jieba
import jieba.analyse


STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
    '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
    '着', '没有', '看', '好', '自己', '这', '他', '她', '它', '我们',
    '你们', '他们', '那', '这个', '那个', '什么', '怎么', '哪', '哪个',
    '吧', '吗', '呢', '啊', '呀', '哦', '嗯', '哈', '啦', '嘛', '喔',
    '但是', '但', '然后', '所以', '因为', '如果', '虽然', '而且', '还是',
    '或者', '可以', '可能', '应该', '已经', '这样', '那样', '之后', '以后',
    '之前', '以前', '非常', '比较', '特别', '真的', '确实', '一直', '还',
    '又', '再', '更', '最', '越', '太', '挺', '蛮', '相当', '十分',
])


class TextProcessor:

    @staticmethod
    def clean_text(text):
        if not text or not isinstance(text, str):
            return ''
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？、；：""''（）]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def segment(text, remove_stopwords=True):
        if not text:
            return []
        words = jieba.lcut(text)
        if remove_stopwords:
            words = [w for w in words if w.strip() and len(w) > 1 and w not in STOP_WORDS]
        return words

    @staticmethod
    def extract_keywords(text, topK=20):
        if not text:
            return []
        keywords = jieba.analyse.extract_tags(text, topK=topK, withWeight=True)
        return [{'word': w, 'weight': round(s, 4)} for w, s in keywords]

    @staticmethod
    def batch_clean(texts):
        return [TextProcessor.clean_text(t) for t in texts]

    @staticmethod
    def batch_segment(texts, remove_stopwords=True):
        return [TextProcessor.segment(t, remove_stopwords) for t in texts]
