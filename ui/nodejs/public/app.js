// AI8N Workflow Visualizer - Frontend JavaScript
class WorkflowVisualizer {
    constructor() {
        this.currentWorkflow = null;
        this.currentExecution = null;
        this.workflows = [];
        this.executions = [];
        this.svg = null;
        this.simulation = null;
        this.zoom = null;
        
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
        document.getElementById('executeBtn').addEventListener('click', () => {
            this.executeWorkflow();
        });


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
            this.closeModal();
        });

        // Close modal on outside click
        document.getElementById('nodeModal').addEventListener('click', (e) => {
            if (e.target.id === 'nodeModal') {
                this.closeModal();
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
            this.showError('Failed to load workflows: ' + error.message);
        }
    }

    populateWorkflowSelect() {
        const select = document.getElementById('workflowSelect');
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
        const execution = this.currentExecution.execution;
        const nodeExecutions = this.currentExecution.node_executions;
        
        // Update execution title and status
        document.getElementById('executionTitle').textContent = 
            `Execution #${execution.id} - ${execution.workflow_name}`;
        
        const statusDiv = document.getElementById('executionStatus');
        statusDiv.textContent = execution.status.toUpperCase();
        statusDiv.className = `execution-status ${execution.status}`;
        
        // Show execution summary
        const summaryDiv = document.getElementById('executionSummary');
        summaryDiv.innerHTML = `
            <div class="execution-detail-item">
                <strong>Execution ID:</strong> ${execution.id}
            </div>
            <div class="execution-detail-item">
                <strong>Status:</strong> ${execution.status}
            </div>
            <div class="execution-detail-item">
                <strong>Started:</strong> ${new Date(execution.started_at).toLocaleString()}
            </div>
            <div class="execution-detail-item">
                <strong>Ended:</strong> ${execution.ended_at ? new Date(execution.ended_at).toLocaleString() : 'N/A'}
            </div>
            ${execution.input ? `
                <div class="execution-detail-item">
                    <strong>Input:</strong>
                    <div class="json-display">${JSON.stringify(JSON.parse(execution.input), null, 2)}</div>
                </div>
            ` : ''}
            ${execution.error ? `
                <div class="execution-detail-item">
                    <strong>Error:</strong>
                    <div class="json-display" style="color: #ef4444;">${execution.error}</div>
                </div>
            ` : ''}
        `;
        
        // Show node executions
        const nodeExecutionsDiv = document.getElementById('nodeExecutionsList');
        nodeExecutionsDiv.innerHTML = '';
        
        nodeExecutions.forEach((nodeExec, index) => {
            const nodeDiv = document.createElement('div');
            nodeDiv.className = 'node-execution-item';
            nodeDiv.innerHTML = `
                <div class="node-execution-header">
                    <div class="node-execution-title">
                        ${index + 1}. ${nodeExec.node_name} (${nodeExec.node_type})
                    </div>
                    <div class="node-execution-status ${nodeExec.status}">
                        ${nodeExec.status.toUpperCase()}
                    </div>
                </div>
                <div class="node-execution-details">
                    <div><strong>Node ID:</strong> ${nodeExec.node_id}</div>
                    <div><strong>Started:</strong> ${new Date(nodeExec.started_at).toLocaleString()}</div>
                    <div><strong>Ended:</strong> ${nodeExec.ended_at ? new Date(nodeExec.ended_at).toLocaleString() : 'N/A'}</div>
                    ${nodeExec.input ? `
                        <div><strong>Input:</strong></div>
                        <div class="json-display">${JSON.stringify(JSON.parse(nodeExec.input), null, 2)}</div>
                    ` : ''}
                    ${nodeExec.output ? `
                        <div><strong>Output:</strong></div>
                        <div class="json-display">${JSON.stringify(JSON.parse(nodeExec.output), null, 2)}</div>
                    ` : ''}
                    ${nodeExec.error ? `
                        <div><strong>Error:</strong></div>
                        <div class="json-display" style="color: #ef4444;">${nodeExec.error}</div>
                    ` : ''}
                </div>
            `;
            nodeExecutionsDiv.appendChild(nodeDiv);
        });
    }

    renderWorkflowGraph() {
        const container = document.getElementById('graphContainer');
        container.innerHTML = '';
        
        if (!this.currentWorkflow || !this.currentWorkflow.nodes.length) {
            container.innerHTML = '<div class="text-center">No nodes to display</div>';
            return;
        }
        
        this.createGraph(container, this.currentWorkflow, false);
    }

    renderExecutionGraph() {
        const container = document.getElementById('graphContainer');
        container.innerHTML = '';
        
        if (!this.currentExecution || !this.currentWorkflow || !this.currentWorkflow.nodes.length) {
            container.innerHTML = '<div class="text-center">No execution data to display</div>';
            return;
        }
        
        this.createGraph(container, this.currentWorkflow, true);
    }

    createGraph(container, workflowData, isExecution = false) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        // Create SVG
        this.svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Create zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });
        
        this.svg.call(this.zoom);
        
        // Create main group
        const g = this.svg.append('g');
        
        // Prepare data
        const nodes = workflowData.nodes.map(d => ({ ...d }));
        
        // Create node lookup for execution data
        let nodeExecutionLookup = {};
        if (isExecution && this.currentExecution) {
            this.currentExecution.node_executions.forEach(ne => {
                nodeExecutionLookup[ne.node_id] = ne;
            });
        }
        
        // Create node ID to node object lookup
        const nodeLookup = {};
        nodes.forEach(node => {
            nodeLookup[node.id] = node;
        });
        
        // Transform connections to have source and target properties for D3
        const links = workflowData.connections.map(conn => {
            const sourceNode = nodeLookup[conn.from_node_id];
            const targetNode = nodeLookup[conn.to_node_id];
            
            if (!sourceNode) {
                console.warn(`Source node not found for connection ${conn.id}: from_node_id=${conn.from_node_id}`);
            }
            if (!targetNode) {
                console.warn(`Target node not found for connection ${conn.id}: to_node_id=${conn.to_node_id}`);
            }
            
            return {
                ...conn,
                source: sourceNode,
                target: targetNode
            };
        }).filter(conn => conn.source && conn.target); // Filter out invalid connections
        
        // Create simulation
        this.simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));
        
        // Create links
        const link = g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(links)
            .enter().append('line')
            .attr('class', d => {
                if (isExecution) {
                    const fromExec = nodeExecutionLookup[d.from_node_id];
                    const toExec = nodeExecutionLookup[d.to_node_id];
                    if (fromExec && toExec && fromExec.status === 'completed' && toExec.status === 'completed') {
                        return 'link success';
                    }
                }
                return 'link';
            });
        
        // Create nodes
        const node = g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(nodes)
            .enter().append('g')
            .attr('class', d => {
                let classes = `node ${d.type.toLowerCase()}`;
                if (isExecution) {
                    const nodeExec = nodeExecutionLookup[d.id];
                    if (nodeExec) {
                        classes += ` ${nodeExec.status}`;
                    }
                }
                return classes;
            })
            .call(d3.drag()
                .on('start', this.dragstarted.bind(this))
                .on('drag', this.dragged.bind(this))
                .on('end', this.dragended.bind(this))
            )
            .on('click', (event, d) => {
                this.showNodeDetails(d, isExecution ? nodeExecutionLookup[d.id] : null);
            });
        
        // Add circles
        node.append('circle')
            .attr('r', d => {
                if (isExecution) {
                    const nodeExec = nodeExecutionLookup[d.id];
                    return nodeExec ? 25 : 20;
                }
                return 20;
            });
        
        // Add text
        node.append('text')
            .text(d => d.name)
            .attr('dy', 0.35 + 'em');
        
        // Update positions on simulation tick
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });
        
        // Show appropriate view
        if (isExecution) {
            document.getElementById('workflowViz').style.display = 'none';
            document.getElementById('executionDetails').style.display = 'block';
        } else {
            document.getElementById('workflowViz').style.display = 'block';
            document.getElementById('executionDetails').style.display = 'none';
        }
    }

    dragstarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    dragended(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    showNodeDetails(node, nodeExecution = null) {
        const modal = document.getElementById('nodeModal');
        const title = document.getElementById('nodeModalTitle');
        const body = document.getElementById('nodeModalBody');
        
        title.textContent = `${node.name} (${node.type})`;
        
        let content = `
            <div class="node-detail-item">
                <strong>ID:</strong> ${node.id}
            </div>
            <div class="node-detail-item">
                <strong>Type:</strong> ${node.type}
            </div>
            <div class="node-detail-item">
                <strong>Name:</strong> ${node.name}
            </div>
        `;
        
        if (node.parameters) {
            try {
                const params = JSON.parse(node.parameters);
                content += `
                    <div class="node-detail-item">
                        <strong>Parameters:</strong>
                        <div class="json-display">${JSON.stringify(params, null, 2)}</div>
                    </div>
                `;
            } catch (e) {
                content += `
                    <div class="node-detail-item">
                        <strong>Parameters:</strong> ${node.parameters}
                    </div>
                `;
            }
        }
        
        if (node.position) {
            try {
                const pos = JSON.parse(node.position);
                content += `
                    <div class="node-detail-item">
                        <strong>Position:</strong> x=${pos.x}, y=${pos.y}
                    </div>
                `;
            } catch (e) {
                content += `
                    <div class="node-detail-item">
                        <strong>Position:</strong> ${node.position}
                    </div>
                `;
            }
        }
        
        if (nodeExecution) {
            content += `
                <hr style="margin: 1rem 0;">
                <h4>Execution Details</h4>
                <div class="node-detail-item">
                    <strong>Status:</strong> <span class="execution-status ${nodeExecution.status}">${nodeExecution.status.toUpperCase()}</span>
                </div>
                <div class="node-detail-item">
                    <strong>Started:</strong> ${new Date(nodeExecution.started_at).toLocaleString()}
                </div>
                <div class="node-detail-item">
                    <strong>Ended:</strong> ${nodeExecution.ended_at ? new Date(nodeExecution.ended_at).toLocaleString() : 'N/A'}
                </div>
            `;
            
            if (nodeExecution.input) {
                content += `
                    <div class="node-detail-item">
                        <strong>Input:</strong>
                        <div class="json-display">${JSON.stringify(JSON.parse(nodeExecution.input), null, 2)}</div>
                    </div>
                `;
            }
            
            if (nodeExecution.output) {
                content += `
                    <div class="node-detail-item">
                        <strong>Output:</strong>
                        <div class="json-display">${JSON.stringify(JSON.parse(nodeExecution.output), null, 2)}</div>
                    </div>
                `;
            }
            
            if (nodeExecution.error) {
                content += `
                    <div class="node-detail-item">
                        <strong>Error:</strong>
                        <div class="json-display" style="color: #ef4444;">${nodeExecution.error}</div>
                    </div>
                `;
            }
        }
        
        body.innerHTML = content;
        modal.style.display = 'block';
    }

    closeModal() {
        document.getElementById('nodeModal').style.display = 'none';
    }

    async executeWorkflow() {
        const workflowId = document.getElementById('workflowSelect').value;
        if (!workflowId) {
            this.showToast('Please select a workflow first', 'warning');
            return;
        }
        
        const inputDataText = document.getElementById('inputData').value.trim();
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
                // Refresh the page to show new execution
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
        if (this.zoom) {
            this.svg.transition().call(this.zoom.scaleBy, 1.5);
        }
    }

    zoomOut() {
        if (this.zoom) {
            this.svg.transition().call(this.zoom.scaleBy, 1 / 1.5);
        }
    }

    resetZoom() {
        if (this.zoom) {
            this.svg.transition().call(this.zoom.transform, d3.zoomIdentity);
        }
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
    new WorkflowVisualizer();
});
