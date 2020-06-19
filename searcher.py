# coding=utf-8
# author: wang xi

"""Search for a query using different scoring methods. Return top 10 documents."""


from typing import List, Sequence
import math
import queue
from functools import reduce
import re

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

import numpy as np

from posting import Posting_handler
from scorer import Scorer

class Searcher(object):
    """Searcher is used to search for a given query and return the top 10 results.

    Attributes:
        scorer: an object that contains many scoring methods
        total_docs: number of documents in total
    """

    def __init__(self, ph: Posting_handler):
        """
        Args:
            ph: a posting handler
        """
        self.scorer = Scorer(ph)
        self.total_docs = ph.num_doc
        self.ph = ph
        self.pattern = re.compile(r"^[a-zA-Z][a-zA-Z']+$")
        

    def search(self, query: str, method: str = "tf-idf", top_k: int = 10) -> List[int]:
        """Search the documents for the given query.

        Args:
            query: query string
            method: different methods are supported,
                jaccard : Jaccard coefficient
                log_freq : Log frequency weighting
                tf-idf : TF-IDF
                cosine_similarity : Cosine similarity
                bm25 : BM25
            top_k: number of documents returned

        Returns:
            a list of returned documents' id with top k scores
        """
        score_fn = None
        if method == "jaccard":
            score_fn = self.scorer.jaccard_score
        elif method == "log_freq":
            score_fn = self.scorer.log_frequency_score
        elif method == "tf-idf":
            score_fn = self.scorer.tf_idf_score
        elif method == "cosine_similarity":
            score_fn = self.scorer.cosine_similarity_score
        elif method == "bm25":
            score_fn = self.scorer.bm25_score
        else:
            print("Wrong method parameter.")
            return []
        query_ = self._process_query(query)
        docs = self._get_matched_docs(query_)
        print(docs)

        q = queue.PriorityQueue()
        for i, doc_id in enumerate(docs):

            s = score_fn(query_, doc_id)
            # print("score: ", s, " doc id: ",doc_id)
            if i >= top_k:
                q.get()
            q.put((s, doc_id))

        res = []
        while not q.empty():
            res.append(q.get()[1])
        res.reverse()
        return res

    def _process_query(self, query: str) -> List[int]:
        """Process query. Remove stop words and transform
        the tokens into appropriate term ids.

        Args:
            query: query string
        
        Returns:
            a list of terms' id for the query string
        """
        tokens = word_tokenize(query)
        tokens = [t.lower() for t in tokens if len(t) < 25 and self.pattern.match(t)]
        

        stop_words = set(stopwords.words('english'))
        query = []
        stemmer = PorterStemmer()
        for t in tokens:
            t_stem = stemmer.stem(t)
            if t_stem in stop_words:
                continue
            query.append(self.ph.get_id_by_term(t_stem))
        print("query:", query)
        return query


    def _get_matched_docs(self, query: List[int]) -> List[int]:
        """Return matched docs' id according to the query.
        """
        #res = []
        
        postings = []
        for q in query:
            #print('\033[0;34mThe term whose id is %d:\033[0m\n%s' % (q, self.ph.get_term_by_id(q)))
            #print(self.ph.posting_list(q))
            postings.append(self.ph.posting_list(q))
        #res = reduce(np.intersect1d, postings)
        res = reduce(np.union1d, postings)
        """
        for d in range(self.total_docs):
            is_matched = True
            for q in query:
                if self.ph.tf(d, q) == 0:
                    is_matched = False
                    break
            if is_matched == True:
                res.append(d)
        """
        return res


if __name__ == "__main__":
    from posting import Posting_handler

    ph = Posting_handler('pages_sample.xml')
    print('-------------------------------------------------')

    query = "boys and girls"
    searcher = Searcher(ph)
    print(searcher.search(query))



