import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.graph.graph_manager import graph_manager
from backend.db.db import get_db_connection

def rebuild_graph():
    print("--- Rebuilding Relationship Graph ---")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Get all images that have more than one person
    cursor.execute("""
        SELECT image_id, GROUP_CONCAT(cluster_id) as cluster_list
        FROM faces
        WHERE cluster_id IS NOT NULL AND cluster_id > 0
        GROUP BY image_id
        HAVING COUNT(cluster_id) > 1
    """)
    
    rows = cursor.fetchall()
    print(f"Found {len(rows)} images with multiple people.")
    
    # Reset graph for a clean rebuild (optional, but good for sync)
    import networkx as nx
    graph_manager.G = nx.Graph()
    
    for row in rows:
        cluster_ids = [int(cid) for cid in row['cluster_list'].split(',')]
        graph_manager.update_co_occurrence(cluster_ids)
        
    print(f"Graph rebuild complete. Total nodes: {graph_manager.G.number_of_nodes()}, Total edges: {graph_manager.G.number_of_edges()}")
    conn.close()

if __name__ == "__main__":
    rebuild_graph()
