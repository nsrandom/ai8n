-- SQLite Database Schema for AI8N Workflow System
-- This schema defines the structure for managing workflows, nodes, connections, and executions

-- Workflows table
CREATE TABLE Workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Node table
CREATE TABLE Node (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('Trigger', 'Command', 'Constant', 'LLM', 'Conditional', 'Manual')),
    parameters TEXT, -- JSON stored as TEXT
    position TEXT,   -- JSON stored as TEXT for x,y coordinates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES Workflows(id) ON DELETE CASCADE
);

-- Connections table
CREATE TABLE Connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node_id INTEGER NOT NULL,
    to_node_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_node_id) REFERENCES Node(id) ON DELETE CASCADE,
    FOREIGN KEY (to_node_id) REFERENCES Node(id) ON DELETE CASCADE
);

-- WorkflowExecutions table - tracks workflow-level execution
CREATE TABLE WorkflowExecutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    input TEXT,  -- JSON stored as TEXT for initial input data
    output TEXT, -- JSON stored as TEXT for final output data
    error TEXT, -- JSON stored as TEXT for workflow-level errors
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES Workflows(id) ON DELETE CASCADE
);

-- NodeExecutions table - tracks node-level execution within workflows
CREATE TABLE NodeExecutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_execution_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    input TEXT,  -- JSON stored as TEXT for input data
    output TEXT, -- JSON stored as TEXT for output data
    error TEXT, -- JSON stored as TEXT for node-level errors
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_execution_id) REFERENCES WorkflowExecutions(id) ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES Node(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_node_workflow_id ON Node(workflow_id);
CREATE INDEX idx_connections_from_node ON Connections(from_node_id);
CREATE INDEX idx_connections_to_node ON Connections(to_node_id);
CREATE INDEX idx_workflow_executions_workflow_id ON WorkflowExecutions(workflow_id);
CREATE INDEX idx_workflow_executions_status ON WorkflowExecutions(status);
CREATE INDEX idx_workflow_executions_started_at ON WorkflowExecutions(started_at);
CREATE INDEX idx_node_executions_workflow_execution_id ON NodeExecutions(workflow_execution_id);
CREATE INDEX idx_node_executions_node_id ON NodeExecutions(node_id);
CREATE INDEX idx_node_executions_status ON NodeExecutions(status);
CREATE INDEX idx_node_executions_started_at ON NodeExecutions(started_at);

-- Create triggers to automatically update the updated_at timestamp
CREATE TRIGGER update_workflows_timestamp 
    AFTER UPDATE ON Workflows
    FOR EACH ROW
    BEGIN
        UPDATE Workflows SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_node_timestamp 
    AFTER UPDATE ON Node
    FOR EACH ROW
    BEGIN
        UPDATE Node SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_connections_timestamp 
    AFTER UPDATE ON Connections
    FOR EACH ROW
    BEGIN
        UPDATE Connections SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_workflow_executions_timestamp 
    AFTER UPDATE ON WorkflowExecutions
    FOR EACH ROW
    BEGIN
        UPDATE WorkflowExecutions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_node_executions_timestamp 
    AFTER UPDATE ON NodeExecutions
    FOR EACH ROW
    BEGIN
        UPDATE NodeExecutions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
