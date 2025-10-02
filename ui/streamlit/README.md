# AI8N Workflow Visualizer

A Streamlit-based web interface for visualizing and exploring AI8N workflows.

## Features

- **Workflow Selection**: Browse and select from available workflows in the database
- **Interactive Graph Visualization**: View workflow nodes and connections as an interactive graph
- **Node Details**: Explore individual node properties, parameters, and positions
- **Connection Information**: See how nodes are connected in the workflow
- **Execution History**: View execution history for each workflow
- **Execute Workflows**: Trigger workflow executions directly from the UI
- **Custom Input Data**: Provide custom JSON input data for workflow execution
- **Execution Flow Visualization**: See how data flows through nodes during execution
- **Node Execution Details**: View input/output values for each node in an execution
- **Real-time Updates**: Automatically reflects changes in the workflow database

## Requirements

- Python 3.7+
- Streamlit
- Plotly (for graph visualization)
- Pandas (for data handling)
- SQLite database with AI8N workflow data

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure you have workflow data in the database:
   ```bash
   # Create some sample workflows
   python data/create_incrementor_workflow.py 3
   ```

## Running the App

### Option 1: Using the launcher script (Recommended)
```bash
python ui/streamlit/run_app.py
```

### Option 2: Direct Streamlit command
```bash
cd /path/to/ai8n
streamlit run ui/streamlit/app.py
```

The app will open in your default web browser at `http://localhost:8501`.

## Usage

1. **Select a Workflow**: Use the dropdown in the sidebar to choose a workflow
2. **View the Graph**: The main area shows an interactive graph of the workflow
3. **Explore Nodes**: Click on the sidebar to see detailed information about each node
4. **Understand Connections**: View how nodes are connected in the workflow
5. **Execute Workflows**: Use the "Execute Workflow" section in the sidebar to run workflows with custom input
6. **Quick Execute**: Click "🚀 Execute Now" for quick execution with default input data
7. **View Executions**: Select an execution from the "Execution History" section in the sidebar
8. **Analyze Execution Flow**: See how data flows through nodes during execution with color-coded status
9. **Inspect Node Data**: View input and output values for each node in the execution

## Graph Visualization

### Workflow Graph
- **Nodes**: Represented as colored circles with node names
- **Connections**: Shown as arrows between nodes
- **Colors**: Different node types have different colors:
  - 🔴 Trigger (Red)
  - 🟢 Command (Teal)
  - 🔵 Constant (Blue)
  - 🟡 LLM (Green)
  - 🟠 Conditional (Yellow)
  - 🟣 Manual (Plum)

### Execution Flow Graph
- **Node Status Colors**: 
  - 🟢 Completed (Green)
  - 🟡 Running (Yellow)
  - 🔴 Failed (Red)
  - ⚫ Pending (Gray)
- **Data Flow**: Green arrows show successful data flow between completed nodes
- **Node Size**: Executed nodes are larger than non-executed ones
- **Execution Info**: Shows execution ID, status, and start time

## Workflow Execution

### Execute Workflow Section
- **Input Data Form**: Enter custom JSON input data for the workflow
- **Default Input**: Pre-filled with sample data (`{"value": 42, "test": "data"}`)
- **Execute Button**: Triggers workflow execution with the provided input
- **Real-time Feedback**: Shows success/error messages and execution results
- **Auto-refresh**: Page automatically refreshes to show new execution

### Quick Execute
- **One-click Execution**: Execute workflow with default input data
- **No Configuration**: Perfect for testing and quick runs
- **Immediate Results**: See execution results instantly

### Execution Results
- **Success Messages**: Clear feedback when execution succeeds
- **Error Handling**: Detailed error messages for failed executions
- **Execution History**: New executions appear in the execution list
- **Data Flow**: See how your input data flows through the workflow

## Troubleshooting

- **No workflows found**: Make sure you have created workflows in the database
- **Database connection issues**: Check that `data/ai8n.db` exists and is accessible
- **Import errors**: Ensure you're running from the project root directory

## Development

To modify the UI:

1. Edit `app.py` for main functionality
2. Modify `run_app.py` for launcher behavior
3. Test changes by running the app locally

The app automatically reloads when you make changes to the code.
