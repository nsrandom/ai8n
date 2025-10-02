# AI8N Workflow Execution System

A Python system for executing workflows defined as directed acyclic graphs (DAGs) of nodes stored in a SQLite database.

## Features

- **Workflow Execution**: Execute workflows by ID from SQLite database
- **Node Types**: Support for 6 different node types (Trigger, Command, Constant, LLM, Conditional, Manual)
- **DAG Traversal**: Automatic dependency resolution and execution order
- **Execution Tracking**: Record execution status and results in database
- **Error Handling**: Comprehensive error handling and logging
- **Testing**: Full test suite with 22 test cases

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the database:
```bash
sqlite3 data/ai8n.db < data/db-setup.sql
```

## Usage

### Basic Usage

```python
from model.run_workflow import run_workflow

# Execute workflow with ID 1
result = run_workflow(1, {"initial": "data"})

if result['success']:
    print("Workflow executed successfully!")
    print(f"Execution ID: {result['execution_id']}")
    print(f"Results: {result['results']}")
else:
    print(f"Error: {result['error']}")
```

### Advanced Usage

```python
from model.run_workflow import WorkflowExecutor

# Create executor with custom database path
executor = WorkflowExecutor("path/to/your/database.db")

# Execute workflow
result = executor.run_workflow(1, {"custom": "input"})
```

## Node Types

1. **Trigger**: Entry point nodes that start workflow execution
2. **Command**: Execute external commands or scripts
3. **Constant**: Return constant values
4. **LLM**: Call language model APIs
5. **Conditional**: Make branching decisions
6. **Manual**: Require human intervention

## Database Schema

The system uses SQLite with the following tables:
- `Workflows`: Workflow definitions
- `Node`: Individual workflow nodes
- `Connections`: Node connections (edges in the DAG)
- `Executions`: Execution records and results

## Testing

### Run All Tests

```bash
python run_tests.py
```

### Run with pytest

```bash
pytest test_run_workflow.py -v
```

### Test Coverage

```bash
pytest test_run_workflow.py --cov=model.run_workflow --cov-report=html
```

## Test Structure

The test suite includes:

- **Unit Tests**: Individual method testing
- **Integration Tests**: End-to-end workflow execution
- **Error Handling Tests**: Various error scenarios
- **DAG Traversal Tests**: Complex workflow structures

### Test Categories

1. **TestWorkflowExecutor**: Tests for the main executor class
2. **TestRunWorkflowFunction**: Tests for the public API function
3. **TestWorkflowExecutionIntegration**: Integration tests with real database

## Development

### Adding New Node Types

1. Add the node type to the database schema CHECK constraint
2. Create a new `execute_{type}_node` method in `WorkflowExecutor`
3. Add the case to the `execute_node` method
4. Write tests for the new node type

### Extending Tests

- Add new test methods to existing test classes
- Create new test classes for new functionality
- Use `unittest.mock` for mocking external dependencies

## Error Handling

The system handles various error scenarios:
- Workflow not found
- Invalid node types
- Circular dependencies
- Database connection errors
- Node execution failures

All errors are logged and returned in a structured format.

## Logging

The system uses Python's built-in logging module. Set log level to control verbosity:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
