import networkx as nx
import pickle
import os
from backend.utils.config import GRAPH_PATH
from backend.db.db import get_db_connection

class GraphManager:
    def __init__(self):
        self.path = GRAPH_PATH
        self.G = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                return pickle.load(f)
        else:
            return nx.Graph()

    def save(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.G, f)

    def update_co_occurrence(self, cluster_ids: list):
        """
        Takes a list of cluster IDs found in a single image and 
        updates the CO_APPEARS edges between them.
        """
        if len(cluster_ids) < 2:
            return

        # Add nodes if they don't exist
        for cid in cluster_ids:
            if not self.G.has_node(cid):
                self.G.add_node(cid, type='person')

        # Add or update edges (co-occurrence)
        import itertools
        for id_a, id_b in itertools.combinations(cluster_ids, 2):
            if self.G.has_edge(id_a, id_b):
                self.G[id_a][id_b]['weight'] += 1
            else:
                self.G.add_edge(id_a, id_b, weight=1, relation='CO_APPEARS')
        
        self.save()

    def get_full_graph_json(self):
        """Returns the graph in a format suitable for D3.js."""
        data = {
            "nodes": [],
            "links": []
        }
        
        # Get labels from DB for nodes
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, label FROM clusters")
        labels = {row['id']: row['label'] or f"Person {row['id']}" for row in cursor.fetchall()}
        conn.close()

        for node in self.G.nodes():
            data["nodes"].append({
                "id": node,
                "label": labels.get(node, f"Unknown {node}")
            })
            
        for u, v, attrs in self.G.edges(data=True):
            data["links"].append({
                "source": u,
                "target": v,
                "weight": attrs.get('weight', 1)
            })
            
        return data

# Global instance
graph_manager = GraphManager()
