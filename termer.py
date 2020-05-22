# coding=utf-8
# authour: wang xi

"""Termer for a sentence."""
DUMP_DIR = '__PKL__'

from typing import List, Sequence
import pickle
import string
import re
import os

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords

if not os.path.exists(DUMP_DIR):
    os.mkdir(DUMP_DIR)

class Termer(object):
    """Termer for a sentence. It includes three phases, 
    tokenization, transformation to a term and adding it to
    the dictionary.

    The whole process generally includes
    removing stop words, stemming or lemmatization.

    A new term will be inserted into term2id_dict.

    Attributes:
        include_stopword: include stopwords or not
        stemmer: used to stem the tokens
        term2id_dict: store the term dictionary, mapping from str -> int
        id2term_dict: mapping from int -> str
        g_term_max_id: currently allocated max term id 
    """

    def __init__(self, include_stopword: bool,
                 stem_type: str = "PorterStemmer"):
        """
        Args:
            stem_type: PorterStemmer, Lemmatizer
        """
        self.include_stopword = include_stopword
        nltk.data.path.append(os.path.join('resources','nltk_data'))

        if stem_type == "PorterStemmer":
            self.stemmer = PorterStemmer().stem
        elif stem_type == "Lemmatizer":
            self.stemmer = WordNetLemmatizer().lemmatize
        self.term2id_dict = dict()
        self.id2term_dict = dict()
        self.g_term_max_id = 0
        self.punctuations = '[0-9’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'

    def to_terms(self, sentence: str) -> List[int]:
        """Transform a sentence into a list of terms and add
        it to the dictionary if a term is not in the dictionary.
        
        Args:
            sentence: original string to be processed
        
        Returns:
            a list of term ids
        """
        tokens = self._tokenize(re.sub(self.punctuations, '', sentence))
        ret = self._tokens_to_terms(tokens)
        return ret
    
    def serialize_dictionary(self, dic_dir: str ,terms_id: str, id_terms: str, xml_file_name = 'test'):
        """Serialize the dictionary to files.
        
        Args:
            terms_id: file name for terms to term ids mapping
            id_terms: file name for term ids to terms mapping
        """
        if not os.path.exists(dic_dir):
            os.mkdir(dic_dir)
        with open(os.path.join(dic_dir,xml_file_name+'_'+terms_id), 'wb') as f:
            pickle.dump(self.term2id_dict, f)
        with open(os.path.join(dic_dir,xml_file_name+'_'+id_terms), 'wb') as f:
            pickle.dump(self.id2term_dict, f)

    def _tokenize(self, sentence: str) -> List[str]:
        """ Transform a sentence into a list of tokens.
        Stop words are removed in this phase.

        Args:
            sentence: original string to be cut
        
        Returns:
            a list of term string
        """        
        tokens = word_tokenize(sentence)
        tokens = [t for t in tokens if t not in self.punctuations]
        
        if self.include_stopword == True:
            return tokens
        stop_words = set(stopwords.words('english'))
        res = []
        for t in tokens:
            if t in stop_words:
                continue
            res.append(t)
        return res

    def _tokens_to_terms(self, tokens: Sequence[str]) -> List[int]:
        """Transform tokens into term ids. 
        """
        ret = []
        for t in tokens:
            term = self.stemmer(t)
            if term in self.term2id_dict:
                ret.append(self.term2id_dict[term])
            else:
                self.term2id_dict[term] = self.g_term_max_id
                self.id2term_dict[self.g_term_max_id] = term
                ret.append(self.g_term_max_id)
                self.g_term_max_id += 1
        return ret
    
    def get_number_of_terms(self):
        return len(self.term2id_dict)



if __name__ == "__main__":
    sentence = " This is good. \n\n ??  '''' | Today is raining."
    s2 = "This is not so good. do you think so?"
    termer = Termer(False)
    term_ids = termer.to_terms(sentence)
    term_ids2 = termer.to_terms(s2)
    print(term_ids2)
    print(term_ids)
    print(termer.term2id_dict)
    print(termer.id2term_dict)
    dict_path = os.path.join(DUMP_DIR,'dictionary')
    termer.serialize_dictionary(dict_path,"term2id.pkl","id2term.pkl")