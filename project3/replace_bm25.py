import os
import pysolr
import requests

import json

#CORE_NAME = "VSM"
CORE_NAME = "bm25"

AWS_IP = "localhost"


def delete_core(core=CORE_NAME):
    print(os.system('sudo su - solr -c "/opt/solr/bin/solr delete -c {core}"'.format(core=core)))


def create_core(core=CORE_NAME):
    print(os.system(
        'sudo su - solr -c "/opt/solr/bin/solr create -c {core} -n data_driven_schema_configs"'.format(
            core=core)))


# collection

collection = [{
    "id": 1,
    "first_name": "Chickie",
    "last_name": "Proven",
    "email": "cproven0@alexa.com",
    "age": 77,
    "pincodes": [2121212, 3232323]
}, {
    "id": 2,
    "first_name": "Dex",
    "last_name": "Bofield",
    "email": "dbofield1@about.com",
    "age": 88,
    "pincodes": [2121212, 3232323]
}, {
    "id": 3,
    "first_name": "Saba",
    "last_name": "Ace",
    "email": "sace2@craigslist.org",
    "age": 55,
    "pincodes": [2121212, 3232323]
}, {
    "id": 4,
    "first_name": "Hymie",
    "last_name": "Patterfield",
    "email": "hpatterfield3@plala.or.jp",
    "age": 22,
    "pincodes": [2121212, 3232323]
}, {
    "id": 5,
    "first_name": "Chiarra",
    "last_name": "Cornils",
    "email": "ccornils4@patch.com",
    "age": 23,
    "pincodes": [2121212, 3232323]
}]


class Indexer:
    def __init__(self):
        self.solr_url = f'http://{AWS_IP}:8983/solr/'
        self.connection = pysolr.Solr(self.solr_url + CORE_NAME, always_commit=True, timeout=5000000)

    def do_initial_setup(self):
        delete_core()
        create_core()

    def create_documents(self, docs):
        print(self.connection.add(docs))

    def add_fields(self):
        data = {
            "add-field": [
                {"name": "lang", "type": "string", "multiValued": False},
                {"name": "text_en", "type": "text_en", "multiValued": False},
                {"name": "text_de", "type": "text_de", "multiValued": False},
                {"name": "text_ru", "type": "text_ru", "multiValued": False},
                {"name": "tweet_hashtags", "type": "strings", "multiValued": True},
                {"name": "tweet_urls", "type": "strings", "multiValued": True},

            ]
        }

        print(requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json())

    def replace_fields(self):
        data = {
            "replace-field": [
                {
                    "name": "age",
                    "type": "string",
                    "multiValued": False
                }
            ]
        }

        print(requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json())

    def replace_BM25(self, b=None, k1=None):
        data = {
            "replace-field-type": [
                {
                    'name': 'text_en',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'indexAnalyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.StopFilterFactory',
                            'words': 'lang/stopwords_en.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.EnglishPossessiveFilterFactory'
                        }, {
                            'class': 'solr.KeywordMarkerFilterFactory',
                            'protected': 'protwords.txt'
                        }, {
                            'class': 'solr.PorterStemFilterFactory'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.BM25SimilarityFactory',
                        'b': str(b),
                        'k1': str(k1)
                    },
                    'queryAnalyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.SynonymGraphFilterFactory',
                            'expand': 'true',
                            'ignoreCase': 'true',
                            'synonyms': 'synonyms.txt'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'words': 'lang/stopwords_en.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.EnglishPossessiveFilterFactory'
                        }, {
                            'class': 'solr.KeywordMarkerFilterFactory',
                            'protected': 'protwords.txt'
                        }, {
                            'class': 'solr.PorterStemFilterFactory'
                        }]
                    }
                }, {
                    'name': 'text_ru',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'analyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'format': 'snowball',
                            'words': 'lang/stopwords_ru.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.SnowballPorterFilterFactory',
                            'language': 'Russian'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.BM25SimilarityFactory',
                        'b': str(b),
                        'k1': str(k1)
                    },
                }, {
                    'name': 'text_de',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'analyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'format': 'snowball',
                            'words': 'lang/stopwords_de.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.GermanNormalizationFilterFactory'
                        }, {
                            'class': 'solr.GermanLightStemFilterFactory'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.BM25SimilarityFactory',
                        'b': str(b),
                        'k1': str(k1)
                    },
                }
            ]
        }

        print(requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json())

    def replace_VSM(self, b=None, k1=None):
        data = {
            "replace-field-type": [
                {
                    'name': 'text_en',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'indexAnalyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.StopFilterFactory',
                            'words': 'lang/stopwords_en.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.EnglishPossessiveFilterFactory'
                        }, {
                            'class': 'solr.KeywordMarkerFilterFactory',
                            'protected': 'protwords.txt'
                        }, {
                            'class': 'solr.PorterStemFilterFactory'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.ClassicSimilarityFactory'
                    },
                    'queryAnalyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.SynonymGraphFilterFactory',
                            'expand': 'true',
                            'ignoreCase': 'true',
                            'synonyms': 'synonyms.txt'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'words': 'lang/stopwords_en.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.EnglishPossessiveFilterFactory'
                        }, {
                            'class': 'solr.KeywordMarkerFilterFactory',
                            'protected': 'protwords.txt'
                        }, {
                            'class': 'solr.PorterStemFilterFactory'
                        }]
                    }
                }, {
                    'name': 'text_ru',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'analyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'format': 'snowball',
                            'words': 'lang/stopwords_ru.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.SnowballPorterFilterFactory',
                            'language': 'Russian'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.ClassicSimilarityFactory'
                    },
                }, {
                    'name': 'text_de',
                    'class': 'solr.TextField',
                    'positionIncrementGap': '100',
                    'analyzer': {
                        'tokenizer': {
                            'class': 'solr.StandardTokenizerFactory'
                        },
                        'filters': [{
                            'class': 'solr.LowerCaseFilterFactory'
                        }, {
                            'class': 'solr.StopFilterFactory',
                            'format': 'snowball',
                            'words': 'lang/stopwords_de.txt',
                            'ignoreCase': 'true'
                        }, {
                            'class': 'solr.GermanNormalizationFilterFactory'
                        }, {
                            'class': 'solr.GermanLightStemFilterFactory'
                        }]
                    },
                    'similarity': {
                        'class': 'solr.ClassicSimilarityFactory'
                    },
                }
            ]
        }

        print(requests.post(self.solr_url + CORE_NAME + "/schema", json=data).json())


def add_data(indexer):
    with open("train.json") as json_file:
        whole_data = json.load(json_file)

        for data in whole_data:
            lang = data['lang']
            lang = 'text_' + lang
            print(data[lang])
            break

    #indexer.create_documents(data)

if __name__ == "__main__":
    i = Indexer()
    #add_data(i)
    #'''
    i.do_initial_setup()


    #i.replace_BM25(b=0.8, k1=1.4)

    i.replace_VSM(b=0.8, k1=.2)


    i.add_fields()
    #i.replace_fields()
    with open("train.json") as json_file:
        data = json.load(json_file)
    i.create_documents(data)
    #i.create_documents(collection)
    
    #'''


