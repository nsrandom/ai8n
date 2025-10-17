// Graph Visualizer - Handles D3.js graph rendering and interactions
class GraphVisualizer {
    constructor() {
        this.svg = null;
        this.zoom = null;
    }

    createGraph(container, workflowData, isExecution = false, nodeExecutionLookup = {}) {
        const width = container.clientWidth || 800;
        const height = container.clientHeight || 600;
        
        container.innerHTML = '';
        
        this.svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', `0 0 ${width} ${height}`)
            .style('background', '#374151');
        
        const g = this.svg.append('g');
        
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });
        
        this.svg.call(this.zoom);
        
        const nodes = this.createGridLayout(workflowData.nodes, width, height);
        
        const nodeLookup = {};
        nodes.forEach(node => {
            nodeLookup[node.id] = node;
        });
        
        const links = workflowData.connections.map(conn => {
            const sourceNode = nodeLookup[conn.from_node_id];
            const targetNode = nodeLookup[conn.to_node_id];
            
            if (!sourceNode || !targetNode) {
                return null;
            }
            
            return {
                ...conn,
                source: sourceNode,
                target: targetNode
            };
        }).filter(conn => conn !== null);
        
        this.drawConnections(g, links, nodeExecutionLookup, isExecution);
        this.drawNodes(g, nodes, nodeExecutionLookup, isExecution);
        
        return { nodes, links };
    }

    createGridLayout(nodes, width, height) {
        const nodeCount = nodes.length;
        if (nodeCount === 0) return [];
        
        const cols = Math.ceil(Math.sqrt(nodeCount));
        const rows = Math.ceil(nodeCount / cols);
        
        const padding = 100;
        const availableWidth = width - (2 * padding);
        const availableHeight = height - (2 * padding);
        const colSpacing = availableWidth / (cols - 1 || 1);
        const rowSpacing = availableHeight / (rows - 1 || 1);
        
        return nodes.map((node, index) => {
            const row = Math.floor(index / cols);
            const col = index % cols;
            
            return {
                ...node,
                x: padding + (col * colSpacing),
                y: padding + (row * rowSpacing)
            };
        });
    }

    drawConnections(container, links, nodeExecutionLookup, isExecution) {
        const linkGroup = container.append('g').attr('class', 'links');
        
        links.forEach(link => {
            const line = linkGroup.append('line')
                .attr('x1', link.source.x)
                .attr('y1', link.source.y)
                .attr('x2', link.target.x)
                .attr('y2', link.target.y)
                .attr('class', 'link');
            
            if (isExecution) {
                const fromExec = nodeExecutionLookup[link.from_node_id];
                const toExec = nodeExecutionLookup[link.to_node_id];
                if (fromExec && toExec && fromExec.status === 'completed' && toExec.status === 'completed') {
                    line.attr('class', 'link success');
                }
            }
        });
    }

    drawNodes(container, nodes, nodeExecutionLookup, isExecution, onNodeClick = null) {
        nodes.forEach(node => {
            const nodeGroup = container.append('g')
                .attr('class', `node ${node.type.toLowerCase()}`)
                .attr('transform', `translate(${node.x}, ${node.y})`)
                .style('cursor', 'pointer');
            
            if (isExecution) {
                const nodeExec = nodeExecutionLookup[node.id];
                if (nodeExec) {
                    nodeGroup.attr('class', `node ${node.type.toLowerCase()} ${nodeExec.status}`);
                }
            }
            
            const radius = isExecution && nodeExecutionLookup[node.id] ? 60 : 50;
            nodeGroup.append('circle')
                .attr('r', radius)
                .attr('fill', this.getNodeColor(node, nodeExecutionLookup, isExecution))
                .attr('stroke', '#6b7280')
                .attr('stroke-width', 2);
            
            nodeGroup.append('text')
                .text(node.name)
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .attr('font-size', '12px')
                .attr('font-weight', 'bold')
                .attr('fill', 'white')
                .style('pointer-events', 'none');
            
            if (onNodeClick) {
                nodeGroup.on('click', () => {
                    onNodeClick(node, isExecution ? nodeExecutionLookup[node.id] : null);
                });
            }
        });
    }

    getNodeColor(node, nodeExecutionLookup, isExecution) {
        if (isExecution && nodeExecutionLookup[node.id]) {
            const statusColors = {
                'completed': '#10b981',
                'running': '#3b82f6',
                'failed': '#ef4444',
                'pending': '#f59e0b'
            };
            return statusColors[nodeExecutionLookup[node.id].status] || '#6b7280';
        }
        
        const typeColors = {
            'start': '#10b981',
            'end': '#ef4444',
            'process': '#3b82f6',
            'decision': '#f59e0b'
        };
        return typeColors[node.type.toLowerCase()] || '#6b7280';
    }

    zoomIn() {
        if (this.zoom && this.svg) {
            this.svg.transition().call(this.zoom.scaleBy, 1.5);
        }
    }

    zoomOut() {
        if (this.zoom && this.svg) {
            this.svg.transition().call(this.zoom.scaleBy, 1 / 1.5);
        }
    }

    resetZoom() {
        if (this.zoom && this.svg) {
            this.svg.transition().call(this.zoom.transform, d3.zoomIdentity);
        }
    }
}
