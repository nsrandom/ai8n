# AI8N Workflow Visualizer - Node.js UI

A modern, responsive web interface built with Node.js, Express, and D3.js for visualizing and managing AI8N workflows.

## Features

- **🎯 Workflow Selection**: Browse and select from available workflows in the database
- **📊 Interactive Graph Visualization**: View workflow nodes and connections as an interactive D3.js graph
- **🔍 Node Details**: Click on nodes to explore individual node properties, parameters, and positions
- **🔗 Connection Information**: See how nodes are connected in the workflow with visual arrows
- **📈 Execution History**: View execution history for each workflow with detailed status tracking
- **🚀 Execute Workflows**: Trigger workflow executions directly from the UI with custom input data
- **⚡ Quick Execute**: One-click execution with default input data for quick testing
- **📋 Execution Flow Visualization**: See how data flows through nodes during execution with color-coded status
- **🔬 Node Execution Details**: View input/output values for each node in an execution
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **🎨 Modern UI**: Clean, intuitive interface with smooth animations and transitions

## Technology Stack

- **Backend**: Node.js + Express
- **Frontend**: Vanilla JavaScript + D3.js
- **Database**: SQLite3
- **Styling**: Modern CSS with Flexbox/Grid
- **Icons**: Font Awesome
- **Visualization**: D3.js for interactive graphs

## Requirements

- Node.js 14.0.0 or higher
- SQLite database with AI8N workflow data
- Python 3.7+ (for workflow execution)

## Installation

1. Navigate to the Node.js UI directory:
   ```bash
   cd ui/nodejs
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Ensure you have workflow data in the database:
   ```bash
   # From the project root
   python data/create_incrementor_workflow.py 3
   ```

## Running the Application

### Option 1: Using npm start (Production)
```bash
npm start
```

### Option 2: Using npm run dev (Development with auto-reload)
```bash
npm run dev
```

### Option 3: Direct Node.js command
```bash
node server.js
```

The application will start on `http://localhost:3000` by default.

## Usage

### 1. Workflow Selection
- Use the dropdown in the sidebar to select a workflow
- The main area will display an interactive graph of the selected workflow
- Workflow details are shown in the sidebar

### 2. Workflow Visualization
- **Nodes**: Represented as colored circles with node names
- **Connections**: Shown as arrows between nodes
- **Interactions**: 
  - Click and drag nodes to reposition them
  - Click on nodes to view detailed information
  - Use zoom controls to zoom in/out or reset view

### 3. Node Types and Colors
- 🔴 **Trigger** (Red) - Entry points of workflows
- 🟢 **Command** (Teal) - External command execution
- 🔵 **Constant** (Blue) - Constant value nodes
- 🟡 **LLM** (Green) - Language model nodes
- 🟠 **Conditional** (Yellow) - Decision/branching nodes
- 🟣 **Manual** (Plum) - Human intervention nodes

### 4. Workflow Execution
- **Custom Input**: Enter JSON input data in the textarea
- **Execute Button**: Run workflow with custom input
- **Quick Execute**: Run with default input data (`{"value": 42, "test": "data"}`)
- **Real-time Feedback**: Toast notifications show execution status

### 5. Execution History
- Select an execution from the dropdown to view execution details
- **Execution Flow Graph**: Shows node execution status with color coding:
  - 🟢 **Completed** (Green) - Successfully executed
  - 🟡 **Running** (Yellow) - Currently executing
  - 🔴 **Failed** (Red) - Execution failed
  - ⚫ **Pending** (Gray) - Not yet executed
- **Data Flow**: Green arrows show successful data flow between completed nodes

### 6. Node Details Modal
- Click on any node to view detailed information
- Shows node properties, parameters, and execution details (if available)
- Displays input/output data for executed nodes

## API Endpoints

The application provides a REST API for workflow management:

- `GET /api/workflows` - Get all workflows
- `GET /api/workflows/:id` - Get workflow details with nodes and connections
- `GET /api/workflows/:id/executions` - Get execution history for a workflow
- `GET /api/executions/:id` - Get detailed execution information
- `POST /api/workflows/:id/execute` - Execute a workflow with custom input

## Configuration

### Environment Variables
- `PORT` - Server port (default: 3000)
- `DB_PATH` - Path to SQLite database (default: `../../data/ai8n.db`)

### Database Path
The application automatically detects the database path relative to the server location. If you need to change this, modify the `DB_PATH` constant in `server.js`.

## Development

### Project Structure
```
ui/nodejs/
├── package.json          # Dependencies and scripts
├── server.js             # Express server and API routes
├── README.md             # This file
└── public/               # Static files
    ├── index.html        # Main HTML template
    ├── styles.css        # CSS styles
    └── app.js            # Frontend JavaScript
```

### Adding New Features
1. **Backend**: Add new API routes in `server.js`
2. **Frontend**: Extend the `WorkflowVisualizer` class in `app.js`
3. **Styling**: Add new styles in `styles.css`

### Debugging
- Use `npm run dev` for development with auto-reload
- Check browser console for frontend errors
- Check server console for backend errors
- Use browser developer tools to inspect network requests

## Troubleshooting

### Common Issues

1. **"No workflows found"**
   - Ensure the database exists and contains workflow data
   - Check the database path in `server.js`
   - Run the workflow creation scripts

2. **Database connection errors**
   - Verify the SQLite database file exists at the correct path
   - Check file permissions
   - Ensure the database is not locked by another process

3. **Workflow execution fails**
   - Ensure Python 3.7+ is installed and accessible
   - Check that `run_workflow.py` exists in the project root
   - Verify the workflow executor can access the database

4. **Port already in use**
   - Change the PORT environment variable
   - Kill the process using the port: `lsof -ti:3000 | xargs kill -9`

### Performance Tips

- For large workflows with many nodes, consider implementing pagination
- Use the zoom controls to navigate large graphs
- Close the node details modal when not needed to improve performance

## Comparison with Streamlit UI

This Node.js UI provides several advantages over the Streamlit version:

- **Better Performance**: Client-side rendering with D3.js
- **More Interactive**: Drag-and-drop nodes, zoom controls, modal dialogs
- **Responsive Design**: Works well on all device sizes
- **Modern UI**: Clean, professional interface with smooth animations
- **Better Error Handling**: Comprehensive error states and user feedback
- **REST API**: Can be integrated with other applications
- **No Python Dependencies**: Pure JavaScript/Node.js stack

## License

MIT License - see the main project LICENSE file for details.
