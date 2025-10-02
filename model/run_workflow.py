import sqlite3
import json
import logging
import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowExecutor:
    """Executes workflows by traversing the DAG of nodes."""
    
    def __init__(self, db_path: str = "data/ai8n.db"):
        self.db_path = db_path
    
    def get_db_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def fetch_workflow(self, workflow_id: int) -> Optional[Dict[str, Any]]:
        """Fetch workflow details from the database."""
        with self.get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch workflow
            cursor.execute("SELECT * FROM Workflows WHERE id = ?", (workflow_id,))
            workflow = cursor.fetchone()
            if not workflow:
                logger.error(f"Workflow {workflow_id} not found")
                return None
            
            # Fetch nodes
            cursor.execute("SELECT * FROM Node WHERE workflow_id = ? ORDER BY id", (workflow_id,))
            nodes = [dict(row) for row in cursor.fetchall()]
            
            # Fetch connections
            cursor.execute("""
                SELECT c.*, 
                       n1.name as from_node_name, 
                       n2.name as to_node_name
                FROM Connections c
                JOIN Node n1 ON c.from_node_id = n1.id
                JOIN Node n2 ON c.to_node_id = n2.id
                WHERE n1.workflow_id = ?
            """, (workflow_id,))
            connections = [dict(row) for row in cursor.fetchall()]
            
            return {
                'workflow': dict(workflow),
                'nodes': nodes,
                'connections': connections
            }
    
    def build_dag(self, nodes: List[Dict], connections: List[Dict]) -> Tuple[Dict[int, List[int]], Dict[int, int]]:
        """Build adjacency list and in-degree count for DAG traversal."""
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize in-degree for all nodes
        for node in nodes:
            in_degree[node['id']] = 0
        
        # Build graph and calculate in-degrees
        for conn in connections:
            from_id = conn['from_node_id']
            to_id = conn['to_node_id']
            graph[from_id].append(to_id)
            in_degree[to_id] += 1
        
        return dict(graph), dict(in_degree)
    
    def find_root_nodes(self, nodes: List[Dict], in_degree: Dict[int, int]) -> List[Dict]:
        """Find root nodes (nodes with in-degree 0)."""
        root_nodes = []
        for node in nodes:
            if in_degree.get(node['id'], 0) == 0:
                root_nodes.append(node)
        return root_nodes
    
    def execute_node(self, node: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single node based on its type."""
        node_type = node['type']
        parameters = json.loads(node['parameters']) if node['parameters'] else {}
        
        logger.info(f"Executing node {node['name']} (type: {node_type})")
        
        try:
            if node_type == 'Trigger':
                return self.execute_trigger_node(node, input_data, parameters)
            elif node_type == 'Command':
                return self.execute_command_node(node, input_data, parameters)
            elif node_type == 'Constant':
                return self.execute_constant_node(node, input_data, parameters)
            elif node_type == 'LLM':
                return self.execute_llm_node(node, input_data, parameters)
            elif node_type == 'Conditional':
                return self.execute_conditional_node(node, input_data, parameters)
            elif node_type == 'Manual':
                return self.execute_manual_node(node, input_data, parameters)
            else:
                raise ValueError(f"Unknown node type: {node_type}")
        except Exception as e:
            logger.error(f"Error executing node {node['name']}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'output': None
            }
    
    # Placeholder node execution functions
    def execute_trigger_node(self, node: Dict[str, Any], input_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trigger node - typically the entry point of a workflow."""
        logger.info(f"Executing trigger node: {node['name']}")
        # Placeholder implementation
        return {
            'success': True,
            'output': input_data,
            'message': f"Trigger node {node['name']} executed successfully"
        }
    
    def execute_command_node(self, node: Dict[str, Any], input_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command node - runs external commands or scripts."""
        logger.info(f"Executing command node: {node['name']}")

        # Serialize input_data as a JSON string and add it to the command
        input_json = json.dumps(input_data)
        command = parameters['command']
        working_dir = parameters.get('working_dir', '.')
        
        # Add the serialized input as an environment variable INPUT_DATA
        env = os.environ.copy()
        env['INPUT_DATA'] = input_json
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env, cwd=working_dir)

        if result.returncode != 0:
            return {
                'success': False,
                'error': result.stderr,
            }

        return {
            'success': True,
            'output': result.stdout,
            'message': f"Command node {node['name']} executed successfully"
        }
    
    def execute_constant_node(self, node: Dict[str, Any], input_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a constant node - returns a constant value."""
        logger.info(f"Executing constant node: {node['name']}")

        return {
            'success': True,
            'output': parameters,
            'message': f"Constant node {node['name']} executed successfully"
        }
    
    def execute_llm_node(self, node: Dict[str, Any], input_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an LLM node - calls language model APIs."""
        logger.info(f"Executing LLM node: {node['name']}")
        # Placeholder implementation
        return {
            'success': True,
            'output': input_data,
            'message': f"LLM node {node['name']} executed successfully"
        }
    
    def execute_conditional_node(self, node: Dict[str, Any], input_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a conditional node - makes branching decisions."""
        logger.info(f"Executing conditional node: {node['name']}")
        # Placeholder implementation
        return {
            'success': True,
            'output': input_data,
            'message': f"Conditional node {node['name']} executed successfully"
        }
    
    def execute_manual_node(self, node: Dict[str, Any], input_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a manual node - requires human intervention."""
        logger.info(f"Executing manual node: {node['name']}")
        # Placeholder implementation
        return {
            'success': True,
            'output': input_data,
            'message': f"Manual node {node['name']} executed successfully"
        }
    
    def create_execution_record(self, workflow_id: int, node_id: int, run_index: int, status: str, input_data: Dict[str, Any] = None, output_data: Dict[str, Any] = None, error: str = None) -> int:
        """Create an execution record for a specific node in the database."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Executions (workflow_id, node_id, run_index, status, input, output, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (workflow_id, node_id, run_index, status, 
                  json.dumps(input_data) if input_data else None,
                  json.dumps(output_data) if output_data else None, 
                  error))
            return cursor.lastrowid
    
    def update_execution_record(self, execution_id: int, status: str, output_data: Dict[str, Any] = None, error: str = None):
        """Update an execution record in the database."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Executions 
                SET status = ?, output = ?, error = ?, ended_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, json.dumps(output_data) if output_data else None, error, execution_id))
    
    def get_next_run_index(self, workflow_id: int, node_id: int) -> int:
        """Get the next run index for a node in a workflow."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(MAX(run_index), 0) + 1 
                FROM Executions 
                WHERE workflow_id = ? AND node_id = ?
            """, (workflow_id, node_id))
            result = cursor.fetchone()
            return result[0] if result else 1
    
    def run_workflow(self, workflow_id: int, initial_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main function to run a workflow."""
        logger.info(f"Starting workflow execution for workflow_id: {workflow_id}")
        
        # No longer create a single workflow-level execution record
        # Each node will have its own execution record
        
        try:
            # Fetch workflow details
            workflow_data = self.fetch_workflow(workflow_id)
            if not workflow_data:
                error_msg = f"Workflow {workflow_id} not found"
                return {'success': False, 'error': error_msg}
            
            workflow = workflow_data['workflow']
            nodes = workflow_data['nodes']
            connections = workflow_data['connections']
            
            if not nodes:
                error_msg = f"No nodes found for workflow {workflow_id}"
                return {'success': False, 'error': error_msg}
            
            # Build DAG
            graph, in_degree = self.build_dag(nodes, connections)
            
            # Find root nodes
            root_nodes = self.find_root_nodes(nodes, in_degree)
            if not root_nodes:
                error_msg = f"No root nodes found for workflow {workflow_id}"
                return {'success': False, 'error': error_msg}
            
            # Create node lookup
            node_lookup = {node['id']: node for node in nodes}
            
            # Execute workflow using topological sort
            execution_results = {}
            queue = deque(root_nodes)
            completed_nodes = set()
            node_execution_ids = {}  # Track execution IDs for each node
            
            # Initialize with root nodes
            for root_node in root_nodes:
                # Get run index for this node
                run_index = self.get_next_run_index(workflow_id, root_node['id'])
                
                # Create execution record for this node
                execution_id = self.create_execution_record(
                    workflow_id, root_node['id'], run_index, "running", 
                    initial_input or {}
                )
                node_execution_ids[root_node['id']] = execution_id
                
                # Execute the node
                result = self.execute_node(root_node, initial_input or {})
                execution_results[root_node['id']] = result
                completed_nodes.add(root_node['id'])
                
                # Update execution record with result
                if result['success']:
                    self.update_execution_record(execution_id, "completed", result['output'])
                else:
                    self.update_execution_record(execution_id, "failed", error=result.get('error'))
                
                # Add connected nodes to queue if their dependencies are met
                for next_node_id in graph.get(root_node['id'], []):
                    if next_node_id not in completed_nodes:
                        queue.append(node_lookup[next_node_id])
            
            # Process remaining nodes
            while queue:
                current_node = queue.popleft()
                
                if current_node['id'] in completed_nodes:
                    continue
                
                # Check if all dependencies are completed
                dependencies_met = True
                for conn in connections:
                    if conn['to_node_id'] == current_node['id']:
                        if conn['from_node_id'] not in completed_nodes:
                            dependencies_met = False
                            break
                
                if not dependencies_met:
                    # Re-queue for later processing
                    queue.append(current_node)
                    continue
                
                # Get input data from previous nodes
                input_data = {}
                for conn in connections:
                    if conn['to_node_id'] == current_node['id']:
                        prev_node_id = conn['from_node_id']
                        if prev_node_id in execution_results:
                            prev_result = execution_results[prev_node_id]
                            if prev_result['success']:
                                output = prev_result.get('output', {})
                                # If output is a string (from command nodes), try to parse as JSON
                                if isinstance(output, str):
                                    try:
                                        output = json.loads(output)
                                    except json.JSONDecodeError:
                                        # If not valid JSON, wrap in a dict
                                        output = {'raw_output': output}
                                elif not isinstance(output, dict):
                                    # If not a dict, wrap it
                                    output = {'value': output}
                                input_data.update(output)
                
                # Get run index for this node
                run_index = self.get_next_run_index(workflow_id, current_node['id'])
                
                # Create execution record for this node
                execution_id = self.create_execution_record(
                    workflow_id, current_node['id'], run_index, "running", 
                    input_data
                )
                node_execution_ids[current_node['id']] = execution_id
                
                # Execute current node
                result = self.execute_node(current_node, input_data)
                execution_results[current_node['id']] = result
                completed_nodes.add(current_node['id'])
                
                # Update execution record with result
                if result['success']:
                    self.update_execution_record(execution_id, "completed", result['output'])
                else:
                    self.update_execution_record(execution_id, "failed", error=result.get('error'))
                
                # Add connected nodes to queue
                for next_node_id in graph.get(current_node['id'], []):
                    if next_node_id not in completed_nodes:
                        queue.append(node_lookup[next_node_id])
            
            # Check if all nodes were executed
            if len(completed_nodes) != len(nodes):
                error_msg = f"Not all nodes could be executed. Completed: {len(completed_nodes)}, Total: {len(nodes)}"
                return {'success': False, 'error': error_msg}
            
            logger.info(f"Workflow {workflow_id} executed successfully")
            return {
                'success': True,
                'execution_ids': node_execution_ids,
                'results': execution_results,
                'message': f"Workflow {workflow['name']} executed successfully"
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during workflow execution: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}


def run_workflow(workflow_id: int, initial_input: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main function to run a workflow by its ID.
    
    Args:
        workflow_id: The ID of the workflow to execute
        initial_input: Optional initial input data for the workflow
    
    Returns:
        Dictionary containing execution results and status
    """
    executor = WorkflowExecutor()
    return executor.run_workflow(workflow_id, initial_input)


if __name__ == "__main__":
    # Example usage
    result = run_workflow(1, {"test": "data"})
    print(json.dumps(result, indent=2))
