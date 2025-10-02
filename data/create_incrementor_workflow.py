#!/usr/bin/env python3
"""
Script to create a workflow with N incrementor commands starting from 42.
This creates a linear chain of incrementor nodes that each increment the value by 1.

Usage:
    python create_incrementor_workflow.py <N> [start_value]
    
    N: Number of incrementor commands to create
    start_value: Starting value (default: 42)

Examples:
    python create_incrementor_workflow.py 3
    python create_incrementor_workflow.py 5 100
    
The script creates:
1. A workflow with the specified number of incrementor commands
2. A constant node that provides the starting value
3. Sequential connections: StartValue -> Incrementor1 -> Incrementor2 -> ... -> IncrementorN

Each incrementor command runs the commands/incrementor.py script which increments the input value by 1.
"""

import sqlite3
import json
import sys
from typing import List, Tuple


class WorkflowCreator:
    """Creates workflows in the AI8N database."""
    
    def __init__(self, db_path: str = "./ai8n.db"):
        self.db_path = db_path
    
    def get_db_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def create_workflow(self, name: str) -> int:
        """Create a new workflow and return its ID."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Workflows (name, active) VALUES (?, ?)",
                (name, 1)
            )
            return cursor.lastrowid
    
    def create_incrementor_nodes(self, workflow_id: int, n: int, start_value: int = 42) -> List[int]:
        """Create N incrementor command nodes and return their IDs."""
        node_ids = []
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            for i in range(n):
                # Create parameters for the incrementor command
                parameters = {
                    "command": "python3 commands/incrementor.py",
                    "working_dir": "."
                }
                
                # Create the node
                cursor.execute("""
                    INSERT INTO Node (workflow_id, name, type, parameters, position)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    workflow_id,
                    f"Incrementor{i+1}",
                    "Command",
                    json.dumps(parameters),
                    json.dumps({"x": 100 + i * 200, "y": 100})
                ))
                
                node_ids.append(cursor.lastrowid)
        
        return node_ids
    
    def create_connections(self, node_ids: List[int]) -> List[int]:
        """Create connections between nodes in sequence and return connection IDs."""
        connection_ids = []
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Connect nodes in sequence: node1 -> node2 -> node3 -> ...
            for i in range(len(node_ids) - 1):
                cursor.execute("""
                    INSERT INTO Connections (from_node_id, to_node_id)
                    VALUES (?, ?)
                """, (node_ids[i], node_ids[i + 1]))
                
                connection_ids.append(cursor.lastrowid)
        
        return connection_ids
    
    def create_initial_constant_node(self, workflow_id: int, start_value: int) -> int:
        """Create an initial constant node with the starting value."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            parameters = {"value": start_value}
            
            cursor.execute("""
                INSERT INTO Node (workflow_id, name, type, parameters, position)
                VALUES (?, ?, ?, ?, ?)
            """, (
                workflow_id,
                "StartValue",
                "Constant",
                json.dumps(parameters),
                json.dumps({"x": 50, "y": 100})
            ))
            
            return cursor.lastrowid
    
    def create_incrementor_workflow(self, n: int, start_value: int = 42) -> Tuple[int, List[int], List[int]]:
        """Create a complete incrementor workflow with N incrementor commands."""
        print(f"Creating incrementor workflow with {n} incrementor commands starting from {start_value}")
        
        # Create the workflow
        workflow_id = self.create_workflow(f"Incrementor Workflow ({n} steps)")
        print(f"Created workflow with ID: {workflow_id}")
        
        # Create initial constant node
        start_node_id = self.create_initial_constant_node(workflow_id, start_value)
        print(f"Created start constant node with ID: {start_node_id}")
        
        # Create incrementor nodes
        incrementor_node_ids = self.create_incrementor_nodes(workflow_id, n, start_value)
        print(f"Created {len(incrementor_node_ids)} incrementor nodes: {incrementor_node_ids}")
        
        # Create connections: start -> incrementor1 -> incrementor2 -> ...
        all_node_ids = [start_node_id] + incrementor_node_ids
        connection_ids = self.create_connections(all_node_ids)
        print(f"Created {len(connection_ids)} connections: {connection_ids}")
        
        return workflow_id, all_node_ids, connection_ids
    
    def verify_workflow(self, workflow_id: int):
        """Verify the created workflow by printing its structure."""
        with self.get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get workflow info
            cursor.execute("SELECT * FROM Workflows WHERE id = ?", (workflow_id,))
            workflow = cursor.fetchone()
            print(f"\nWorkflow: {dict(workflow)}")
            
            # Get nodes
            cursor.execute("SELECT * FROM Node WHERE workflow_id = ? ORDER BY id", (workflow_id,))
            nodes = [dict(row) for row in cursor.fetchall()]
            print(f"\nNodes ({len(nodes)}):")
            for node in nodes:
                print(f"  {node['id']}: {node['name']} ({node['type']}) - {node['parameters']}")
            
            # Get connections
            cursor.execute("""
                SELECT c.*, n1.name as from_node_name, n2.name as to_node_name
                FROM Connections c
                JOIN Node n1 ON c.from_node_id = n1.id
                JOIN Node n2 ON c.to_node_id = n2.id
                WHERE n1.workflow_id = ?
                ORDER BY c.id
            """, (workflow_id,))
            connections = [dict(row) for row in cursor.fetchall()]
            print(f"\nConnections ({len(connections)}):")
            for conn in connections:
                print(f"  {conn['from_node_name']} -> {conn['to_node_name']}")


def main():
    """Main function to create the incrementor workflow."""
    if len(sys.argv) < 2:
        print("Usage: python create_incrementor_workflow.py <N> [start_value]")
        print("  N: Number of incrementor commands to create")
        print("  start_value: Starting value (default: 42)")
        print("\nExamples:")
        print("  python create_incrementor_workflow.py 3")
        print("  python create_incrementor_workflow.py 5 100")
        print("  python create_incrementor_workflow.py --help")
        sys.exit(1)
    
    if sys.argv[1] in ['-h', '--help']:
        print("Usage: python create_incrementor_workflow.py <N> [start_value]")
        print("  N: Number of incrementor commands to create")
        print("  start_value: Starting value (default: 42)")
        print("\nExamples:")
        print("  python create_incrementor_workflow.py 3")
        print("  python create_incrementor_workflow.py 5 100")
        print("  python create_incrementor_workflow.py --help")
        sys.exit(0)
    
    try:
        n = int(sys.argv[1])
        start_value = int(sys.argv[2]) if len(sys.argv) > 2 else 42
        
        if n <= 0:
            print("Error: N must be a positive integer")
            sys.exit(1)
        
        creator = WorkflowCreator()
        workflow_id, node_ids, connection_ids = creator.create_incrementor_workflow(n, start_value)
        
        print(f"\n✅ Successfully created workflow {workflow_id} with {n} incrementor commands!")
        
        # Verify the workflow
        creator.verify_workflow(workflow_id)
        
        print(f"\nTo run this workflow, use:")
        print(f"python -c \"from model.run_workflow import run_workflow; print(run_workflow({workflow_id}, {{'value': {start_value}}}))\"")
        
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
