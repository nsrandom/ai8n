const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { spawn } = require('child_process');

const router = express.Router();

// Database path - adjust relative to the project root
const DB_PATH = path.join(__dirname, '../../data/ai8n.db');

// Database helper functions
function getDbConnection() {
    return new sqlite3.Database(DB_PATH, (err) => {
        if (err) {
            console.error('Error opening database:', err.message);
        }
    });
}

// API Routes

// Get all workflows
router.get('/workflows', (req, res) => {
    const db = getDbConnection();
    db.all("SELECT id, name, active, created_at FROM Workflows ORDER BY created_at DESC", [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
        db.close();
    });
});

// Get workflow details with nodes and connections
router.get('/workflows/:id', (req, res) => {
    const workflowId = req.params.id;
    const db = getDbConnection();
    
    // Get workflow
    db.get("SELECT * FROM Workflows WHERE id = ?", [workflowId], (err, workflow) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        if (!workflow) {
            res.status(404).json({ error: 'Workflow not found' });
            return;
        }
        
        // Get nodes
        db.all("SELECT * FROM Nodes WHERE workflow_id = ? ORDER BY id", [workflowId], (err, nodes) => {
            if (err) {
                res.status(500).json({ error: err.message });
                return;
            }
            
            // Get connections
            db.all(`
                SELECT c.*, 
                       n1.name as from_node_name, 
                       n2.name as to_node_name
                FROM Connections c
                JOIN Nodes n1 ON c.from_node_id = n1.id
                JOIN Nodes n2 ON c.to_node_id = n2.id
                WHERE n1.workflow_id = ?
            `, [workflowId], (err, connections) => {
                if (err) {
                    res.status(500).json({ error: err.message });
                    return;
                }
                
                res.json({
                    workflow: workflow,
                    nodes: nodes,
                    connections: connections
                });
                db.close();
            });
        });
    });
});

// Get workflow executions
router.get('/workflows/:id/executions', (req, res) => {
    const workflowId = req.params.id;
    const db = getDbConnection();
    
    db.all(`
        SELECT id, status, started_at, ended_at, input, output, error
        FROM WorkflowExecutions 
        WHERE workflow_id = ? 
        ORDER BY started_at DESC
    `, [workflowId], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
        db.close();
    });
});

// Get execution details
router.get('/executions/:id', (req, res) => {
    const executionId = req.params.id;
    const db = getDbConnection();
    
    // Get workflow execution details
    db.get(`
        SELECT we.*, w.name as workflow_name
        FROM WorkflowExecutions we
        JOIN Workflows w ON we.workflow_id = w.id
        WHERE we.id = ?
    `, [executionId], (err, execution) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        if (!execution) {
            res.status(404).json({ error: 'Execution not found' });
            return;
        }
        
        // Get node executions
        db.all(`
            SELECT ne.*, n.name as node_name, n.type as node_type
            FROM NodeExecutions ne
            JOIN Nodes n ON ne.node_id = n.id
            WHERE ne.workflow_execution_id = ?
            ORDER BY ne.started_at
        `, [executionId], (err, nodeExecutions) => {
            if (err) {
                res.status(500).json({ error: err.message });
                return;
            }
            
            res.json({
                execution: execution,
                node_executions: nodeExecutions
            });
            db.close();
        });
    });
});

// Execute workflow
router.post('/workflows/:id/execute', (req, res) => {
    const workflowId = req.params.id;
    const inputData = req.body.input || {};
    
    // Execute the Python workflow executor
    const pythonProcess = spawn('python3', [
        path.join(__dirname, '../../run_workflow.py'),
        workflowId.toString(),
        JSON.stringify(inputData)
    ], {
        cwd: path.join(__dirname, '../..')
    });
    
    let stdout = '';
    let stderr = '';
    
    pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
        if (code === 0) {
            try {
                const result = JSON.parse(stdout);
                res.json(result);
            } catch (e) {
                res.status(500).json({ 
                    success: false, 
                    error: 'Failed to parse execution result',
                    stdout: stdout,
                    stderr: stderr
                });
            }
        } else {
            res.status(500).json({ 
                success: false, 
                error: 'Workflow execution failed',
                stderr: stderr,
                stdout: stdout
            });
        }
    });
    
    pythonProcess.on('error', (err) => {
        res.status(500).json({ 
            success: false, 
            error: 'Failed to start workflow execution',
            details: err.message
        });
    });
});

module.exports = router;
