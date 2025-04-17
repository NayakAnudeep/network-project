# users/arango/edge_ops.py
from users.arangodb import db
import logging

logger = logging.getLogger(__name__)

class EdgeManager:
    @staticmethod
    def create(edge_collection, from_id, to_id, data=None):
        """Create an edge between two vertices."""
        try:
            if data is None:
                data = {}
            
            # Make sure IDs are in the correct format
            if '/' not in from_id:
                from_collection = from_id.split('_')[0] if '_' in from_id else 'Submissions'
                from_id = f"{from_collection}/{from_id}"
            
            if '/' not in to_id:
                to_collection = to_id.split('_')[0] if '_' in to_id else 'Mistakes'
                to_id = f"{to_collection}/{to_id}"
            
            edge = {
                '_from': from_id,
                '_to': to_id,
                **data
            }
            
            collection = db.collection(edge_collection)
            meta = collection.insert(edge, return_new=True)
            return meta.get('new')
        except Exception as e:
            logger.error(f"Error creating edge in {edge_collection}: {str(e)}")
            raise

    @staticmethod
    def get_connections(start_vertex_id, direction="outbound", edge_collection=None, depth=1):
        """Get connections from/to a vertex."""
        try:
            graph = db.graph('ai_ta_graph')
            
            traverse_options = {
                "direction": direction,
                "startVertex": start_vertex_id,
                "maxDepth": depth,
                "vertexCollections": [],
                "edgeCollections": [edge_collection] if edge_collection else []
            }
            
            result = graph.traverse(**traverse_options)
            return result
        except Exception as e:
            logger.error(f"Error getting connections for {start_vertex_id}: {str(e)}")
            raise

    @staticmethod
    def delete_edge(edge_collection, edge_key):
        """Delete an edge by key."""
        try:
            collection = db.collection(edge_collection)
            collection.delete(edge_key)
            return True
        except Exception as e:
            logger.error(f"Error deleting edge {edge_key}: {str(e)}")
            raise
