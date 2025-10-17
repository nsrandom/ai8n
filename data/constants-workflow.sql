-- SQL to set up a simple workflow with 3 constant nodes in sequence
-- This creates a workflow where data flows from Constant1 -> Constant2 -> Constant3

-- 1. Create the workflow
INSERT INTO Workflows (name, active) 
VALUES ('Simple Constant Sequence Workflow', 1);

-- Get the workflow ID (assuming it's 1, or use last_insert_rowid() in SQLite)
-- For this example, we'll assume the workflow ID is 1

-- 2. Create 3 constant nodes
INSERT INTO Nodes (workflow_id, name, type, parameters, position) VALUES
(1, 'Constant1', 'Constant', '{"value": "Hello"}', '{"x": 100, "y": 100}'),
(1, 'Constant2', 'Constant', '{"value": "World"}', '{"x": 300, "y": 100}'),
(1, 'Constant3', 'Constant', '{"value": "!"}', '{"x": 500, "y": 100}');

-- 3. Create connections between the nodes in sequence
-- Connect Constant1 -> Constant2
INSERT INTO Connections (from_node_id, to_node_id) 
SELECT 
    (SELECT id FROM Nodes WHERE workflow_id = 1 AND name = 'Constant1'),
    (SELECT id FROM Nodes WHERE workflow_id = 1 AND name = 'Constant2');

-- Connect Constant2 -> Constant3
INSERT INTO Connections (from_node_id, to_node_id) 
SELECT 
    (SELECT id FROM Nodes WHERE workflow_id = 1 AND name = 'Constant2'),
    (SELECT id FROM Nodes WHERE workflow_id = 1 AND name = 'Constant3');

-- Verify the setup
SELECT 'Workflow created:' as info, id, name, active FROM Workflows WHERE id = 1;

SELECT 'Nodes created:' as info, id, name, type, parameters FROM Nodes WHERE workflow_id = 1 ORDER BY id;

SELECT 'Connections created:' as info, 
       c.id, 
       n1.name as from_node, 
       n2.name as to_node 
FROM Connections c
JOIN Nodes n1 ON c.from_node_id = n1.id
JOIN Nodes n2 ON c.to_node_id = n2.id
WHERE n1.workflow_id = 1;
