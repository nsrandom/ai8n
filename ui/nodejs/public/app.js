// AI8N Workflow Visualizer - Frontend JavaScript
class WorkflowVisualizer {
    constructor() {
        this.currentWorkflow = null;
        this.currentExecution = null;
        this.workflows = [];
        this.executions = [];
        this.graphVisualizer = new GraphVisualizer();
        this.executionDisplay = new ExecutionDisplay();
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadWorkflows();
    }

    setupEventListeners() {
        // Workflow selection
        document.getElementById('workflowSelect').addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadWorkflow(e.target.value);
            }
        });

        // Execution selection
        document.getElementById('executionSelect').addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadExecution(e.target.value);
            }
        });

        // Execute workflow
        const executeBtn = document.getElementById('executeBtn');
        if (executeBtn) {
            executeBtn.addEventListener('click', () => {
                this.executeWorkflow();
            });
        }

        // Refresh
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadWorkflows();
        });

        // Retry
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.loadWorkflows();
        });

        // Zoom controls
        document.getElementById('zoomInBtn').addEventListener('click', () => {
            this.zoomIn();
        });

        document.getElementById('zoomOutBtn').addEventListener('click', () => {
            this.zoomOut();
        });

        document.getElementById('resetZoomBtn').addEventListener('click', () => {
            this.resetZoom();
        });

        // Modal close
        document.querySelector('.modal-close').addEventListener('click', () => {
            this.executionDisplay.closeModal();
        });

        // Close modal on outside click
        document.getElementById('nodeModal').addEventListener('click', (e) => {
            if (e.target.id === 'nodeModal') {
                this.executionDisplay.closeModal();
            }
        });
    }

    async loadWorkflows() {
        this.showLoading();
        try {
            const response = await fetch('/api/workflows');
            
            if (!response.ok) throw new Error('Failed to load workflows');
            
            this.workflows = await response.json();
            this.populateWorkflowSelect();
            
            if (this.workflows.length === 0) {
                this.showEmpty();
            } else {
                this.hideStates();
            }
        } catch (error) {
            console.error('[WorkflowVisualizer] Error loading workflows:', error);
            this.showError('Failed to load workflows: ' + error.message);
        }
    }

    populateWorkflowSelect() {
        const select = document.getElementById('workflowSelect');
        
        if (!select) {
            console.error('[WorkflowVisualizer] workflowSelect element not found!');
            return;
        }
        
        select.innerHTML = '<option value="">Select a workflow...</option>';
        
        this.workflows.forEach(workflow => {
            const option = document.createElement('option');
            option.value = workflow.id;
            option.textContent = `${workflow.name} (ID: ${workflow.id})`;
            select.appendChild(option);
        });
    }

    async loadWorkflow(workflowId) {
        this.showLoading();
        try {
            const response = await fetch(`/api/workflows/${workflowId}`);
            if (!response.ok) throw new Error('Failed to load workflow');
            
            this.currentWorkflow = await response.json();
            this.currentExecution = null;
            
            // Load executions for this workflow
            await this.loadWorkflowExecutions(workflowId);
            
            // Show workflow details
            this.showWorkflowDetails();
            this.renderWorkflowGraph();
            this.hideStates();
        } catch (error) {
            this.showError('Failed to load workflow: ' + error.message);
        }
    }

    async loadWorkflowExecutions(workflowId) {
        try {
            const response = await fetch(`/api/workflows/${workflowId}/executions`);
            if (!response.ok) throw new Error('Failed to load executions');
            
            this.executions = await response.json();
            this.populateExecutionSelect();
        } catch (error) {
            console.error('Failed to load executions:', error);
            this.executions = [];
            this.populateExecutionSelect();
        }
    }

    populateExecutionSelect() {
        const select = document.getElementById('executionSelect');
        select.innerHTML = '<option value="">No executions</option>';
        
        this.executions.forEach(execution => {
            const option = document.createElement('option');
            option.value = execution.id;
            option.textContent = `Exec #${execution.id} - ${execution.status} (${new Date(execution.started_at).toLocaleString()})`;
            select.appendChild(option);
        });
    }

    async loadExecution(executionId) {
        this.showLoading();
        try {
            const response = await fetch(`/api/executions/${executionId}`);
            if (!response.ok) throw new Error('Failed to load execution');
            
            this.currentExecution = await response.json();
            this.showExecutionDetails();
            this.renderExecutionGraph();
            this.hideStates();
        } catch (error) {
            this.showError('Failed to load execution: ' + error.message);
        }
    }

    showWorkflowDetails() {
        const workflow = this.currentWorkflow.workflow;
        const detailsDiv = document.getElementById('workflowInfo');
        
        detailsDiv.innerHTML = `
            <div class="workflow-detail-item">
                <strong>Name:</strong> ${workflow.name}
            </div>
            <div class="workflow-detail-item">
                <strong>ID:</strong> ${workflow.id}
            </div>
            <div class="workflow-detail-item">
                <strong>Active:</strong> ${workflow.active ? 'Yes' : 'No'}
            </div>
            <div class="workflow-detail-item">
                <strong>Created:</strong> ${new Date(workflow.created_at).toLocaleString()}
            </div>
            <div class="workflow-detail-item">
                <strong>Nodes:</strong> ${this.currentWorkflow.nodes.length}
            </div>
            <div class="workflow-detail-item">
                <strong>Connections:</strong> ${this.currentWorkflow.connections.length}
            </div>
        `;
        
        document.getElementById('workflowDetails').style.display = 'block';
    }

    showExecutionDetails() {
        this.executionDisplay.showExecutionDetails(this.currentExecution);
    }

    renderWorkflowGraph() {
        const container = document.getElementById('graphContainer');
        
        if (!container) {
            console.error('[WorkflowVisualizer] graphContainer element not found!');
            return;
        }
        
        if (!this.currentWorkflow || !this.currentWorkflow.nodes.length) {
            container.innerHTML = '<div class="text-center">No nodes to display</div>';
            return;
        }
        
        this.graphVisualizer.createGraph(container, this.currentWorkflow, false, {}, (node, nodeExecution) => {
            this.executionDisplay.showNodeDetails(node, nodeExecution);
        });
        
        this.executionDisplay.showWorkflowView();
    }

    renderExecutionGraph() {
        const container = document.getElementById('graphContainer');
        
        if (!this.currentExecution || !this.currentWorkflow || !this.currentWorkflow.nodes.length) {
            container.innerHTML = '<div class="text-center">No execution data to display</div>';
            return;
        }
        
        const nodeExecutionLookup = {};
        this.currentExecution.node_executions.forEach(ne => {
            nodeExecutionLookup[ne.node_id] = ne;
        });
        
        this.graphVisualizer.createGraph(container, this.currentWorkflow, true, nodeExecutionLookup, (node, nodeExecution) => {
            this.executionDisplay.showNodeDetails(node, nodeExecution);
        });
        
        this.executionDisplay.showExecutionView();
    }

    async executeWorkflow() {
        const workflowId = document.getElementById('workflowSelect').value;
        if (!workflowId) {
            this.showToast('Please select a workflow first', 'warning');
            return;
        }
        
        const inputDataElement = document.getElementById('inputData');
        const inputDataText = inputDataElement ? inputDataElement.value.trim() : '';
        let inputData = {};
        
        if (inputDataText) {
            try {
                inputData = JSON.parse(inputDataText);
            } catch (e) {
                this.showToast('Invalid JSON input data', 'error');
                return;
            }
        }
        
        this.showLoading();
        try {
            const response = await fetch(`/api/workflows/${workflowId}/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: inputData }),
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('Workflow executed successfully!', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                this.showToast(`Execution failed: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Execution error: ${error.message}`, 'error');
        }
    }

    zoomIn() {
        this.graphVisualizer.zoomIn();
    }

    zoomOut() {
        this.graphVisualizer.zoomOut();
    }

    resetZoom() {
        this.graphVisualizer.resetZoom();
    }

    showLoading() {
        document.getElementById('loadingState').style.display = 'flex';
        document.getElementById('errorState').style.display = 'none';
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('workflowViz').style.display = 'none';
        document.getElementById('executionDetails').style.display = 'none';
    }

    showError(message) {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('errorState').style.display = 'flex';
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('workflowViz').style.display = 'none';
        document.getElementById('executionDetails').style.display = 'none';
        document.getElementById('errorMessage').textContent = message;
    }

    showEmpty() {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('errorState').style.display = 'none';
        document.getElementById('emptyState').style.display = 'flex';
        document.getElementById('workflowViz').style.display = 'none';
        document.getElementById('executionDetails').style.display = 'none';
    }

    hideStates() {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('errorState').style.display = 'none';
        document.getElementById('emptyState').style.display = 'none';
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        const visualizer = new WorkflowVisualizer();
        window.visualizer = visualizer;
    } catch (error) {
        console.error('[App] Error creating WorkflowVisualizer:', error);
    }
});
