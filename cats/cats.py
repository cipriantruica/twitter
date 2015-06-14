__author__ = "Adrien Guille"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "adrien.guille@univ-lyon2.fr"
__status__ = "Production"

from flask import Flask, Response, render_template, request
from indexing.vocabulary_index import VocabularyIndex
from search_mongo import Search
import pymongo
from nlplib.lemmatize_text import LemmatizeText
import re

# Connecting to the database
client = pymongo.MongoClient()
dbname = 'TwitterDB'
db = client[dbname]

app = Flask(__name__)

query = {}

def getTweetCount():
    return db.documents.find(query).count()

@app.route('/cats/collection')
def collection_dashboard_page(name=None):
    return render_template('collection.html', name=name) 

@app.route('/cats/collection', methods=['POST'])
def collection_dashboard_page2():
    return collection_dashboard_page()

@app.route('/cats/analysis')
def analysis_dashboard_page(name=None):
    tweetCount = getTweetCount()
    return render_template('analysis.html', name=name, tweetCount=tweetCount) 

@app.route('/cats/analysis', methods=['POST'])
def analysis_dashboard_page2():
    keywords = request.form['keyword']
    date = request.form['date']
    lem = LemmatizeText(keywords)
    lem.createLemmaText()
    lem.createLemmas()
    wordList = []
    for word in lem.wordList:
        """
            If you want to use a regex,
            This example will construct a regex that contains the lemma
            similar in SQL to -> where word like '%fuck%'
        """
        #regex = re.compile(word.word, re.IGNORECASE)
        #wordList.append(regex)
        """
            this one will find only the tweets with the matching word
        """
        wordList.append(word.word)
    global query
    query = {}
    if wordList:
        query["words.word"] = {"$in": wordList }
    if date:
        start, end = date.split(" ") 
        query["date"] = {"$gt": start, "$lte": end}

    if query:
        vocab = VocabularyIndex(dbname)
        vocab.createIndex(query)

    tweetCount = getTweetCount()
    return render_template('analysis.html', tweetCount=tweetCount)  
    
@app.route('/cats/about')
def about_page(name=None):
    return render_template('about.html', name=name)

@app.route('/cats/analysis/construct_vocabulary')
def construct_vocabulary():
    print("constructing vocab")	
    vocab = VocabularyIndex(dbname)
    vocab.createIndex()
    return analysis_dashboard_page()

@app.route('/cats/analysis/vocabulary_cloud')
def getTermCloud():
    if query:
        voc = db.vocabulary_query.find(fields={'word':1,'idf':1},limit=250, sort=[('idf',pymongo.ASCENDING)])
    else:
        voc = db.vocabulary.find(fields={'word':1,'idf':1},limit=250, sort=[('idf',pymongo.ASCENDING)])
    return render_template('word_cloud.html', voc=voc)     
    
@app.route('/cats/analysis/vocabulary.csv')
def getTerms():
    if query:
        voc = db.vocabulary_query.find(fields={'word':1,'idf':1}, limit=1000, sort=[('idf',pymongo.ASCENDING)])
    else:
        voc = db.vocabulary.find(fields={'word':1,'idf':1}, limit=1000, sort=[('idf',pymongo.ASCENDING)])
    csv = 'word,idf\n'
    for doc in voc :
        csv += doc['word']+','+str(doc['idf'])+'\n'
    return Response(csv,mimetype="text/csv")   

@app.route('/cats/analysis/tweets',methods=['POST'])
def getTweets():
    searchPhrase = request.form['cooccurringwords']
    query_exists = False
    if query:
        query_exists = True
    search = Search(searchPhrase=searchPhrase, dbname=dbname, query=query_exists)
    results = search.results()
    return render_template('tweet_browser.html', results=results) 

@app.route('/cats/analysis/named_entities.csv')
def getNamedEntities():
    return ""
    
@app.route('/cats/analysis/named_entities')
def visualizeNamedEntities():
    return ""
    
if __name__ == '__main__':
    app.run(debug=True,host='mediamining.univ-lyon2.fr')
    # run local
    # app.run(debug=True,host='127.0.0.1')
