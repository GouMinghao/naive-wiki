# coding:utf-8
from flask import Flask, request, render_template, redirect, url_for
from typing import List, Sequence
import os

import re
import datetime
from wiki_xml_handler import wiki_xmlhandler

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

app = Flask(__name__, static_url_path='')
from posting import Posting_handler
from searcher import Searcher

ph = Posting_handler('pages_sample_big.xml')
searchers = Searcher(ph)
doc_list, docid_dic = ph.xml_handler.get_dict()

def matchcase(word):
    def replace(m):
        text = m.group()
        if text.isupper():
            return '<em><font color="red">{}</font></em>'.format(word.upper())
        elif text.islower():
            return '<em><font color="red">{}</font></em>'.format(word.lower())
        elif text[0].isupper():
            return '<em><font color="red">{}</font></em>'.format(word.capitalize())
        else:
            return '<em><font color="red">{}</font></em>'.format(word)
    return replace


@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        return redirect(url_for('search', query=query))

    return render_template('index.html')

@app.route("/q/<query>", methods=['POST', 'GET'])
def search(query: str):
    if query.isdigit():
        return redirect(url_for('doc', query=query))
    docs = get_list(query)
    #docs = [10, 66, 68]
    terms,original_query = process_query(query)
    print(docs, terms)
    result = gen_list_html(docs, terms, original_query)
    return render_template('search.html', docs=result, value=query, length=len(docs))

@app.route("/doc/<query>", methods=['POST', 'GET'])
def doc(query):
    doc_id = int(query)
    doc_dict = ph.xml_handler.get_plain_wiki_text_and_link(doc_id)
    wikitext = doc_dict['text']
    f = open('./templates/doc.txt', 'w', encoding='utf-8')
    f.write(wikitext)
    f.close()

    os.system("python ./templates/txt2html.py < ./templates/doc.txt > ./templates/output.html")


    return render_template('output.html')


def get_list(query:str):
    search_algorithm = 'tf-idf'
    #search_algorithm = 'jaccard'
    #search_algorithm = 'log_freq'
    #search_algorithm = 'cosine_similarity'
    #search_algorithm = 'bm25'
    print("method: %s" %(search_algorithm), end='    ')

    start_time = datetime.datetime.now()
    result = searchers.search(query, method=search_algorithm)
    search_time = datetime.datetime.now() - start_time
    print("search time: %f" % (search_time))

    return result

def process_query(query: str) -> List[str]:
    """Process query. Remove stop words and transform
    the tokens into appropriate term ids.

    Args:
        query: query string

    Returns:
        a list of terms for the query string
    """
    original_query = query.split()
    tokens = word_tokenize(query)
    punctuations = '[0-9’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
    tokens = [t for t in tokens if t not in punctuations]

    stop_words = set(stopwords.words('english'))
    query = []
    stemmer = PorterStemmer()
    for t in tokens:
        t_stem = stemmer.stem(t)
        if t_stem in stop_words:
            continue
        query.append(t_stem)
    print("query:", query)
    return query,original_query


def gen_list_html(docs: list, terms: str, original_query: list):
    
    result = []
    for doc_id in docs:
        doc_id=int(doc_id)
        title = doc_list[doc_id][0]
        doc_dict = ph.xml_handler.get_plain_wiki_text_and_link(doc_id)
        wikitext = doc_dict['text']
        # for term in terms:
        #     title = title.replace(term, '<em><font color="red">{}</font></em>'.format(term))
        #     wikitext = wikitext.replace(term, '<em><font color="red">{}</font></em>'.format(term))
        print('original query',original_query)
        for query_word in original_query:
            title = re.sub(query_word, matchcase(query_word), title, flags=re.IGNORECASE)
            # wikitext = re.sub(query_word, matchcase(query_word), wikitext, flags=re.IGNORECASE)
            # title = title.replace(query_word, '<em><font color="red">{}</font></em>'.format(query_word))
            # wikitext = wikitext.replace(query_word, '<em><font color="red">{}</font></em>'.format(query_word))
        # title = title.capitalize()
        print(title)

        result.append((doc_id, title, wikitext))
    return result


if __name__ == "__main__":


    # main_wiki_xmlhandler = wiki_xmlhandler('pages_sample_big.xml')

    app.run(host='0.0.0.0', port=22190, debug=True)

