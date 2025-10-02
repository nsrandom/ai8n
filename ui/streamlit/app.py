#!/usr/bin/env python3
"""
Streamlit UI for AI8N Workflow System

This application provides a web interface to:
1. View available workflows
2. Select a workflow to visualize its nodes as a graph
3. View workflow details and node information
"""

import streamlit as st
import sqlite3
import json
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from collections import defaultdict

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model.workflow import WorkflowExecutor

# Configure Streamlit page
st.set_page_config(
    page_title="AI8N Workflow Visualizer",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

class WorkflowVisualizer:
    """Handles workflow data retrieval and visualization."""
    
    def __init__(self, db_path: str = "data/ai8n.db"):
        self.db_path = db_path
        self.executor = WorkflowExecutor(db_path)
    
    def get_db_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def get_available_workflows(self) -> List[Dict[str, Any]]:
        """Get list of all available workflows."""
        with self.get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, active, created_at FROM Workflows ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_workflow_details(self, workflow_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed workflow information including nodes and connections."""
        return self.executor.fetch_workflow(workflow_id)
    
    def create_workflow_graph(self, workflow_data: Dict[str, Any]) -> go.Figure:
        """Create an interactive graph visualization of the workflow."""
        nodes = workflow_data['nodes']
        connections = workflow_data['connections']
        
        if not nodes:
            # Return empty graph if no nodes
            fig = go.Figure()
            fig.add_annotation(
                text="No nodes found in this workflow",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Create node positions (use stored positions or generate layout)
        node_positions = {}
        for node in nodes:
            if node['position']:
                pos = json.loads(node['position'])
                node_positions[node['id']] = (pos['x'], pos['y'])
            else:
                # Default position if not stored
                node_positions[node['id']] = (100, 100)
        
        # Prepare data for plotting
        node_x = []
        node_y = []
        node_text = []
        node_ids = []
        node_colors = []
        
        # Color mapping for different node types
        type_colors = {
            'Trigger': '#FF6B6B',      # Red
            'Command': '#4ECDC4',      # Teal
            'Constant': '#45B7D1',     # Blue
            'LLM': '#96CEB4',          # Green
            'Conditional': '#FFEAA7',  # Yellow
            'Manual': '#DDA0DD'        # Plum
        }
        
        for node in nodes:
            node_x.append(node_positions[node['id']][0])
            node_y.append(node_positions[node['id']][1])
            node_text.append(f"{node['name']}<br>Type: {node['type']}")
            node_ids.append(node['id'])
            node_colors.append(type_colors.get(node['type'], '#CCCCCC'))
        
        # Create edges
        edge_x = []
        edge_y = []
        
        for conn in connections:
            from_node = next((n for n in nodes if n['id'] == conn['from_node_id']), None)
            to_node = next((n for n in nodes if n['id'] == conn['to_node_id']), None)
            
            if from_node and to_node:
                from_pos = node_positions[from_node['id']]
                to_pos = node_positions[to_node['id']]
                
                edge_x.extend([from_pos[0], to_pos[0], None])
                edge_y.extend([from_pos[1], to_pos[1], None])
        
        # Create the graph
        fig = go.Figure()
        
        # Add edges
        if edge_x:
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines',
                name='Connections'
            ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=50,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            text=[node['name'] for node in nodes],
            textposition="middle center",
            textfont=dict(size=10, color='white'),
            customdata=node_ids,
            hovertemplate='<b>%{text}</b><br>Type: %{customdata}<extra></extra>',
            name='Nodes'
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"Workflow: {workflow_data['workflow']['name']}",
                font=dict(size=16)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='#2E86AB', size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        return fig

def main():
    """Main Streamlit application."""
    st.title("🔄 AI8N Workflow Visualizer")
    st.markdown("---")
    
    # Initialize the visualizer
    visualizer = WorkflowVisualizer()
    
    # Sidebar for workflow selection
    st.sidebar.header("Workflow Selection")
    
    # Get available workflows
    workflows = visualizer.get_available_workflows()
    
    if not workflows:
        st.error("No workflows found in the database.")
        st.info("Create some workflows first using the workflow creation scripts.")
        return
    
    # Create workflow selection dropdown
    workflow_options = {f"{wf['name']} (ID: {wf['id']})": wf['id'] for wf in workflows}
    selected_workflow_name = st.sidebar.selectbox(
        "Select a workflow:",
        options=list(workflow_options.keys()),
        index=0
    )
    
    selected_workflow_id = workflow_options[selected_workflow_name]
    
    # Get workflow details
    workflow_data = visualizer.get_workflow_details(selected_workflow_id)
    
    if not workflow_data:
        st.error(f"Could not load workflow {selected_workflow_id}")
        return
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Workflow Graph")
        
        # Create and display the graph
        fig = visualizer.create_workflow_graph(workflow_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Workflow Details")
        
        # Display workflow information
        workflow = workflow_data['workflow']
        st.write(f"**Name:** {workflow['name']}")
        st.write(f"**ID:** {workflow['id']}")
        st.write(f"**Active:** {'Yes' if workflow['active'] else 'No'}")
        st.write(f"**Created:** {workflow['created_at']}")
        
        st.markdown("---")
        
        # Display nodes information
        st.subheader("Nodes")
        nodes = workflow_data['nodes']
        
        if nodes:
            for i, node in enumerate(nodes, 1):
                with st.expander(f"{i}. {node['name']} ({node['type']})"):
                    st.write(f"**ID:** {node['id']}")
                    st.write(f"**Type:** {node['type']}")
                    
                    if node['parameters']:
                        try:
                            params = json.loads(node['parameters'])
                            st.write("**Parameters:**")
                            st.json(params)
                        except json.JSONDecodeError:
                            st.write(f"**Parameters:** {node['parameters']}")
                    
                    if node['position']:
                        try:
                            pos = json.loads(node['position'])
                            st.write(f"**Position:** x={pos['x']}, y={pos['y']}")
                        except json.JSONDecodeError:
                            st.write(f"**Position:** {node['position']}")
        else:
            st.write("No nodes found in this workflow.")
        
        st.markdown("---")
        
        # Display connections information
        st.subheader("Connections")
        connections = workflow_data['connections']
        
        if connections:
            for i, conn in enumerate(connections, 1):
                st.write(f"{i}. {conn['from_node_name']} → {conn['to_node_name']}")
        else:
            st.write("No connections found in this workflow.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**AI8N Workflow System** | Built with Streamlit | "
        f"Total workflows: {len(workflows)}"
    )

if __name__ == "__main__":
    main()
