# coding:utf-8
from flask import Flask, request, render_template, redirect, url_for
from typing import List, Sequence
import os



from wiki_xml_handler import wiki_xmlhandler

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

app = Flask(__name__, static_url_path='')


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
    terms = process_query(query)
    print(docs, terms)
    result = gen_list_html(docs, terms)
    return render_template('search.html', docs=result, value=query, length=len(docs))

@app.route("/doc/<query>", methods=['POST', 'GET'])
def doc(query):
    doc_id = int(query)
    doc_dict = main_wiki_xmlhandler.get_plain_wiki_text_and_link(doc_id)
    wikitext = doc_dict['text']
    f = open('./templates/doc.txt', 'w', encoding='utf-8')
    f.write(wikitext)
    f.close()

    os.system("python ./templates/txt2html.py < ./templates/doc.txt > ./templates/output.html")


    return render_template('output.html')


def get_list(query:str):

    return (searchers.search(query))

def process_query(query: str) -> List[str]:
    """Process query. Remove stop words and transform
    the tokens into appropriate term ids.

    Args:
        query: query string

    Returns:
        a list of terms for the query string
    """
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
    return query


def gen_list_html(docs: list, terms: str):


    doc_list, docid_dic = main_wiki_xmlhandler.get_dict()
    result = []
    for doc_id in docs:
        doc_id=int(doc_id)
        title = doc_list[doc_id][0]
        doc_dict = main_wiki_xmlhandler.get_plain_wiki_text_and_link(doc_id)
        wikitext = doc_dict['text']
        for term in terms:
            title = title.replace(term, '<em><font color="red">{}</font></em>'.format(term))
            wikitext = wikitext.replace(term, '<em><font color="red">{}</font></em>'.format(term))


        result.append((doc_id, title, wikitext))
    return result


if __name__ == "__main__":
    from posting import Posting_handler
    from searcher import Searcher

    ph = Posting_handler('pages_sample.xml')
    searchers = Searcher(ph)

    main_wiki_xmlhandler = wiki_xmlhandler('pages_sample.xml')

    app.run(host='localhost', port=9000, debug=True)

