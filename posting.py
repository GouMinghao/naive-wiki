DUMP_DIR = '__PKL__'
TF_LIST_FILENAME_POST_FREFIX = '_tf.pkl'
DF_LIST_FILENAME_POST_FREFIX = '_df.npy'
DL_LIST_FILENAME_POST_FREFIX = '_dl.npy'
LINK_LIST_FILENAME_POST_FREFIX = '_link.pkl'
TERM2ID_DICT_FILENAME_POST_FREFIX = '_term2id.pkl'
ID2TERM_DICT_FILENAME_POST_FREFIX = '_id2term.pkl'

from wiki_xml_handler import wiki_xmlhandler
from termer import Termer

import numpy as np
import os
import pickle
from collections import Counter


if not os.path.exists(DUMP_DIR):
    os.mkdir(DUMP_DIR)

############## Data Stucture #############
# tf = [
#     {0:2, 3:5 .....} # doc 0
#     {1:3, 3:1 .....} # doc 1
#     ...
#     {         .....} # doc n
# ]

# # tf[d][t] is the term frequency for term 't' in document 'd'.

# df = [3, 5, 0 ,4 ...] # df[t] is the document frequency for term 't'.

# dl = [123,43,2354 ...] # dl[d] is the number of terms in document 'd'.

# avgdl = np.array(dl).mean() # avgdl is the average number of terms in all the documents.

# link_list = [
#     {1,2,4,6...},
#     {2,3,4...},
#     ...
#     {...}
# ]

class Posting_handler(object):
    def __init__(self,xml_file_name):
        self.file_name = xml_file_name.replace('.xml','')
        print('\033[0;33mRetrieving XML Handler\033[0m')
        self.xml_handler = wiki_xmlhandler(xml_file_name)
        #######################################
        #######Don't use termer directly ######
        ###### User the two dicts instead #####
        self.termer = Termer(False) ###########
        #######################################
        #######################################
        self.num_doc = len(self.xml_handler.doc_list)
        print('\033[0;33mRetrieving TF, DF, DL and Termer\033[0m')
        self.tf_list, self.df_list, self.dl_list, self.term2id_dict, self.id2term_dict = self.get_tf_df_dl_term() # list of dicts, np.array, np.array, dict, dict
        print('\033[0;33mRetrieving Link\033[0m')
        self.link_list = self.get_link_list() # list of sets
        self.avgdl = self.get_avgdl()

    def tf(self,doc_id,term_id):
        '''
        **Input:**

        - doc_id: int of the id of the doc

        - term_id: int of the id of the term

        **Output:**

        - int of the term frequency for term_id in document doc_id
        '''
        doc_tf = self.tf_list[doc_id]
        if term_id in doc_tf.keys():
            return doc_tf[term_id]
        else:
            return 0
    
    def df(self,term_id):
        '''
        **Input:**

        - term_id: int of the id of the term

        **Output:**

        - int of the document frequency for term_id
        '''
        return self.df_list[term_id]

    def idf(self,term_id):
        '''
        **Input:**

        - term_id: int of the id of the term

        **Output:**

        - float of the inversed document frequency for term_id
        '''
        ############# NOT SURE ##############
        # total number of docs / number of docs that contain the term
        return self.num_doc / self.df(term_id)

    def dl(self,doc_id):
        '''
        **Input:**

        - doc_id: int of the id of the doc

        **Output:**

        - int of the number of terms for document doc_id
        '''
        return self.dl_list[doc_id]

    def link_set(self,doc_id):
        '''
        **Input:**

        - doc_id: int of the id of the doc

        **Output:**

        - set of the ids of docs which are linked by document doc_id
        '''
        return self.link_list[doc_id]
    def get_avgdl(self):
        '''
        **Output:**
        - float of the average document length of all documents
        '''
        return self.dl_list.mean()

    def get_term_list_and_link_set(self,id_or_title):
        '''
        **Input:**
        
        - id_or_title: string or int of the title or id of the doc

        **Output:**

        - term_id_list, link_set

        - term_id_list: a list of the id of terms in the text sequence

        - link_set: a set of doc ids which are link by this document
        '''
        doc_dict = self.xml_handler.get_plain_wiki_text_and_link(id_or_title)
        if doc_dict is None:
            return ([],set())
        plain_wiki_text = doc_dict['text']
        link_set = doc_dict['link_set']
        # print(plain_wiki_text)
        term_id_list=self.termer.to_terms(plain_wiki_text)
        return term_id_list,link_set

    def get_tf_df_dl_term(self):
        tf_file_name = os.path.join(DUMP_DIR,self.file_name+TF_LIST_FILENAME_POST_FREFIX)
        df_file_name = os.path.join(DUMP_DIR,self.file_name+DF_LIST_FILENAME_POST_FREFIX)
        dl_file_name = os.path.join(DUMP_DIR,self.file_name+DL_LIST_FILENAME_POST_FREFIX)
        term2id_file_name = os.path.join(DUMP_DIR,self.file_name+TERM2ID_DICT_FILENAME_POST_FREFIX)
        id2term_file_name = os.path.join(DUMP_DIR,self.file_name+ID2TERM_DICT_FILENAME_POST_FREFIX)

        if not (os.path.exists(tf_file_name) and os.path.exists(df_file_name) and os.path.exists(dl_file_name) and os.path.exists(term2id_file_name) and os.path.exists(id2term_file_name)):
            return self.gen_tf_df_dl_term()
        else:
            print('Loading dumped file form {}'.format(tf_file_name))
            f = open(tf_file_name,'rb')
            tf_list = pickle.load(f)
            f.close()
            print('Loading dumped file form {}'.format(df_file_name))
            df_list = np.load(df_file_name)
            print('Loading dumped file form {}'.format(dl_file_name))
            dl_list = np.load(dl_file_name)
            print('Loading dumped file form {}'.format(term2id_file_name))
            f = open(term2id_file_name,'rb')
            term2id_dict = pickle.load(f)
            f.close()
            print('Loading dumped file form {}'.format(id2term_file_name))
            f = open(id2term_file_name,'rb')
            id2term_dict = pickle.load(f)
            f.close()
            return tf_list,df_list,dl_list,term2id_dict,id2term_dict

    def gen_tf_df_dl_term(self):
        '''generate tf df dl and term2id,id2term'''
        tf_file_name = os.path.join(DUMP_DIR,self.file_name+TF_LIST_FILENAME_POST_FREFIX)
        df_file_name = os.path.join(DUMP_DIR,self.file_name+DF_LIST_FILENAME_POST_FREFIX)
        dl_file_name = os.path.join(DUMP_DIR,self.file_name+DL_LIST_FILENAME_POST_FREFIX)
        term2id_file_name = os.path.join(DUMP_DIR,self.file_name+TERM2ID_DICT_FILENAME_POST_FREFIX)
        id2term_file_name = os.path.join(DUMP_DIR,self.file_name+ID2TERM_DICT_FILENAME_POST_FREFIX)
        
        tf_list = []
        dl_list = np.zeros(self.num_doc,dtype=np.uint32)

        print('generating tf list, and dl list')
        for i in range(self.num_doc):
            print('\r[%d/%d]:   %.3f%%' % (i+1,self.num_doc,(i+1)/self.num_doc * 100),end='')
            term_id_list,_ = self.get_term_list_and_link_set(i)
            dl_list[i] = len(term_id_list)
            tf_dict = Counter(term_id_list)
            tf_list.append(tf_dict)
        print('\ngenerating df list')
        
        df_list = np.zeros(self.termer.get_number_of_terms(),dtype = np.uint32)
        for i in range(self.num_doc):
            print('\r[%d/%d]:   %.3f%%' % (i+1,self.num_doc,(i+1)/self.num_doc * 100),end='')
            for term_id in tf_list[i]:
                df_list[term_id] += tf_list[i][term_id]

        print('')

        np.save(dl_file_name,dl_list)
        np.save(df_file_name,df_list)
        with open(tf_file_name,'wb') as f:
            pickle.dump(tf_list,f)
        with open(term2id_file_name,'wb') as f:
            pickle.dump(self.termer.term2id_dict,f)
        with open(id2term_file_name,'wb') as f:
            pickle.dump(self.termer.id2term_dict,f)  
        return tf_list,df_list,dl_list,self.termer.term2id_dict,self.termer.id2term_dict

    def get_link_list(self):
        ''' retrieve the link list'''
        link_file_name = os.path.join(DUMP_DIR,self.file_name+LINK_LIST_FILENAME_POST_FREFIX)
        if not os.path.exists(link_file_name):
            return self.gen_link_list()
        else:
            print('Loading dumped file form {}'.format(link_file_name))
            f = open(link_file_name,'rb')
            link_list = pickle.load(f)
            f.close()
            return link_list

    def gen_link_list(self):
        '''generate the link list for the xml'''
        link_file_name = os.path.join(DUMP_DIR,self.file_name+LINK_LIST_FILENAME_POST_FREFIX)
        link_list = []
        print('generating link list')
        for i in range(self.num_doc):
            print('\r[%d/%d]:   %.3f%%' % (i+1,self.num_doc,(i+1)/self.num_doc * 100),end='')
            doc_dict = self.xml_handler.get_plain_wiki_text_and_link(i)
            link_list.append(doc_dict['link_set'])
        print('')
        f = open(link_file_name,'wb')
        pickle.dump(link_list,f)
        f.close()
        return link_list
        
    def get_term_by_id(self,id):
        '''
        **Input:**

        - id: int of the term id

        **Output:**

        - string of the corresponding term
        '''
        if id in self.id2term_dict.keys():
            return self.id2term_dict[id]
        else:
            return None

    def get_id_by_term(self,term):
        '''
        **Input:**

        - string of the corresponding term
        
        **Output:**

        - id: int of the term id
        '''
        if term in self.term2id_dict.keys():
            return self.term2id_dict[term]
        else:
            return None

if __name__ == '__main__':
    ph = Posting_handler('pages.xml')
    print('-------------------------------------------------')
    
    # the term frequency for term with id = 1151 in doc with id = 2
    print('\033[0;34mThe term frequency for term with id = 1151 in doc with id = 2:\033[0m\n%d' % ph.tf(doc_id = 2,term_id=1151))
    print('\033[0;34mThe term frequency for term with id = 1151 in doc with id = 10:\033[0m\n%d' % ph.tf(doc_id = 10,term_id=1151))

    # the document frequency of the term with id=1151
    print('\033[0;34mThe document frequency of the term with id=1151:\033[0m\n%d' % ph.df_list[1151])
    print('\033[0;34mThe document frequency of the term with id=1151:\033[0m\n%d' % ph.df(1151)) # recommended

    # the document frequency of the term with id=1151
    print('\033[0;34mThe inversed document frequency of the term with id=1151:\033[0m\n%f' % ph.idf(1151)) # recommended

    # the link set for doc with id = 68
    print('\033[0;34mThe link set for doc with id = 68:\033[0m\n{}'.format(ph.link_set(68)))

    # the length of document with id = 69
    print('\033[0;34mThe length of document with id = 69:\033[0m\n%d' % (ph.dl(69)))
    
    # the average document length
    print('\033[0;34mThe average document length:\033[0m\n%f' % ph.avgdl)

    # the term whose id is 1151
    print('\033[0;34mThe term whose id is 1151:\033[0m\n%s' % ph.get_term_by_id(1151))
    # the term id for 'redirect'
    print("\033[0;34mThe term id for 'redirect':\033[0m\n%d" % ph.get_id_by_term('redirect'))
    
