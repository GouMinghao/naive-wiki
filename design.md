# 确定几个核心类和其核心接口函数：

## **localizer**:
    # 输入 doc id，返回其在那个大文件的offset 和length
    localize(int id) -> long offset， int length 

## **tokenProcessor**:
    ## 将一个word进行处理，包括stem, 转成小写之类的
    tokenize(string word) -> string token

## **parser**:
    # 从offset开始，对length长的文件进行parse，输出对应的forward index, forward index 无需排序
    # forward index 格式是：len (1B): docID (8B): termID (8B): #occurence (1B) : pos (1B) : pos (1B) : ...
                            len (1B): docID (8B): termID (8B): #occurence (1B) : pos (1B) : pos (1B) : ...
    parse(string filename, long offset, long length) -> forward index

## **indexer**:
    # 将forward index 进行排序，按照docID升序进行排序
    # inverted index 格式： len (1B) : termID (8B): docID (8B):  #occurence (1B) : pos (1B) : pos (1B) : ...
                                                    docID (8B):  #occurence (1B) : pos (1B) : pos (1B) : ...
                                                    docID (8B):  #occurence (1B) : pos (1B) : pos (1B) : ...
                            len (1B) : termID (8B): docID (8B):  #occurence (1B) : pos (1B) : pos (1B) : ...
                                                    docID (8B):  #occurence (1B) : pos (1B) : pos (1B) : ...
                                                    docID (8B):  #occurence (1B) : pos (1B) : pos (1B) : ...
    index(forward index) -> inverted index

## **searcher**:
    # 这个应该是一个抽象类,具体可以实现五种抽象的类来完成具体的工作
    # 搜索inverted posting，如果有符合要求的docid，将其送入scorer进行评分
    # 返回score最大的k个
    search(string[] query) -> list of docID

## **scorer**:
    # 输入 某docid的对应query每一个单词的inverted posting，对其进行打分
    # 返回得分值
    # 这里也是我们的重点，我们要写5个具体函数进行打分，供这个函数调用
    score(a list of（#occurence (1B) : pos (1B) : pos (1B) : ...）) -> double 

## **server**:
    # 服务器类相应用户请求，调用searcher.search()，得到前k个docid，从localizer中得到对应的具体文章位置，进而得到内容
    # （画出重点，生成summary)
    # 生成html文件进行渲染，返回用户

### Functions:
- get_xml(int docID): return the xml string of the doc.
- get_abstract(int docID): return the abstract string of the doc.
- get_list(string searching string): return the docID_list for given searching string.
- gen_list_html(list docID_list): return the html string of search results list. with doc title and abstract  
- gen_doc_html(int docID): return the main page html string of the doc.
- gen_index_html(list docID_list): return the index.html. Index.html is a static file.
- on_click_search(string search_string): When the user click the "search" botton on the index.html, this function is called. This function should call the get_list and gen_list_html functions and return the list html.
- on_click_doc(int docID): When the user click any of the searching result on list.html, this function is called. This function should call the gen_doc_html function and return the doccument main html.
- on_connection(): When the user opens the browser and type in the url of our website, this function is called. This function should call gen_index_html function and return the index html.



# 确定几个核心数据结构：
需要存放到硬盘中的：
- dictionary: string -> int ：term到id的映射
- docs: 映射，每一条都是：string -> docid, offset, length
- forward index: 编码格式如上
- inverted index:编码如上
    
```python
tf = [
    {0:2, 3:5 .....} # doc 0
    {1:3, 3:1 .....} # doc 1
    ...
    {         .....} # doc n
]

# tf[d][t] is the term frequency for term 't' in document 'd'.

df = [3, 5, 0 ,4 ...] # df[t] is the document frequency for term 't'.

dl = [123,43,2354 ...] # dl[d] is the number of terms in document 'd'.

avgdl = np.array(dl).mean() # avgdl is the average number of terms in all the documents.

link_list = [
    {1,2,4,6...},
    {2,3,4...},
    ...
    {...}
]
# BM25 score
# https://blog.csdn.net/zhoubl668/article/details/7321012

```

