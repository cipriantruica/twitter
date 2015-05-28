# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import pymongo
from twitter.indexing.vocabulary_index import VocabularyIndex
from time import time


class MarketMatrix:
    def __init__(self, dbname='TwitterDB'):
        client = pymongo.MongoClient()
        self.dbname = dbname
        self.db = client[self.dbname]
        self.cursor = None

    """
        input:
            query: a query used to build the vocabulary, if no query is given then we use the entire vocabulary
            limit: parameter used to limit the numeber of returned line, based on idf
            rebuild: parameter used if the vocabulary should be rebuilt
    """
    def build(self, query=None, limit=None, rebuild=False):
        if query:
            # if the vocabulary should be rebuilt
            if rebuild:
                vocab = VocabularyIndex(self.dbname)
                vocab.createIndex(query)
            if limit:
                self.cursor = self.db.vocabulary_query.find(fields={'word': 1, 'idf': 1, 'docIDs.docID': 1, 'docIDs.count': 1, 'docIDs.tf': 1}, limit=limit, sort=[('idf', pymongo.ASCENDING)])
            else:
                self.cursor = self.db.vocabulary_query.find(fields={'word': 1, 'idf': 1, 'docIDs.docID': 1, 'docIDs.count': 1, 'docIDs.tf': 1}, sort=[('idf', pymongo.ASCENDING)])
        else:
            # if the vocabulary should be rebuilt
            if rebuild:
                vocab = VocabularyIndex(self.dbname)
                vocab.createIndex()
            if limit:
                self.cursor = self.db.vocabulary.find(fields={'word': 1, 'idf': 1, 'docIDs.docID': 1, 'docIDs.count': 1, 'docIDs.tf': 1}, limit=limit, sort=[('idf', pymongo.ASCENDING)])
            else:
                self.cursor = self.db.vocabulary.find(fields={'word': 1, 'idf': 1, 'docIDs.docID': 1, 'docIDs.count': 1, 'docIDs.tf': 1}, sort=[('idf', pymongo.ASCENDING)])

    """
        function used to write an market matrix file
    """
    def writeMMFile(self, filename, num_rows, num_columns, num_entries, market_matrix):
        with open(filename, 'w') as mm_file:
            mm_file.write('%%MatrixMarket matrix coordinate real general\n%\n')
            mm_file.write(str(num_rows) + ' ' + str(num_columns) + ' ' + str(num_entries) + '\n')
            idx = 1
            for elem in market_matrix:
                for column, value in elem:
                    mm_file.write(str(idx) + ' ' + str(column+1) + ' ' + str(value) + '\n')
                idx += 1
            mm_file.close()

    """
        constructs the binary market matrix
        output:
            the binary market matrix
    """
    def buildBinaryMM(self, filename=None):
        if self.cursor:
            self.cursor.rewind()
            num_entries = 0
            id2word = {}
            word2id = {}
            wordID = 0
            id2tweetID = {}
            tweetID2id = {}
            tweetID = 0
            market_matrix = []
            for elem in self.cursor:
                num_entries += len(elem['docIDs'])
                if word2id.get(elem['word'], -1) == -1:
                    id2word[wordID] = elem['word']
                    word2id[elem['word']] = wordID
                    wordID += 1
                for doc in elem['docIDs']:
                    if tweetID2id.get(doc['docID'], -1) == -1:
                        id2tweetID[tweetID] = doc['docID']
                        tweetID2id[doc['docID']] = tweetID
                        tweetID += 1
                    if len(market_matrix) == tweetID:
                        market_matrix[tweetID2id[doc['docID']]] += [(word2id[elem['word']], 1)]
                    else:
                        market_matrix.append([(word2id[elem['word']], 1)])
            #if filename is given then write to file
            if filename:
                self.writeMMFile(filename=filename, num_rows=len(id2tweetID), num_columns=len(id2word), num_entries=num_entries, market_matrix=market_matrix)
            return id2word, id2tweetID, market_matrix

    """
        constructs the count market matrix
        output:
            the count market matrix
    """

    def buildCountMM(self, filename=None):
        if self.cursor:
            self.cursor.rewind()
            num_entries = 0
            id2word = {}
            word2id = {}
            wordID = 0
            id2tweetID = {}
            tweetID2id = {}
            tweetID = 0
            market_matrix = []
            for elem in self.cursor:
                num_entries += len(elem['docIDs'])
                if word2id.get(elem['word'], -1) == -1:
                    id2word[wordID] = elem['word']
                    word2id[elem['word']] = wordID
                    wordID += 1
                for doc in elem['docIDs']:
                    if tweetID2id.get(doc['docID'], -1) == -1:
                        id2tweetID[tweetID] = doc['docID']
                        tweetID2id[doc['docID']] = tweetID
                        tweetID += 1
                    if len(market_matrix) == tweetID:
                        market_matrix[tweetID2id[doc['docID']]] += [(word2id[elem['word']], doc['count'])]
                    else:
                        market_matrix.append([(word2id[elem['word']], doc['count'])])
            #if filename is given then write to file
            if filename:
                self.writeMMFile(filename=filename, num_rows=len(id2tweetID), num_columns=len(id2word), num_entries=num_entries, market_matrix=market_matrix)
            return id2word, id2tweetID, market_matrix

    """
        constructs the TF market matrix
        output:
            the TF market matrix
    """
    def buildTFMM(self, filename=None):
        if self.cursor:
            self.cursor.rewind()
            num_entries = 0
            id2word = {}
            word2id = {}
            wordID = 0
            id2tweetID = {}
            tweetID2id = {}
            tweetID = 0
            market_matrix = []
            for elem in self.cursor:
                num_entries += len(elem['docIDs'])
                if word2id.get(elem['word'], -1) == -1:
                    id2word[wordID] = elem['word']
                    word2id[elem['word']] = wordID
                    wordID += 1
                for doc in elem['docIDs']:
                    if tweetID2id.get(doc['docID'], -1) == -1:
                        id2tweetID[tweetID] = doc['docID']
                        tweetID2id[doc['docID']] = tweetID
                        tweetID += 1
                    if len(market_matrix) == tweetID:
                        market_matrix[tweetID2id[doc['docID']]] += [(word2id[elem['word']], doc['tf'])]
                    else:
                        market_matrix.append([(word2id[elem['word']], doc['tf'])])
            #if filename is given then write to file
            if filename:
                self.writeMMFile(filename=filename, num_rows=len(id2tweetID), num_columns=len(id2word), num_entries=num_entries, market_matrix=market_matrix)
            return id2word, id2tweetID, market_matrix

# these are just tests
if __name__ == '__main__':
    query_or = {"words.word" : {"$in": ["shit", "fuck"] }, "date": {"$gt": "2015-04-10", "$lte":  "2015-04-12"}}
    query_and = {"$and": [{"words.word": "shit"}, {'words.word': "fuck"}],
                 "date": {"$gt": "2015-04-10", "$lte": "2015-04-12"}}
    #for the entire vocabulary
    #mm.build(rebuild=True)
    start = time()
    mm = MarketMatrix(dbname='TwitterDB')
    mm.build()

    #for given queries with/without limit
    #mm.build(query=query_or)
    #mm.build(query=query_and, limit=100)
    end = time()
    print 'Build time:',(end-start)

    start = time()
    mm.buildBinaryMM('mm_binary.mtx')
    end = time()
    print "Binary MM time:", (end-start)

    start = time()
    mm.buildCountMM('mm_count.mtx')
    end = time()
    print "Binary Count time:", (end-start)
    start = time()
    mm.buildTFMM('mm_tf.mtx')
    end = time()
    print "Binary TF time:", (end-start)
