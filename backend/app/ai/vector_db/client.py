import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings as app_settings # App's general settings
from typing import List, Dict, Any, Optional, Union

# Collection names from documentation (or make them configurable)
QUESTIONS_COLLECTION_NAME = "questions"
USER_LEARNING_COLLECTION_NAME = "user_learning_patterns"

class ChromaDBClient:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        path: Optional[str] = "./chroma_data", # For persistent local storage if not using HTTP client
        in_memory: bool = False # For transient in-memory client
    ):
        if in_memory:
            self.client = chromadb.Client(ChromaSettings(is_persistent=False))
            # self.client = chromadb.EphemeralClient() # Simpler way for in-memory
        elif host and port:
            # HTTP Client for connecting to a remote ChromaDB server
            self.client = chromadb.HttpClient(
                host=host, # or app_settings.CHROMA_DB_HOST
                port=port, # or app_settings.CHROMA_DB_PORT
                settings=ChromaSettings(chroma_client_auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                                        chroma_client_auth_credentials=app_settings.CHROMA_DB_AUTH_TOKEN if hasattr(app_settings, "CHROMA_DB_AUTH_TOKEN") else None)
                                        # Example for token auth, adjust as needed
            )
        else:
            # Persistent client storing data locally
            self.client = chromadb.PersistentClient(
                path=path,
                settings=ChromaSettings()
            )

        # Placeholder for actual collection objects
        self._questions_collection = None
        self._user_learning_collection = None

    def _get_or_create_collection(self, name: str, metadata_schema: Optional[Dict[str, Any]] = None, embedding_function_name: Optional[str] = "DefaultEmbeddingFunction"):
        """
        Helper to get or create a collection.
        ChromaDB's default embedding function is Sentence Transformers all-MiniLM-L6-v2.
        For Google Text-Embedding-004, a custom embedding function would be needed if not handled externally.
        """
        try:
            # embedding_function = chromadb.utils.embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=app_settings.GEMINI_API_KEY) # Example if using Gemini for embeddings
            # For now, let's assume embeddings are generated externally and passed in, or use Chroma's default.
            # If metadata_schema is provided, it's for validation during add, not strict schema enforcement like SQL.
            collection = self.client.get_or_create_collection(
                name=name,
                # embedding_function=embedding_function, # If using a specific one
                metadata={"hnsw:space": "cosine"} # Example: using cosine distance
            )
            return collection
        except Exception as e:
            # log.error(f"Error getting or creating collection {name}: {e}")
            raise

    @property
    def questions_collection(self):
        if self._questions_collection is None:
            # As per documentation:
            # questions_collection_metadata_schema = {
            #     "question_id": "string", "subject": "string", "topic": "string",
            #     "difficulty": "integer", "type": "string", "priority_score": "float", "year": "integer"
            # }
            # Chroma doesn't enforce metadata schema strictly at collection creation, but good for reference.
            self._questions_collection = self._get_or_create_collection(QUESTIONS_COLLECTION_NAME)
        return self._questions_collection

    @property
    def user_learning_collection(self):
        if self._user_learning_collection is None:
            # user_learning_collection_metadata_schema = {
            #     "user_id": "string", "subject": "string",
            #     "performance_level": "float", "learning_style": "string"
            # }
            self._user_learning_collection = self._get_or_create_collection(USER_LEARNING_COLLECTION_NAME)
        return self._user_learning_collection

    def add_documents(
        self,
        collection_name: str,
        embeddings: List[List[float]], # List of embedding vectors
        documents: Optional[List[str]] = None, # Optional: text content of documents
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: List[str] = None # Unique IDs for each document
    ):
        if collection_name == QUESTIONS_COLLECTION_NAME:
            collection = self.questions_collection
        elif collection_name == USER_LEARNING_COLLECTION_NAME:
            collection = self.user_learning_collection
        else:
            raise ValueError(f"Unknown collection name: {collection_name}")

        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_collection(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None, # For filtering metadata, e.g., {"subject": "Math"}
        where_document: Optional[Dict[str, Any]] = None, # For filtering based on document content (e.g., $contains)
        include: Optional[List[str]] = None # e.g., ["metadatas", "documents", "distances"]
    ) -> Dict[str, Any]: # Chroma query results structure
        if collection_name == QUESTIONS_COLLECTION_NAME:
            collection = self.questions_collection
        elif collection_name == USER_LEARNING_COLLECTION_NAME:
            collection = self.user_learning_collection
        else:
            raise ValueError(f"Unknown collection name: {collection_name}")

        if include is None:
            include = ["metadatas", "documents", "distances"]

        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include
        )
        return results

    def get_document_by_id(self, collection_name: str, doc_id: Union[str, List[str]], include: Optional[List[str]] = None):
        if collection_name == QUESTIONS_COLLECTION_NAME:
            collection = self.questions_collection
        elif collection_name == USER_LEARNING_COLLECTION_NAME:
            collection = self.user_learning_collection
        else:
            raise ValueError(f"Unknown collection name: {collection_name}")

        if include is None:
            include = ["metadatas", "documents"]

        return collection.get(ids=doc_id if isinstance(doc_id, list) else [doc_id], include=include)

    def update_document(self, collection_name: str, doc_id: str, embedding: Optional[List[float]] = None, metadata: Optional[Dict[str, Any]] = None, document: Optional[str] = None):
        if collection_name == QUESTIONS_COLLECTION_NAME:
            collection = self.questions_collection
        elif collection_name == USER_LEARNING_COLLECTION_NAME:
            collection = self.user_learning_collection
        else:
            raise ValueError(f"Unknown collection name: {collection_name}")

        update_args = {"ids": [doc_id]}
        if embedding:
            update_args["embeddings"] = [embedding]
        if metadata:
            update_args["metadatas"] = [metadata]
        if document:
            update_args["documents"] = [document]

        if len(update_args) > 1: # Need at least one field to update besides id
            collection.update(**update_args)


    def delete_documents(self, collection_name: str, ids: List[str]):
        if collection_name == QUESTIONS_COLLECTION_NAME:
            collection = self.questions_collection
        elif collection_name == USER_LEARNING_COLLECTION_NAME:
            collection = self.user_learning_collection
        else:
            raise ValueError(f"Unknown collection name: {collection_name}")

        collection.delete(ids=ids)

    def count(self, collection_name: str) -> int:
        if collection_name == QUESTIONS_COLLECTION_NAME:
            return self.questions_collection.count()
        elif collection_name == USER_LEARNING_COLLECTION_NAME:
            return self.user_learning_collection.count()
        raise ValueError(f"Unknown collection name: {collection_name}")

# Example instantiation (could be a singleton or managed by DI)
# chroma_client = ChromaDBClient() # Defaults to persistent local storage in ./chroma_data
# chroma_client_http = ChromaDBClient(host="localhost", port=8000) # For remote server
# chroma_client_memory = ChromaDBClient(in_memory=True) # For testing or temp use
