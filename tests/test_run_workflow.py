import unittest
import sqlite3
import json
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from model.run_workflow import WorkflowExecutor, run_workflow


class TestWorkflowExecutor(unittest.TestCase):
    """Test cases for WorkflowExecutor class."""
    
    def setUp(self):
        """Set up test database and executor."""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.executor = WorkflowExecutor(self.db_path)
        
        # Create test database schema
        self._create_test_database()
        
        # Sample test data
        self.workflow_id = 1
        self._insert_test_data()
    
    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_test_database(self):
        """Create test database with schema from db-setup.sql."""
        # Read the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'db-setup.sql')
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript(sql_script)
    
    def _insert_test_data(self):
        """Insert test data into database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert workflow
            cursor.execute("""
                INSERT INTO Workflows (id, name, active) VALUES (?, ?, ?)
            """, (1, "Test Workflow", 1))
            
            # Insert nodes
            nodes = [
                (1, 1, "Start", "Trigger", '{}', '{"x": 0, "y": 0}'),
                (2, 1, "Process", "Command", '{"command": "echo hello"}', '{"x": 100, "y": 0}'),
                (3, 1, "Constant", "Constant", '{"value": "test_value"}', '{"x": 200, "y": 0}'),
                (4, 1, "LLM Node", "LLM", '{"model": "gpt-3.5-turbo"}', '{"x": 300, "y": 0}'),
                (5, 1, "Conditional", "Conditional", '{"condition": "true"}', '{"x": 400, "y": 0}'),
                (6, 1, "Manual", "Manual", '{"prompt": "Please review"}', '{"x": 500, "y": 0}')
            ]
            
            cursor.executemany("""
                INSERT INTO Node (id, workflow_id, name, type, parameters, position) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, nodes)
            
            # Insert connections
            connections = [
                (1, 1, 2),  # Start -> Process
                (2, 2, 3),  # Process -> Constant
                (3, 3, 4),  # Constant -> LLM Node
                (4, 4, 5),  # LLM Node -> Conditional
                (5, 5, 6)   # Conditional -> Manual
            ]
            
            cursor.executemany("""
                INSERT INTO Connections (id, from_node_id, to_node_id) 
                VALUES (?, ?, ?)
            """, connections)
    
    def test_fetch_workflow_success(self):
        """Test successful workflow fetching."""
        result = self.executor.fetch_workflow(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['workflow']['id'], 1)
        self.assertEqual(result['workflow']['name'], "Test Workflow")
        self.assertEqual(len(result['nodes']), 6)
        self.assertEqual(len(result['connections']), 5)
    
    def test_fetch_workflow_not_found(self):
        """Test workflow not found."""
        result = self.executor.fetch_workflow(999)
        self.assertIsNone(result)
    
    def test_build_dag(self):
        """Test DAG building."""
        workflow_data = self.executor.fetch_workflow(1)
        graph, in_degree = self.executor.build_dag(workflow_data['nodes'], workflow_data['connections'])
        
        # Check graph structure
        self.assertEqual(len(graph[1]), 1)  # Node 1 connects to node 2
        self.assertEqual(graph[1][0], 2)
        
        # Check in-degree counts
        self.assertEqual(in_degree[1], 0)  # Root node
        self.assertEqual(in_degree[2], 1)  # Has one incoming connection
        self.assertEqual(in_degree[6], 1)  # Last node has one incoming connection
    
    def test_find_root_nodes(self):
        """Test finding root nodes."""
        workflow_data = self.executor.fetch_workflow(1)
        graph, in_degree = self.executor.build_dag(workflow_data['nodes'], workflow_data['connections'])
        root_nodes = self.executor.find_root_nodes(workflow_data['nodes'], in_degree)
        
        self.assertEqual(len(root_nodes), 1)
        self.assertEqual(root_nodes[0]['id'], 1)
        self.assertEqual(root_nodes[0]['name'], "Start")
    
    def test_execute_trigger_node(self):
        """Test trigger node execution."""
        node = {'id': 1, 'name': 'Test Trigger', 'type': 'Trigger', 'parameters': '{}'}
        result = self.executor.execute_trigger_node(node, {'input': 'test'}, {})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], {'input': 'test'})
        self.assertIn('Trigger node Test Trigger executed successfully', result['message'])
    
    def test_execute_command_node(self):
        """Test command node execution."""
        node = {'id': 2, 'name': 'Test Command', 'type': 'Command', 'parameters': '{"command": "echo hello"}'}
        result = self.executor.execute_command_node(node, {'input': 'test'}, {'command': 'echo hello'})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], {'input': 'test'})
        self.assertIn('Command node Test Command executed successfully', result['message'])
    
    def test_execute_constant_node(self):
        """Test constant node execution."""
        node = {'id': 3, 'name': 'Test Constant', 'type': 'Constant', 'parameters': '{"value": "test_value"}'}
        result = self.executor.execute_constant_node(node, {'input': 'test'}, {'value': 'test_value'})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], {'value': 'test_value'})
        self.assertIn('Constant node Test Constant executed successfully', result['message'])
    
    def test_execute_llm_node(self):
        """Test LLM node execution."""
        node = {'id': 4, 'name': 'Test LLM', 'type': 'LLM', 'parameters': '{"model": "gpt-3.5-turbo"}'}
        result = self.executor.execute_llm_node(node, {'input': 'test'}, {'model': 'gpt-3.5-turbo'})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], {'input': 'test'})
        self.assertIn('LLM node Test LLM executed successfully', result['message'])
    
    def test_execute_conditional_node(self):
        """Test conditional node execution."""
        node = {'id': 5, 'name': 'Test Conditional', 'type': 'Conditional', 'parameters': '{"condition": "true"}'}
        result = self.executor.execute_conditional_node(node, {'input': 'test'}, {'condition': 'true'})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], {'input': 'test'})
        self.assertIn('Conditional node Test Conditional executed successfully', result['message'])
    
    def test_execute_manual_node(self):
        """Test manual node execution."""
        node = {'id': 6, 'name': 'Test Manual', 'type': 'Manual', 'parameters': '{"prompt": "Please review"}'}
        result = self.executor.execute_manual_node(node, {'input': 'test'}, {'prompt': 'Please review'})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], {'input': 'test'})
        self.assertIn('Manual node Test Manual executed successfully', result['message'])
    
    def test_execute_node_unknown_type(self):
        """Test executing node with unknown type."""
        node = {'id': 1, 'name': 'Unknown', 'type': 'UnknownType', 'parameters': '{}'}
        result = self.executor.execute_node(node, {'input': 'test'})
        
        self.assertFalse(result['success'])
        self.assertIn('Unknown node type: UnknownType', result['error'])
        self.assertIsNone(result['output'])
    
    def test_execute_node_exception(self):
        """Test node execution with exception."""
        with patch.object(self.executor, 'execute_trigger_node', side_effect=Exception("Test error")):
            node = {'id': 1, 'name': 'Test', 'type': 'Trigger', 'parameters': '{}'}
            result = self.executor.execute_node(node, {'input': 'test'})
            
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], 'Test error')
            self.assertIsNone(result['output'])
    
    def test_create_execution_record(self):
        """Test creating execution record."""
        execution_id = self.executor.create_execution_record(1, 1, 1, "running", {"test": "input"}, {"test": "output"})
        
        self.assertIsInstance(execution_id, int)
        self.assertGreater(execution_id, 0)
        
        # Verify record was created
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Executions WHERE id = ?", (execution_id,))
            record = cursor.fetchone()
            self.assertIsNotNone(record)
            self.assertEqual(record[1], 1)  # workflow_id
            self.assertEqual(record[2], 1)  # node_id
            self.assertEqual(record[3], 1)  # run_index
            self.assertEqual(record[4], "running")  # status
    
    def test_update_execution_record(self):
        """Test updating execution record."""
        execution_id = self.executor.create_execution_record(1, 1, 1, "running", {"test": "input"})
        self.executor.update_execution_record(execution_id, "completed", {"result": "success"})
        
        # Verify record was updated
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Executions WHERE id = ?", (execution_id,))
            record = cursor.fetchone()
            self.assertEqual(record[4], "completed")  # status
            self.assertIsNotNone(record[6])  # ended_at should be set
    
    def test_get_next_run_index(self):
        """Test getting next run index for a node."""
        # First run should be 1
        run_index = self.executor.get_next_run_index(1, 1)
        self.assertEqual(run_index, 1)
        
        # Create an execution record
        self.executor.create_execution_record(1, 1, 1, "completed", {"input": "test"})
        
        # Next run should be 2
        run_index = self.executor.get_next_run_index(1, 1)
        self.assertEqual(run_index, 2)
        
        # Different node should still be 1
        run_index = self.executor.get_next_run_index(1, 2)
        self.assertEqual(run_index, 1)
    
    def test_run_workflow_success(self):
        """Test successful workflow execution."""
        result = self.executor.run_workflow(1, {"initial": "test_data"})
        
        self.assertTrue(result['success'])
        self.assertIn('execution_ids', result)
        self.assertIn('results', result)
        self.assertIn('message', result)
        self.assertEqual(len(result['results']), 6)  # All 6 nodes executed
        self.assertEqual(len(result['execution_ids']), 6)  # All 6 nodes have execution records
    
    def test_run_workflow_not_found(self):
        """Test workflow not found."""
        result = self.executor.run_workflow(999)
        
        self.assertFalse(result['success'])
        self.assertIn('Workflow 999 not found', result['error'])
    
    def test_run_workflow_no_nodes(self):
        """Test workflow with no nodes."""
        # Create workflow without nodes
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Workflows (id, name, active) VALUES (?, ?, ?)", (2, "Empty Workflow", 1))
        
        result = self.executor.run_workflow(2)
        
        self.assertFalse(result['success'])
        self.assertIn('No nodes found for workflow 2', result['error'])
    
    def test_run_workflow_no_root_nodes(self):
        """Test workflow with no root nodes (circular dependency)."""
        # Create workflow with circular dependency
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Workflows (id, name, active) VALUES (?, ?, ?)", (3, "Circular Workflow", 1))
            cursor.execute("""
                INSERT INTO Node (id, workflow_id, name, type, parameters, position) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (10, 3, "Node A", "Trigger", '{}', '{"x": 0, "y": 0}'))
            cursor.execute("""
                INSERT INTO Node (id, workflow_id, name, type, parameters, position) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (11, 3, "Node B", "Command", '{}', '{"x": 100, "y": 0}'))
            cursor.execute("""
                INSERT INTO Connections (id, from_node_id, to_node_id) 
                VALUES (?, ?, ?)
            """, (10, 10, 11))  # A -> B
            cursor.execute("""
                INSERT INTO Connections (id, from_node_id, to_node_id) 
                VALUES (?, ?, ?)
            """, (11, 11, 10))  # B -> A (circular)
        
        result = self.executor.run_workflow(3)
        
        self.assertFalse(result['success'])
        self.assertIn('No root nodes found for workflow 3', result['error'])


class TestRunWorkflowFunction(unittest.TestCase):
    """Test cases for the run_workflow function."""
    
    def setUp(self):
        """Set up test database and executor."""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Create test database schema
        self._create_test_database()
        
        # Sample test data
        self.workflow_id = 1
        self._insert_test_data()
    
    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_test_database(self):
        """Create test database with schema from db-setup.sql."""
        # Read the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'db-setup.sql')
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript(sql_script)
    
    def _insert_test_data(self):
        """Insert test data into database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert workflow
            cursor.execute("""
                INSERT INTO Workflows (id, name, active) VALUES (?, ?, ?)
            """, (1, "Test Workflow", 1))
            
            # Insert nodes
            nodes = [
                (1, 1, "Start", "Trigger", '{}', '{"x": 0, "y": 0}'),
                (2, 1, "Process", "Command", '{"command": "echo hello"}', '{"x": 100, "y": 0}'),
                (3, 1, "Constant", "Constant", '{"value": "test_value"}', '{"x": 200, "y": 0}')
            ]
            
            cursor.executemany("""
                INSERT INTO Node (id, workflow_id, name, type, parameters, position) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, nodes)
            
            # Insert connections
            connections = [
                (1, 1, 2),  # Start -> Process
                (2, 2, 3)   # Process -> Constant
            ]
            
            cursor.executemany("""
                INSERT INTO Connections (id, from_node_id, to_node_id) 
                VALUES (?, ?, ?)
            """, connections)
    
    @patch('model.run_workflow.WorkflowExecutor')
    def test_run_workflow_function(self, mock_executor_class):
        """Test the run_workflow function."""
        # Mock the executor instance
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        # Mock the run_workflow method
        expected_result = {
            'success': True,
            'execution_id': 123,
            'results': {'node1': {'success': True, 'output': 'test'}},
            'message': 'Workflow executed successfully'
        }
        mock_executor.run_workflow.return_value = expected_result
        
        # Call the function
        result = run_workflow(1, {"test": "data"})
        
        # Verify results
        self.assertEqual(result, expected_result)
        mock_executor_class.assert_called_once()
        mock_executor.run_workflow.assert_called_once_with(1, {"test": "data"})
    
    @patch('model.run_workflow.WorkflowExecutor')
    def test_run_workflow_function_no_input(self, mock_executor_class):
        """Test the run_workflow function without initial input."""
        # Mock the executor instance
        mock_executor = MagicMock()
        mock_executor_class.return_value = mock_executor
        
        # Mock the run_workflow method
        expected_result = {
            'success': True,
            'execution_id': 123,
            'results': {},
            'message': 'Workflow executed successfully'
        }
        mock_executor.run_workflow.return_value = expected_result
        
        # Call the function without input
        result = run_workflow(1)
        
        # Verify results
        self.assertEqual(result, expected_result)
        mock_executor.run_workflow.assert_called_once_with(1, None)


class TestWorkflowExecutionIntegration(unittest.TestCase):
    """Integration tests for workflow execution."""
    
    def setUp(self):
        """Set up test database and executor."""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.executor = WorkflowExecutor(self.db_path)
        
        # Create test database schema
        self._create_test_database()
    
    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_test_database(self):
        """Create test database with schema from db-setup.sql."""
        # Read the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'db-setup.sql')
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript(sql_script)
    
    def test_simple_linear_workflow(self):
        """Test a simple linear workflow execution."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create workflow
            cursor.execute("INSERT INTO Workflows (id, name, active) VALUES (?, ?, ?)", (1, "Linear Workflow", 1))
            
            # Create nodes
            nodes = [
                (1, 1, "Start", "Trigger", '{}', '{"x": 0, "y": 0}'),
                (2, 1, "Process", "Command", '{"command": "echo hello"}', '{"x": 100, "y": 0}'),
                (3, 1, "End", "Constant", '{"value": "done"}', '{"x": 200, "y": 0}')
            ]
            
            cursor.executemany("""
                INSERT INTO Node (id, workflow_id, name, type, parameters, position) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, nodes)
            
            # Create connections
            connections = [
                (1, 1, 2),  # Start -> Process
                (2, 2, 3)   # Process -> End
            ]
            
            cursor.executemany("""
                INSERT INTO Connections (id, from_node_id, to_node_id) 
                VALUES (?, ?, ?)
            """, connections)
        
        # Execute workflow
        result = self.executor.run_workflow(1, {"initial": "test"})
        
        # Verify results
        self.assertTrue(result['success'])
        self.assertEqual(len(result['results']), 3)
        self.assertIn('execution_ids', result)
        self.assertEqual(len(result['execution_ids']), 3)  # All 3 nodes have execution records
        
        # Verify execution records were created
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Executions WHERE workflow_id = ?", (1,))
            executions = cursor.fetchall()
            self.assertEqual(len(executions), 3)  # One record per node
            for execution in executions:
                self.assertEqual(execution[4], "completed")  # status
    
    def test_parallel_workflow(self):
        """Test workflow with parallel execution paths."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create workflow
            cursor.execute("INSERT INTO Workflows (id, name, active) VALUES (?, ?, ?)", (2, "Parallel Workflow", 1))
            
            # Create nodes
            nodes = [
                (10, 2, "Start", "Trigger", '{}', '{"x": 0, "y": 0}'),
                (11, 2, "Branch A", "Command", '{"command": "echo A"}', '{"x": 100, "y": -50}'),
                (12, 2, "Branch B", "Command", '{"command": "echo B"}', '{"x": 100, "y": 50}'),
                (13, 2, "Merge", "Constant", '{"value": "merged"}', '{"x": 200, "y": 0}')
            ]
            
            cursor.executemany("""
                INSERT INTO Node (id, workflow_id, name, type, parameters, position) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, nodes)
            
            # Create connections
            connections = [
                (10, 10, 11),  # Start -> Branch A
                (11, 10, 12),  # Start -> Branch B
                (12, 11, 13),  # Branch A -> Merge
                (13, 12, 13)   # Branch B -> Merge
            ]
            
            cursor.executemany("""
                INSERT INTO Connections (id, from_node_id, to_node_id) 
                VALUES (?, ?, ?)
            """, connections)
        
        # Execute workflow
        result = self.executor.run_workflow(2, {"initial": "test"})
        
        # Verify results
        self.assertTrue(result['success'])
        self.assertEqual(len(result['results']), 4)
        self.assertEqual(len(result['execution_ids']), 4)  # All 4 nodes have execution records
        
        # Verify all nodes were executed
        executed_nodes = set(result['results'].keys())
        expected_nodes = {10, 11, 12, 13}
        self.assertEqual(executed_nodes, expected_nodes)
        
        # Verify execution records were created
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Executions WHERE workflow_id = ?", (2,))
            executions = cursor.fetchall()
            self.assertEqual(len(executions), 4)  # One record per node


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
