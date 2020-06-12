# coding=utf-8
# authour: wang xi

"""Determine a score for a doc-query pair."""


from typing import List, Sequence
import math

from posting import Posting_handler

class Scorer(object):
    """Scorer is used to assign a score to a doc and a given query.

    Many different scoring methods are supported. They are the
    variants of TF-IDF.

    1. Jaccard coefficient
    2. Log frequency weighting
    3. TF-IDF
    4. Cosine similarity
    5. BM25

    Attributes:
        ph: posting handler, from which we can get term-frequency, idf, etc... 
    """

    def __init__(self, ph: Posting_handler):
        """
        Args:
            ph: a posting handler
        """
        self.ph = ph
        

    def jaccard_score(self, query: List[int], doc_id: int) -> float:
        """Jaccard coefficient(q, d) = |q intersect d| / sqrt(|q union d|)
        We use Jaccard score with length normalization.

        Args:
            query: terms' id of a query
            doc_id: document id
        
        Returns:
            the Jaccard score of the given query and doc id
        """
        intersection = 0
        union = self.ph.dl(doc_id)
        for term_id in query:
            intersection += (self.ph.tf(doc_id, term_id) > 0)
        return intersection / math.sqrt(union)
        

    def log_frequency_score(self, query: List[int], doc_id: int) -> float:
        """Log frequency weighting is a variant of tf-idf. It uses only the
        log term frequency as the score.
        
        log frequency score = sum{ 1 + log(1 + tf(t, d)) | t in query }

        Args:
            query: terms' id of a query
            doc_id: document id
        
        Returns:
            log frequency score of the given query and doc id
        """
        score = 0.0
        for term_id in query:
            score += 1+ math.log(1 + self.ph.tf(doc_id, term_id))
        return score

    def tf_idf_score(self, query: List[int], doc_id: int) -> float:
        """TF-IDF score. There are many kinds of weighting schemes.
        Here, we use log term frequency, i.e. LTN.
        
        tf-idf score = sum{ (1 + log(1 + tf(t, d))) * log(N/df(t)) | t in query }

        Args:
            query: terms' id of a query
            doc_id: document id
        
        Returns:
            log frequency score of the given query and doc id
        """
        score = 0.0
        for term_id in query:
            tf = 1 + math.log(1 + self.ph.tf(doc_id, term_id))
            idf = math.log(self.ph.idf(term_id))
            score += (tf * idf)
        return score

    def cosine_similarity_score(self, query: List[int], doc_id: int) -> float:
        """Cosine similarity of query and a doc. For vector representation
        of doc and query, we use tf-idf. As for the weighting scheme, we use lnc.ltc.
        
        For document weighting: 1 + log(1 + tf(t, d)), normalized by doc length
        For query weighting: (1 + log(tf(t, q))) * log(N/df(t))

        Args:
            query: terms' id of a query
            doc_id: document id
        
        Returns:
            cosine similarity score of the given query and doc id
        """
        score = 0.0
        for term_id in query:
            d_wt = 1 + math.log(1 + self.ph.tf(doc_id, term_id))
            d_wt /= self.ph.dl(doc_id)

            q_wt = math.log(self.ph.idf(term_id))
            score += d_wt * q_wt
        return score

    def bm25_score(self, query: List[int], doc_id: int) -> float:
        """BM25 score. It is another variant of tf-idf.
        
        The only difference is that BM25 replaces tf with R(t, d).

        R(t, d) = tf(t, d) * (k1 + 1) / (tf(t, d) + K)

        K = k1 * (1 - b + b * len(d) / avg(doc len))

        We use k1 = 2, b = 0.75

        Args:
            query: terms' id of a query
            doc_id: document id
        
        Returns:
            BM25 score of the given query and doc id
        """
        score = 0.0
        k1, b = 2.0, 0.75
        for term_id in query:
            tf = self.ph.tf(doc_id, term_id)
            K = k1 * (1 - b + b * self.ph.dl(doc_id) / self.ph.avgdl)
            R = tf * (k1 + 1) / (tf + K)

            idf = self.ph.idf(doc_id)
            score += R * idf
        return score



if __name__ == "__main__":
    from posting import Posting_handler

    ph = Posting_handler('pages_sample.xml')
    print('-------------------------------------------------')

    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer
    from nltk.corpus import stopwords

    query = "Political"
    tokens = word_tokenize(query)
    print(tokens)
    punctuations = '[0-9’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
    tokens = [t for t in tokens if t not in punctuations]

    stop_words = set(stopwords.words('english'))
    query = []
    
    stemmer = PorterStemmer()
    for t in tokens:
        t_stem = stemmer.stem(t)
        if t_stem in stop_words:
            continue
        query.append(ph.get_id_by_term(t_stem))
    print(query)
    
    doc_id = 0
    print('tf: %d' % ph.tf(doc_id, query[0]))
    print('idf: %f' % ph.idf(query[0]))

    scorer = Scorer(ph)
    print("Jaccard score: %f" % scorer.jaccard_score(query, doc_id))
    print("Log freq score: %f" % scorer.log_frequency_score(query, doc_id))
    print("TF-IDF score: %f" % scorer.tf_idf_score(query, doc_id))
    print("Cosine similarity score: %f" % scorer.cosine_similarity_score(query, doc_id))
    print("BM25 score: %f" % scorer.bm25_score(query, doc_id))



