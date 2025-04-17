# users/arango/document_ops.py
from users.arangodb import db
import logging

logger = logging.getLogger(__name__)

class DocumentManager:
    @staticmethod
    def create(collection_name, document):
        """Create a document in a collection."""
        try:
            collection = db.collection(collection_name)
            meta = collection.insert(document, return_new=True)
            return meta.get('new')
        except Exception as e:
            logger.error(f"Error creating document in {collection_name}: {str(e)}")
            raise

    @staticmethod
    def get(collection_name, document_key):
        """Retrieve a document by key."""
        try:
            collection = db.collection(collection_name)
            return collection.get(document_key)
        except Exception as e:
            logger.error(f"Error retrieving document {document_key}: {str(e)}")
            return None

    @staticmethod
    def update(collection_name, document_key, document):
        """Update a document."""
        try:
            collection = db.collection(collection_name)
            meta = collection.update(document_key, document, return_new=True)
            return meta.get('new')
        except Exception as e:
            logger.error(f"Error updating document {document_key}: {str(e)}")
            raise

    @staticmethod
    def delete(collection_name, document_key):
        """Delete a document."""
        try:
            collection = db.collection(collection_name)
            collection.delete(document_key)
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_key}: {str(e)}")
            raise

    @staticmethod
    def query(aql_query, bind_vars=None):
        """Execute a custom AQL query."""
        try:
            cursor = db.aql.execute(aql_query, bind_vars=bind_vars or {})
            return [doc for doc in cursor]
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
