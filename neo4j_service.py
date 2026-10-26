from __future__ import annotations
from typing import Any
import streamlit as st
from neo4j import GraphDatabase, RoutingControl

# ------------------------------------------------------------------ ข้อมูลตัวอย่าง
PERSONS = ["Ing", "Somying", "Natee", "Mana", "Wichai", "On", "Beam", "Non", "Games", "Palm"]

COMPUTERS = [
    {"name": "Dell XPS 13", "brand": "Dell", "category": "Ultrabook", "price": 42900},
    {"name": "HP Spectre x360", "brand": "HP", "category": "2-in-1", "price": 48900},
    {"name": "Lenovo ThinkPad X1 Carbon", "brand": "Lenovo", "category": "Business", "price": 55900},
    {"name": "Apple MacBook Pro", "brand": "Apple", "category": "Ultrabook", "price": 69900},
    {"name": "ASUS ROG Zephyrus G14", "brand": "ASUS", "category": "Gaming", "price": 52900},
    {"name": "Acer Swift 3", "brand": "Acer", "category": "Ultrabook", "price": 25900},
    {"name": "MSI Prestige 14", "brand": "MSI", "category": "Creator", "price": 39900},
    {"name": "Microsoft Surface Laptop 5", "brand": "Microsoft", "category": "Ultrabook", "price": 44900},
    {"name": "Samsung Galaxy Book3", "brand": "Samsung", "category": "Ultrabook", "price": 38900},
    {"name": "Razer Blade 15", "brand": "Razer", "category": "Gaming", "price": 79900},
]

COMPUTER_NAMES = [c["name"] for c in COMPUTERS]

LIKES = [
    ("Ing", "Dell XPS 13"), ("Ing", "HP Spectre x360"), ("Ing", "Lenovo ThinkPad X1 Carbon"),
    ("Somying", "Dell XPS 13"), ("Somying", "HP Spectre x360"), ("Somying", "Apple MacBook Pro"), ("Somying", "ASUS ROG Zephyrus G14"),
    ("Natee", "Dell XPS 13"), ("Natee", "Apple MacBook Pro"), ("Natee", "Acer Swift 3"),
    ("Mana", "ASUS ROG Zephyrus G14"), ("Mana", "Acer Swift 3"), ("Mana", "MSI Prestige 14"),
    ("Wichai", "HP Spectre x360"), ("Wichai", "Apple MacBook Pro"), ("Wichai", "Samsung Galaxy Book3"),
    ("On", "Dell XPS 13"), ("On", "Microsoft Surface Laptop 5"), ("On", "Lenovo ThinkPad X1 Carbon"),
    ("Beam", "Apple MacBook Pro"), ("Beam", "Acer Swift 3"), ("Beam", "Lenovo ThinkPad X1 Carbon"),
    ("Non", "ASUS ROG Zephyrus G14"), ("Non", "MSI Prestige 14"), ("Non", "Samsung Galaxy Book3"),
    ("Games", "Samsung Galaxy Book3"), ("Games", "Razer Blade 15"), ("Games", "Apple MacBook Pro"),
    ("Palm", "Microsoft Surface Laptop 5"), ("Palm", "Dell XPS 13"), ("Palm", "HP Spectre x360")
]

# Cypher Query สำหรับ Collaborative Filtering
RECOMMEND_CYPHER = """
MATCH (t:Person {name: $name})
MATCH (rec:Computer)
WHERE NOT (t)-[:LIKES]->(rec)
OPTIONAL MATCH (t)-[:LIKES]->(c:Computer)<-[:LIKES]-(o:Person)-[:LIKES]->(rec)
WHERE o <> t
WITH rec, count(DISTINCT o) AS similar_voters, collect(DISTINCT o.name) AS similar_names
WITH rec, similar_voters, similar_names,
     similar_voters * $sim_weight AS score
WHERE score > 0
RETURN rec.name AS computer, rec.brand AS brand, rec.category AS category, rec.price AS price,
       score, similar_voters, similar_names,
       COUNT { (rec)<-[:LIKES]-() } AS popularity
ORDER BY score DESC, popularity DESC, computer
LIMIT $limit
"""

# ------------------------------------------------------------------ Connection
def _config() -> tuple[str, str, str, str | None]:
    cfg = st.secrets["neo4j"]
    return cfg["uri"], cfg["username"], cfg["password"], cfg.get("database") or None

@st.cache_resource(show_spinner=False)
def get_driver():
    uri, username, password, _ = _config()
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    return driver

def query(cypher: str, parameters: dict[str, Any] | None = None, *, write: bool = False) -> list[dict[str, Any]]:
    _, _, _, database = _config()
    records, _, _ = get_driver().execute_query(
        cypher,
        parameters_=parameters or {},
        database_=database,
        routing_=RoutingControl.WRITE if write else RoutingControl.READ,
    )
    return [r.data() for r in records]

def ping() -> bool:
    rows = query("RETURN 1 AS ok")
    return bool(rows and rows[0]["ok"] == 1)

# ------------------------------------------------------------------ Setup
def create_schema() -> None:
    for stmt in (
        "CREATE CONSTRAINT person_name_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
        "CREATE CONSTRAINT computer_name_unique IF NOT EXISTS FOR (c:Computer) REQUIRE c.name IS UNIQUE",
    ):
        query(stmt, write=True)

def seed_demo_data() -> None:
    create_schema()
    query("UNWIND $rows AS n MERGE (:Person {name: n})", {"rows": PERSONS}, write=True)
    
    # Merge computers with properties
    query(
        """
        UNWIND $rows AS c
        MERGE (comp:Computer {name: c.name})
        SET comp.brand = c.brand, comp.category = c.category, comp.price = c.price
        """,
        {"rows": COMPUTERS},
        write=True
    )
    
    query(
        """
        UNWIND $rows AS row
        MATCH (p:Person {name: row[0]}), (c:Computer {name: row[1]})
        MERGE (p)-[:LIKES]->(c)
        """,
        {"rows": LIKES},
        write=True,
    )

def clear_graph_data() -> None:
    query("MATCH (n) WHERE n:Person OR n:Computer DETACH DELETE n", write=True)

def add_person(name: str) -> None:
    query("MERGE (:Person {name: $name})", {"name": name}, write=True)

def add_computer(name: str, brand: str, category: str, price: int) -> None:
    query(
        "MERGE (c:Computer {name: $name}) SET c.brand = $brand, c.category = $category, c.price = $price",
        {"name": name, "brand": brand, "category": category, "price": price},
        write=True
    )

# ------------------------------------------------------------------ Reads
def get_people() -> list[str]:
    return [r["name"] for r in query("MATCH (p:Person) RETURN p.name AS name ORDER BY name")]

def get_computers() -> list[str]:
    return [r["name"] for r in query("MATCH (c:Computer) RETURN c.name AS name ORDER BY name")]

def get_metrics() -> dict[str, int]:
    rows = query(
        """
        RETURN COUNT { (:Person) } AS persons,
               COUNT { (:Computer) } AS computers,
               COUNT { (:Person)-[:LIKES]->(:Computer) } AS likes
        """
    )
    return rows[0] if rows else {"persons": 0, "computers": 0, "likes": 0}

def top_computers(limit: int = 10) -> list[dict[str, Any]]:
    return query(
        """
        MATCH (c:Computer)
        RETURN c.name AS computer, c.brand AS brand, c.category AS category, c.price AS price, COUNT { (c)<-[:LIKES]-() } AS likes
        ORDER BY likes DESC, computer
        LIMIT $limit
        """,
        {"limit": int(limit)},
    )

def get_liked(name: str) -> list[str]:
    rows = query(
        "MATCH (:Person {name: $name})-[:LIKES]->(c:Computer) RETURN c.name AS computer ORDER BY computer",
        {"name": name},
    )
    return [r["computer"] for r in rows]

def similar_people(name: str, limit: int = 10) -> list[dict[str, Any]]:
    rows = query(
        """
        MATCH (t:Person {name: $name})-[:LIKES]->(c:Computer)<-[:LIKES]-(o:Person)
        WHERE o <> t
        RETURN o.name AS person, count(c) AS shared, collect(c.name) AS shared_computers
        ORDER BY shared DESC, person
        LIMIT $limit
        """,
        {"name": name, "limit": int(limit)},
    )
    for r in rows:
        r["shared_computers"] = sorted(r["shared_computers"])
    return rows

def recommend_computers(name: str, limit: int = 5, sim_weight: float = 1.0) -> list[dict[str, Any]]:
    rows = query(
        RECOMMEND_CYPHER,
        {"name": name, "limit": int(limit), "sim_weight": float(sim_weight)},
    )
    for r in rows:
        r["similar_names"] = sorted(r["similar_names"])
    return rows

def popular_fallback(name: str, limit: int = 5) -> list[dict[str, Any]]:
    return query(
        """
        MATCH (c:Computer)
        WHERE NOT EXISTS { MATCH (:Person {name: $name})-[:LIKES]->(c) }
        RETURN c.name AS computer, c.brand AS brand, c.category AS category, c.price AS price, COUNT { (c)<-[:LIKES]-() } AS likes
        ORDER BY likes DESC, computer
        LIMIT $limit
        """,
        {"name": name, "limit": int(limit)},
    )

def graph_edges(name: str) -> list[dict[str, Any]]:
    return query(
        """
        MATCH (t:Person {name: $name})
        OPTIONAL MATCH (t)-[:LIKES]->(:Computer)<-[:LIKES]-(o:Person)
        WHERE o <> t
        WITH t, collect(DISTINCT o) AS similar
        UNWIND ([t] + similar) AS p
        MATCH (p)-[:LIKES]->(c:Computer)
        RETURN DISTINCT p.name AS person, c.name AS computer, c.brand AS brand, c.category AS category, c.price AS price
        """,
        {"name": name},
    )

# ------------------------------------------------------------------ Writes
def set_likes(name: str, computers: list[str]) -> None:
    query(
        """
        MATCH (p:Person {name: $name})-[r:LIKES]->(c:Computer)
        WHERE NOT c.name IN $computers
        DELETE r
        """,
        {"name": name, "computers": computers},
        write=True,
    )
    query(
        """
        MATCH (p:Person {name: $name})
        UNWIND $computers AS cn
        MATCH (c:Computer {name: cn})
        MERGE (p)-[:LIKES]->(c)
        """,
        {"name": name, "computers": computers},
        write=True,
    )