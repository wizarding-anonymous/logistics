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

from typing import Optional

def search_documents(
    query: str,
    status: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    Performs a multi-index search with optional filters.
    """
    es = get_es_client()

    must_clauses = []
    should_clauses = []

    # Full-text search part
    if query:
        should_clauses.append({
            "multi_match": {
                "query": query,
                "fields": ["*"],
                "fuzziness": "AUTO"
            }
        })

    # Filter part
    if status:
        must_clauses.append({"term": {"status.keyword": status}})

    price_range = {}
    if min_price is not None:
        price_range["gte"] = min_price
    if max_price is not None:
        price_range["lte"] = max_price
    if price_range:
        must_clauses.append({"range": {"price": price_range}})

    search_body = {
        "query": {
            "bool": {
                "must": must_clauses,
                "should": should_clauses,
                "minimum_should_match": 1 if query else 0
            }
        }
    }

    response = es.search(
        index=[RFQ_INDEX, ORDER_INDEX],
        body=search_body
    )

    return [hit['_source'] for hit in response['hits']['hits']]
