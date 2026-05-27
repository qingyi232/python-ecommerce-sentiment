import json
from collections import Counter
from gensim import corpora, models
from app import db
from app.models.demand import DemandTopic, DemandKeyword
from app.services.text_processor import TextProcessor


TOPIC_LABELS = {
    0: '产品质量',
    1: '物流配送',
    2: '售后服务',
    3: '价格优惠',
    4: '外观设计',
    5: '使用体验',
    6: '包装品质',
    7: '功能特性',
}


class DemandService:

    @staticmethod
    def analyze(product_id, reviews, num_topics=5):
        DemandTopic.query.filter_by(product_id=product_id).delete()
        DemandKeyword.query.filter_by(product_id=product_id).delete()

        texts = []
        all_words = Counter()

        for review in reviews:
            cleaned = TextProcessor.clean_text(review.content)
            if not cleaned:
                continue
            words = TextProcessor.segment(cleaned)
            if len(words) >= 2:
                texts.append(words)
                all_words.update(words)

        if len(texts) < 3:
            db.session.commit()
            return {'topics': [], 'keywords': []}

        dictionary = corpora.Dictionary(texts)
        dictionary.filter_extremes(no_below=2, no_above=0.8)
        corpus = [dictionary.doc2bow(text) for text in texts]

        if not corpus or len(dictionary) < 3:
            db.session.commit()
            return {'topics': [], 'keywords': []}

        num_topics = min(num_topics, len(dictionary), len(texts))
        lda_model = models.LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            passes=15,
            random_state=42,
            alpha='auto',
            eta='auto',
        )

        topics_data = []
        for topic_id in range(num_topics):
            topic_terms = lda_model.show_topic(topic_id, topn=10)
            topic_words = [word for word, _ in topic_terms]
            weight = sum(prob for _, prob in topic_terms)

            label = TOPIC_LABELS.get(topic_id, f'主题{topic_id + 1}')

            topic = DemandTopic(
                product_id=product_id,
                topic_id=topic_id,
                topic_name=label,
                topic_words=json.dumps(topic_words, ensure_ascii=False),
                weight=weight,
                review_count=sum(1 for doc in corpus if any(
                    tid == topic_id for tid, _ in lda_model.get_document_topics(doc, minimum_probability=0.3)
                )),
            )
            db.session.add(topic)
            topics_data.append(topic)

        for word, freq in all_words.most_common(50):
            kw = DemandKeyword(
                product_id=product_id,
                keyword=word,
                frequency=freq,
            )
            db.session.add(kw)

        db.session.commit()

        return {
            'topics': [t.to_dict() for t in topics_data],
            'keywords': [{'keyword': w, 'frequency': f} for w, f in all_words.most_common(50)],
        }
