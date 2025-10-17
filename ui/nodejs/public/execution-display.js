// Execution Display - Handles execution details and node execution display
class ExecutionDisplay {
    constructor() {
        // No initialization needed
    }

    showExecutionDetails(executionData) {
        const execution = executionData.execution;
        const nodeExecutions = executionData.node_executions;
        
        this.updateExecutionHeader(execution);
        this.updateExecutionSummary(execution);
        this.updateNodeExecutions(nodeExecutions);
    }

    updateExecutionHeader(execution) {
        // Update execution title and status
        document.getElementById('executionTitle').textContent = 
            `Execution #${execution.id} - ${execution.workflow_name}`;
        
        const statusDiv = document.getElementById('executionStatus');
        statusDiv.textContent = execution.status.toUpperCase();
        statusDiv.className = `execution-status ${execution.status}`;
    }

    updateExecutionSummary(execution) {
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
    }

    updateNodeExecutions(nodeExecutions) {
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
                        <div class="json-display">${this.formatJsonDisplay(nodeExec.input)}</div>
                    ` : ''}
                    ${nodeExec.output ? `
                        <div><strong>Output:</strong></div>
                        <div class="json-display">${this.formatJsonDisplay(nodeExec.output)}</div>
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

    showNodeDetails(node, nodeExecution = null) {
        const modal = document.getElementById('nodeModal');
        const title = document.getElementById('nodeModalTitle');
        const body = document.getElementById('nodeModalBody');
        
        title.textContent = `${node.name} (${node.type})`;
        
        let content = this.buildNodeBasicInfo(node);
        content += this.buildNodeParameters(node);
        content += this.buildNodePosition(node);
        content += this.buildNodeExecutionInfo(nodeExecution);
        
        body.innerHTML = content;
        modal.style.display = 'block';
    }

    buildNodeBasicInfo(node) {
        return `
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
    }

    buildNodeParameters(node) {
        if (!node.parameters) return '';
        
        try {
            const params = JSON.parse(node.parameters);
            return `
                <div class="node-detail-item">
                    <strong>Parameters:</strong>
                    <div class="json-display">${JSON.stringify(params, null, 2)}</div>
                </div>
            `;
        } catch (e) {
            return `
                <div class="node-detail-item">
                    <strong>Parameters:</strong> ${node.parameters}
                </div>
            `;
        }
    }

    buildNodePosition(node) {
        if (!node.position) return '';
        
        try {
            const pos = JSON.parse(node.position);
            return `
                <div class="node-detail-item">
                    <strong>Position:</strong> x=${pos.x}, y=${pos.y}
                </div>
            `;
        } catch (e) {
            return `
                <div class="node-detail-item">
                    <strong>Position:</strong> ${node.position}
                </div>
            `;
        }
    }

    buildNodeExecutionInfo(nodeExecution) {
        if (!nodeExecution) return '';
        
        let content = `
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
                    <div class="json-display">${this.formatJsonDisplay(nodeExecution.input)}</div>
                </div>
            `;
        }
        
        if (nodeExecution.output) {
            content += `
                <div class="node-detail-item">
                    <strong>Output:</strong>
                    <div class="json-display">${this.formatJsonDisplay(nodeExecution.output)}</div>
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
        
        return content;
    }

    closeModal() {
        document.getElementById('nodeModal').style.display = 'none';
    }

    showExecutionView() {
        document.getElementById('workflowViz').style.display = 'none';
        document.getElementById('executionDetails').style.display = 'block';
    }

    showWorkflowView() {
        document.getElementById('workflowViz').style.display = 'block';
        document.getElementById('executionDetails').style.display = 'none';
    }

    formatJsonDisplay(jsonString) {
        try {
            // First, try to parse the JSON string
            let parsed = JSON.parse(jsonString);
            
            // If the parsed result is a string, it might be double-encoded JSON
            if (typeof parsed === 'string') {
                try {
                    // Try to parse it again in case it's double-encoded
                    const doubleParsed = JSON.parse(parsed);
                    return JSON.stringify(doubleParsed, null, 2);
                } catch (e) {
                    // If it's not double-encoded, handle escaped characters
                    const unescaped = parsed.replace(/\\n/g, '\n').replace(/\\"/g, '"');
                    return JSON.stringify(unescaped, null, 2);
                }
            }
            
            // Otherwise, format normally
            return JSON.stringify(parsed, null, 2);
        } catch (e) {
            // If JSON parsing fails, return the original string
            return jsonString;
        }
    }
}
