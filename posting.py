DUMP_DIR = '__PKL__'
TF_LIST_FILENAME_POST_FREFIX = '_tf.pkl'
DF_LIST_FILENAME_POST_FREFIX = '_df.npy'
DL_LIST_FILENAME_POST_FREFIX = '_dl.npy'
LINK_LIST_FILENAME_POST_FREFIX = '_link.pkl'

from wiki_xml_handler import wiki_xmlhandler
from termer import Termer

import numpy as np
import os
import pickle

if not os.path.exists(DUMP_DIR):
    os.mkdir(DUMP_DIR)

class Posting_handler(object):
    def __init__(self,xml_file_name):
        self.file_name = xml_file_name.replace('.xml','')
        self.xml_handler = wiki_xmlhandler(xml_file_name)
        self.termer = Termer(False)
        self.num_doc = len(self.xml_handler.doc_list)
        self.tf_list = self.get_tf_list() # list of dicts
        self.df_list = self.get_df_list() # np.array
        self.dl_list = self.get_dl_list() # np.array
        self.link_list = self.get_link_list() # list of sets
        self.avgdl = self.get_avgdl()

    def tf(self,doc_id,term_id):
        doc_tf = self.tf_list[doc_id]
        if term_id in doc_tf.keys():
            return doc_tf[term_id]
        else:
            return 0
    
    def df(self,term_id):
        return self.df_list[term_id]

    def idf(self,term_id):
        ############# NOT SURE ##############
        # total number of docs / number of docs that contain the term
        return self.num_doc / self.df(term_id)

    def dl(self,doc_id):
        return self.dl_list[doc_id]

    def link_set(self,doc_id):
        return self.link_list[doc_id]

    def get_term_list_and_link_set(self,id_or_title):
        doc_dict = self.xml_handler.get_plain_wiki_text_and_link(id_or_title)
        plain_wiki_text = doc_dict['text']
        link_set = doc_dict['link_set']
        print(plain_wiki_text)
        term_id_list=self.termer.to_terms(plain_wiki_text)
        return term_id_list,link_set

    def get_tf_list(self):
        tf_file_name = os.path.join(DUMP_DIR,self.file_name+TF_LIST_FILENAME_POST_FREFIX)
        if not os.path.exists(tf_file_name):
            return self.gen_tf_list()
        else:
            f = open(tf_file_name,'rb')
            tf_list = pickle.load(f)
            f.close()
            return tf_list

    def gen_tf_list(self):
        '''generate the tf list for the xml'''
        pass

    def get_df_list(self):
        df_file_name = os.path.join(DUMP_DIR,self.file_name+DF_LIST_FILENAME_POST_FREFIX)
        if not os.path.exists(df_file_name):
            return self.gen_df_list()
        else:
            return np.load(df_file_name)
        
    def gen_df_list(self):
        '''generate the df list for the xml'''
        pass

    def get_dl_list(self):
        dl_file_name = os.path.join(DUMP_DIR,self.file_name+DL_LIST_FILENAME_POST_FREFIX)
        if not os.path.exists(dl_file_name):
            return self.gen_dl_list()
        else:
            return np.load(dl_file_name)
        
    def gen_dl_list(self):
        '''generate the dl list for the xml'''
        pass

    def get_avgdl(self):
        return self.dl_list.mean()

    def get_link_list(self):
        link_file_name = os.path.join(DUMP_DIR,self.file_name+LINK_LIST_FILENAME_POST_FREFIX)
        if not os.path.exists(link_file_name):
            return self.gen_link_list()
        else:
            f = open(link_file_name,'rb')
            link_list = pickle.load(f)
            f.close()
            return link_list

    def gen_link_list(self):
        '''generate the link list for the xml'''
        pass

    def gen_all(self):
        '''generate the tf_list, df_list, dl_list and link_list for the xml'''
        pass

if __name__ == '__main__':
    # main_wiki_xmlhandler = wiki_xmlhandler()
    ph = Posting_handler('pages_sample.xml')
    print(ph.get_term_list_and_link_set('Aristotle'))