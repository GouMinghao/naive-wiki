DUMP_DIR = '__PKL__'
STATE_OUTSIDE = 0
STATE_INSIDE = 1
import os
import re
import pickle
import xml.etree.ElementTree as ET

class text_file(object):
    '''
    A wrapper class for dealing with wiki xml.
    Wiki xml file shouldn't be read with the build-in file module in Python
    '''
    def __init__(self,f):
        self.f = f
        self.seek = self.f.seek
        self.tell = self.f.tell
        self.close = self.f.close

    def read(self,size):
        return self.f.read(size).decode(encoding='latin1')

def read_text_with_offset_and_length(file_path,offset,length):
    '''
    ** Input: **
    
    - file_path: string of the file path

    - offset: int of the offset characters

    - length: int of the length of the text that want to read

    ** Output: **

    - string from file[offset] to file[offset + length]
    '''
    f = text_file(open(file_path,mode='rb'))
    f.seek(offset)
    txt = f.read(length)
    f.close()
    return txt


    
class wiki_xmlhandler(object):
    '''
    ** Input: **

    - file_name: string of the xml file name
    '''
    def __init__(self,file_name):
        self.file_name = file_name
        self.doc_list,self.docid_dic = self.get_dict()
    
    def get_dict(self):
        '''
        ** Output: **

        - tuple:(doc_list,docid_dic)
        '''
        if not os.path.exists(os.path.join(DUMP_DIR,self.file_name.replace('.xml','.pkl'))):
            print('No dumped file available, gen_dict is called')
            return self.gen_dict()
        else: 
            print('Loading dumped file from {}'.format(os.path.join(DUMP_DIR,self.file_name.replace('.xml','.pkl'))))
            return self.load_dump()

    def gen_dict(self):
        '''
        Parsing the xmlfile and extracting needed information.

        ** Output: **

        - tuple:(doc_list,docid_dic)
        
        '''
        doc_list = []
        docid_dic = dict()
        # term_dict format:  id -> [term,offset,length]
        # docid_dic format:  term -> id
        f = text_file(open(self.file_name,mode='rb',buffering=2 **20))
        total_length = f.seek(0,2)
        print('File length:{}'.format(total_length))
        f.seek(0)
        string = f.read(7)
        state = STATE_OUTSIDE
        id = 0
        while True:
            ch = f.read(1)
            if ch == '':
                break
            string = string[1:]+ch

            if state == STATE_OUTSIDE:
                if string.endswith('<page>'):
                    offset = f.tell() - 6
                    state = STATE_INSIDE
                    continue
            if state == STATE_INSIDE:
                if string.endswith('</page>'):
                    length = f.tell() - offset
                    f.seek(offset,0)

                    seek_ptr = f.tell()
                    page_xml = f.read(length)
                    after_ptr = f.tell()
                    assert after_ptr - seek_ptr == length

                    p = re.compile(r'<title>(.*?)</title>',re.DOTALL)
                    title_list = re.findall(p,page_xml)
                    assert(len(title_list) == 1)
                    title = title_list[0]
                    print('\rProcessing: [%6.4f%%] id=%d' % (f.tell() / total_length * 100,id),end='')
                    # print(f.tell(),id)
                    doc_list.append([title,offset,length])
                    docid_dic[title] = id
                    id += 1
                    # print(title_list[0].replace('<title>','').replace('</title>',''))
                    state = STATE_OUTSIDE
                    continue
        f.close()
        print('\nFile parsing finished, number of docs:{}'.format(id))
        if not os.path.exists(os.path.join(DUMP_DIR)):
            os.mkdir(os.path.join(DUMP_DIR))
        dump_file = open(os.path.join(DUMP_DIR,self.file_name.replace('.xml','.pkl')),'wb')
        pickle.dump([doc_list,docid_dic],dump_file)
        dump_file.close()
        return doc_list,docid_dic

    def load_dump(self):
        '''

        Loading the extracted information from dumped file

        ** Output: **

        - dic[0]: list of [doc title, offset, length]

        - dic[1]: dict of {title:id}
        '''
        f = open(os.path.join(DUMP_DIR,self.file_name.replace('.xml','.pkl')),'rb')
        dic = pickle.load(f)
        f.close()
        return dic[0],dic[1]

    def get_doc_id(self,id):
        '''
        ** Input: **

        - id: int of the doc id

        ** Oupput: **

        - string of the doc xml content
        '''
        if id < len(self.doc_list):
            [title,offset,length] = self.doc_list[id]
            return read_text_with_offset_and_length(self.file_name,offset,length)
        else:
            return None

    def get_doc_title(self,title):
        '''
        ** Input: **

        - title: string of the doc title

        ** Oupput: **

        - string of the doc xml content
        '''
        id = self.docid_dic.get(title)
        if id is not None:
            return self.get_doc_id(id)
        else:
            return None

    def get_doc(self,id_or_title):
        '''
        ** Input: **
        
        - id_or_title: string of the doc title or int of the docid

        ** Output: **

        - string of the doc xml content
        '''
        if isinstance(id_or_title,int):
            id = id_or_title
            return self.get_doc_id(id)

        elif isinstance(id_or_title,str):
            title = id_or_title
            return self.get_doc_title(title)
        else:
            raise ValueError('get doc must be called with int or str, but the given type is:{}'.format(type(id_or_title)))
    
    def get_wiki_text(self,id_or_title):
        doc = self.get_doc(id_or_title)
        root = ET.fromstring(doc)
        revision = root.find('revision')
        wikitext = revision.find('text').text
        return wikitext
    
    def get_redirect(self,id_or_title):
        doc = self.get_doc(id_or_title)
        root = ET.fromstring(doc)
        redirect = root.find('redirect')
        if redirect is None:
            return None
        else:
            return redirect.get('title')
    
    def get_plain_wiki_text_and_link(self,id_or_title):
        wiki_text = self.get_wiki_text(id_or_title)
        if wiki_text is None:
            return None

        doc_dict = dict()
        link_set= set()

        p_double_middle = re.compile(r'\[\[(.*?)\]\]',re.DOTALL)        
        double_middle_list = re.findall(p_double_middle,wiki_text)
        for double_middle in double_middle_list:
            for title in double_middle.split('|'):
                doc_id = self.docid_dic.get(title)
                if doc_id is not None:
                    link_set.add(doc_id)
            wiki_text = wiki_text.replace('[[{}]]'.format(double_middle),'')
       
        double_middle_list = re.findall(p_double_middle,wiki_text)
        for double_middle in double_middle_list:
            wiki_text = wiki_text.replace('[[{}]]'.format(double_middle),'')

        doc_dict['link_set']=link_set

        p_double_bracket = re.compile(r'\{\{(.*?)\}\}',re.DOTALL)    
        double_bracket_list = re.findall(p_double_bracket,wiki_text)
        for double_bracket in double_bracket_list:
            wiki_text = wiki_text.replace('{{'+double_bracket+'}}','')

        p_single_middle = re.compile(r'\[(.*?)\]',re.DOTALL)    
        single_middle_list = re.findall(p_single_middle,wiki_text)

        for single_middle in single_middle_list:
            wiki_text = wiki_text.replace('['+single_middle+']','')

        p_single_bracket = re.compile(r'\{(.*?)\}',re.DOTALL)    
        single_bracket_list = re.findall(p_single_bracket,wiki_text)
        for single_bracket in single_bracket_list:
            wiki_text = wiki_text.replace('{'+single_bracket+'}','')

        p_line = re.compile(r'\n[\*\|].*\n')
        line_list = re.findall(p_line,wiki_text)
        for line in line_list:
            wiki_text = wiki_text.replace(line.replace('\n',''),'')

        doc_dict['text']=wiki_text
        return doc_dict

if __name__ == '__main__':
    main_wiki_xmlhandler = wiki_xmlhandler('pages.xml')
    doc_dict = main_wiki_xmlhandler.get_plain_wiki_text_and_link(338340)
    print(doc_dict['text'])
    print(doc_dict['link_set'])
