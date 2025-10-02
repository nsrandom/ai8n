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

-- Executions table
CREATE TABLE Executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    data TEXT, -- JSON stored as TEXT
    error TEXT, -- JSON stored as TEXT
    FOREIGN KEY (workflow_id) REFERENCES Workflows(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_node_workflow_id ON Node(workflow_id);
CREATE INDEX idx_connections_from_node ON Connections(from_node_id);
CREATE INDEX idx_connections_to_node ON Connections(to_node_id);
CREATE INDEX idx_executions_workflow_id ON Executions(workflow_id);
CREATE INDEX idx_executions_status ON Executions(status);
CREATE INDEX idx_executions_started_at ON Executions(started_at);

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
