import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from chromadb import PersistentClient
from neo4j import GraphDatabase
import chromadb.utils.embedding_functions as embedding_functions


def get_neo4j_session():
    assert 'NEO4J_PASSWORD' in os.environ, 'NEO4J_PASSWORD should be set in .env'
    neo4j_driver = GraphDatabase.driver(
        'bolt://localhost:7687', auth=('neo4j', os.environ['NEO4J_PASSWORD'])
    )
    return neo4j_driver.session()


def get_mongo_client(uri=None):
    from pymongo.errors import ServerSelectionTimeoutError

    assert (
        'MONGO_USERNAME' in os.environ and 'MONGO_PASSWORD' in os.environ
    ), 'MongoDB username and password should be set in .env'

    if uri is None:
        uri = 'mongodb://localhost:27017'

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
    except ServerSelectionTimeoutError:
        print('Could not connect to MongoDB')
        print(
            'Make sure your IP address has been enabled in the MongoDB Atlas network access settings.'
        )
    except Exception as e:
        print(e)

    return client


def setup_mongo_collection(
    collection_name,
    uri=None,
    db_name='research_database',
    clear_existing=False,
):
    assert (
        'MONGO_USERNAME' in os.environ and 'MONGO_PASSWORD' in os.environ
    ), 'MongoDB username and password should be set in .env'

    if uri is None:
        uri = 'mongodb://localhost:27017'

    # Create a new client and connect to the server
    client = get_mongo_client(uri)

    # In MongoDB, databases and collections are created lazily (when first document is inserted)
    db = client[db_name]
    collection = db[collection_name]

    if clear_existing:
        collection.drop()
        print(f'Dropped existing collection: {collection_name}')

    # print the number of documents in the collection
    print(
        f'Number of documents in {collection_name}: {collection.count_documents({})}'
    )

    return collection


def get_chromadb_collection(collection_name='pubmed_docs', 
    path='../../data/chroma_data',
    embedding: str = "text-embedding-3-large"):

    assert 'OPENAI' in os.environ, 'OPENAI API key should be set in .env'
    if embedding is not None:
        embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=os.getenv('OPENAI'),
                    model_name=embedding
            )
    else:
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2")
    client = PersistentClient(path=path)
    # check if collection exists, if not create it
    if collection_name in [col.name for col in client.list_collections()]:
        return client.get_collection(name=collection_name)
    else:
        print(f'Created new collection: {collection_name}')
        return client.create_collection(name=collection_name, embedding_function=embedding_function)