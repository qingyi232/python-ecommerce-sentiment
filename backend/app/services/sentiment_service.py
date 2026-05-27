import json
from collections import Counter
from snownlp import SnowNLP
from app import db
from app.models.review import Review
from app.models.product import Product
from app.models.sentiment import SentimentResult
from app.services.text_processor import TextProcessor


class SentimentService:

    @staticmethod
    def analyze(product_id, reviews, algorithm='snownlp'):
        positive_words = Counter()
        negative_words = Counter()
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_score = 0.0

        for review in reviews:
            cleaned = TextProcessor.clean_text(review.content)
            if not cleaned:
                continue

            review.cleaned_content = cleaned

            if algorithm == 'bert':
                score = SentimentService._bert_score(cleaned)
            else:
                score = SentimentService._snownlp_score(cleaned)

            review.sentiment_score = score
            review.is_analyzed = True
            total_score += score

            words = TextProcessor.segment(cleaned)

            if score >= 0.6:
                review.sentiment_label = 'positive'
                positive_count += 1
                positive_words.update(words)
            elif score <= 0.4:
                review.sentiment_label = 'negative'
                negative_count += 1
                negative_words.update(words)
            else:
                review.sentiment_label = 'neutral'
                neutral_count += 1

            kw = TextProcessor.extract_keywords(cleaned, topK=5)
            review.keywords = json.dumps([k['word'] for k in kw], ensure_ascii=False)

        total = len(reviews)
        avg = total_score / total if total > 0 else 0

        SentimentResult.query.filter_by(product_id=product_id, algorithm=algorithm).delete()

        result = SentimentResult(
            product_id=product_id,
            total_reviews=total,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            avg_score=avg,
            positive_ratio=round(positive_count / total * 100, 1) if total else 0,
            negative_ratio=round(negative_count / total * 100, 1) if total else 0,
            neutral_ratio=round(neutral_count / total * 100, 1) if total else 0,
            top_positive_words=json.dumps(
                [w for w, _ in positive_words.most_common(20)], ensure_ascii=False
            ),
            top_negative_words=json.dumps(
                [w for w, _ in negative_words.most_common(20)], ensure_ascii=False
            ),
            algorithm=algorithm,
        )

        db.session.add(result)

        product = Product.query.get(product_id)
        if product:
            product.avg_sentiment = avg

        db.session.commit()

        return result.to_dict()

    @staticmethod
    def _snownlp_score(text):
        try:
            s = SnowNLP(text)
            return s.sentiments
        except Exception:
            return 0.5

    @staticmethod
    def _bert_score(text):
        try:
            if not hasattr(SentimentService, '_bert_pipeline'):
                SentimentService._bert_pipeline = SentimentService._load_bert()
            if SentimentService._bert_pipeline is None:
                return SentimentService._snownlp_score(text)
            result = SentimentService._bert_pipeline(text[:512])
            label = result[0]['label']
            conf = result[0]['score']
            if label == 'positive':
                return 0.5 + conf * 0.5
            else:
                return 0.5 - conf * 0.5
        except Exception:
            return SentimentService._snownlp_score(text)

    @staticmethod
    def _load_bert():
        try:
            import os
            os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
            from transformers import pipeline
            model_name = 'uer/roberta-base-finetuned-jd-binary-chinese'
            return pipeline('sentiment-analysis', model=model_name, device=-1)
        except Exception as e:
            print(f'BERT model unavailable, falling back to SnowNLP: {e}')
            return None
