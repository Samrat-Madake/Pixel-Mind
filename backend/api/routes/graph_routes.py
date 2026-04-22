from fastapi import APIRouter, HTTPException
from backend.graph.graph_manager import graph_manager
from backend.db.db import get_db_connection

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/")
async def get_full_graph():
    """Returns the full relationship graph for D3.js."""
    return graph_manager.get_full_graph_json()

@router.get("/{cluster_id}")
async def get_ego_graph(cluster_id: int):
    """Returns connections for a specific person (ego network)."""
    if not graph_manager.G.has_node(cluster_id):
        raise HTTPException(status_code=404, detail="Person not found in graph")
        
    edges = graph_manager.G.edges(cluster_id, data=True)
    
    # We need to get the labels for the connected nodes
    connected_nodes = set([cluster_id])
    for u, v, d in edges:
        connected_nodes.add(u)
        connected_nodes.add(v)
        
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(connected_nodes))
    cursor.execute(f"SELECT id, label FROM clusters WHERE id IN ({placeholders})", list(connected_nodes))
    labels = {row["id"]: row["label"] or f"Person {row['id']}" for row in cursor.fetchall()}
    conn.close()
    
    data = {"nodes": [], "links": []}
    for n in connected_nodes:
        data["nodes"].append({"id": n, "label": labels.get(n, f"Person {n}")})
        
    for u, v, d in edges:
        data["links"].append({"source": u, "target": v, "weight": d.get("weight", 1)})
        
    return data
