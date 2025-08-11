import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")

es_client = Elasticsearch(hosts=[ELASTICSEARCH_URL])

def get_es_client():
    # This could be enhanced to handle connection pooling, etc.
    return es_client
