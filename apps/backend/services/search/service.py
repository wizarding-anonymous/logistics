from elasticsearch import Elasticsearch
from .es_client import get_es_client

# Define the names of the indices we will use
RFQ_INDEX = "rfqs"
ORDER_INDEX = "orders"

def index_document(index_name: str, document_id: str, document_body: dict):
    """
    Indexes a document into the specified Elasticsearch index.
    """
    es = get_es_client()
    es.index(index=index_name, id=document_id, body=document_body)
    print(f"Indexed document {document_id} into index {index_name}")

def search_documents(query: str):
    """
    Performs a multi-index search across all relevant indices.
    """
    es = get_es_client()

    # A simple multi-match query across common fields
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["*description", "*address", "*notes", "id"],
                "fuzziness": "AUTO"
            }
        }
    }

    response = es.search(
        index=[RFQ_INDEX, ORDER_INDEX],
        body=search_body
    )

    return [hit['_source'] for hit in response['hits']['hits']]
