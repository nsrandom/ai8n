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
    
    def get_workflow_executions(self, workflow_id: int) -> List[Dict[str, Any]]:
        """Get list of executions for a specific workflow."""
        with self.get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, status, started_at, ended_at, input, output, error
                FROM WorkflowExecutions 
                WHERE workflow_id = ? 
                ORDER BY started_at DESC
            """, (workflow_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_execution_details(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed execution information including node executions."""
        with self.get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get workflow execution details
            cursor.execute("""
                SELECT we.*, w.name as workflow_name
                FROM WorkflowExecutions we
                JOIN Workflows w ON we.workflow_id = w.id
                WHERE we.id = ?
            """, (execution_id,))
            execution = cursor.fetchone()
            
            if not execution:
                return None
            
            # Get node executions with node details
            cursor.execute("""
                SELECT ne.*, n.name as node_name, n.type as node_type
                FROM NodeExecutions ne
                JOIN Nodes n ON ne.node_id = n.id
                WHERE ne.workflow_execution_id = ?
                ORDER BY ne.started_at
            """, (execution_id,))
            node_executions = [dict(row) for row in cursor.fetchall()]
            
            return {
                'execution': dict(execution),
                'node_executions': node_executions
            }
    
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
    
    def create_execution_flow_graph(self, execution_data: Dict[str, Any], workflow_data: Dict[str, Any]) -> go.Figure:
        """Create an execution flow visualization showing node execution status and data flow."""
        execution = execution_data['execution']
        node_executions = execution_data['node_executions']
        workflow_nodes = workflow_data['nodes']
        connections = workflow_data['connections']
        
        if not workflow_nodes:
            fig = go.Figure()
            fig.add_annotation(
                text="No nodes found in this workflow",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Create node lookup for execution data
        node_execution_lookup = {ne['node_id']: ne for ne in node_executions}
        
        # Create node positions (use stored positions or generate layout)
        node_positions = {}
        for node in workflow_nodes:
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
        node_sizes = []
        
        # Color mapping for different node types and execution status
        type_colors = {
            'Trigger': '#FF6B6B',      # Red
            'Command': '#4ECDC4',      # Teal
            'Constant': '#45B7D1',     # Blue
            'LLM': '#96CEB4',          # Green
            'Conditional': '#FFEAA7',  # Yellow
            'Manual': '#DDA0DD'        # Plum
        }
        
        # Status color mapping
        status_colors = {
            'completed': '#28a745',    # Green
            'running': '#ffc107',      # Yellow
            'failed': '#dc3545',       # Red
            'pending': '#6c757d'       # Gray
        }
        
        for node in workflow_nodes:
            node_x.append(node_positions[node['id']][0])
            node_y.append(node_positions[node['id']][1])
            
            # Get execution status for this node
            node_exec = node_execution_lookup.get(node['id'])
            if node_exec:
                status = node_exec['status']
                status_color = status_colors.get(status, '#6c757d')
                node_text.append(f"{node['name']}<br>Type: {node['type']}<br>Status: {status}")
                node_colors.append(status_color)
                node_sizes.append(60)  # Larger for executed nodes
            else:
                node_text.append(f"{node['name']}<br>Type: {node['type']}<br>Status: Not executed")
                node_colors.append(type_colors.get(node['type'], '#CCCCCC'))
                node_sizes.append(50)  # Normal size for non-executed nodes
            
            node_ids.append(node['id'])
        
        # Create edges
        edge_x = []
        edge_y = []
        edge_colors = []
        
        for conn in connections:
            from_node = next((n for n in workflow_nodes if n['id'] == conn['from_node_id']), None)
            to_node = next((n for n in workflow_nodes if n['id'] == conn['to_node_id']), None)
            
            if from_node and to_node:
                from_pos = node_positions[from_node['id']]
                to_pos = node_positions[to_node['id']]
                
                # Check if both nodes were executed
                from_exec = node_execution_lookup.get(from_node['id'])
                to_exec = node_execution_lookup.get(to_node['id'])
                
                if from_exec and to_exec and from_exec['status'] == 'completed' and to_exec['status'] == 'completed':
                    edge_color = '#28a745'  # Green for successful data flow
                else:
                    edge_color = '#888'  # Gray for non-executed or failed
                
                edge_x.extend([from_pos[0], to_pos[0], None])
                edge_y.extend([from_pos[1], to_pos[1], None])
                edge_colors.append(edge_color)
        
        # Create the graph
        fig = go.Figure()
        
        # Add edges
        if edge_x:
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=3, color='#888'),
                hoverinfo='none',
                mode='lines',
                name='Connections'
            ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            text=[node['name'] for node in workflow_nodes],
            textposition="middle center",
            textfont=dict(size=10, color='white'),
            customdata=node_ids,
            hovertemplate='<b>%{text}</b><br>Type: %{customdata}<extra></extra>',
            name='Nodes'
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"Execution Flow: {execution['workflow_name']} (ID: {execution['id']})",
                font=dict(size=16)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text=f"Status: {execution['status']} | Started: {execution['started_at']}",
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
    
    # Add workflow execution section
    st.sidebar.markdown("---")
    st.sidebar.subheader("Execute Workflow")
    
    # Input data form
    with st.sidebar.form("execute_workflow_form"):
        st.write("**Input Data (JSON):**")
        default_input = '{"value": 42, "test": "data"}'
        input_data_text = st.text_area(
            "Input JSON:",
            value=default_input,
            height=100,
            help="Enter JSON data to pass as input to the workflow"
        )
        
        execute_button = st.form_submit_button("🚀 Execute Workflow", use_container_width=True)
    
    # Handle workflow execution
    if execute_button:
        try:
            # Parse input data
            if input_data_text.strip():
                input_data = json.loads(input_data_text)
            else:
                input_data = {}
            
            # Execute the workflow
            with st.spinner("Executing workflow..."):
                result = visualizer.executor.run_workflow(selected_workflow_id, input_data)
            
            if result.get('success', False):
                st.sidebar.success("✅ Workflow executed successfully!")
                st.sidebar.json(result)
                
                # Refresh the page to show the new execution
                st.rerun()
            else:
                st.sidebar.error(f"❌ Workflow execution failed: {result.get('error', 'Unknown error')}")
                
        except json.JSONDecodeError as e:
            st.sidebar.error(f"❌ Invalid JSON input: {str(e)}")
        except Exception as e:
            st.sidebar.error(f"❌ Execution error: {str(e)}")

    # Add execution viewing section
    st.sidebar.markdown("---")
    st.sidebar.subheader("Execution History")
    
    # Get executions for the selected workflow
    executions = visualizer.get_workflow_executions(selected_workflow_id)
    
    if executions:
        execution_options = {f"Exec #{exec['id']} - {exec['status']} ({exec['started_at']})": exec['id'] for exec in executions}
        selected_execution_name = st.sidebar.selectbox(
            "Select an execution:",
            options=list(execution_options.keys()),
            index=0
        )
        selected_execution_id = execution_options[selected_execution_name]
        
        # Get execution details
        execution_data = visualizer.get_execution_details(selected_execution_id)
    else:
        st.sidebar.info("No executions found for this workflow.")
        execution_data = None
        selected_execution_id = None

    # Main content area
    if execution_data:
        # Show execution view
        col_title, col_exec = st.columns([3, 1])
        with col_title:
            st.subheader("Execution Flow")
        with col_exec:
            if st.button("🔄 Refresh Executions", help="Refresh the execution list"):
                st.rerun()
        
        # Create and display the execution flow graph
        fig = visualizer.create_execution_flow_graph(execution_data, workflow_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show execution details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Node Execution Details")
            
            # Display node executions
            node_executions = execution_data['node_executions']
            if node_executions:
                for i, ne in enumerate(node_executions, 1):
                    with st.expander(f"{i}. {ne['node_name']} ({ne['node_type']}) - {ne['status']}"):
                        st.write(f"**Node ID:** {ne['node_id']}")
                        st.write(f"**Status:** {ne['status']}")
                        st.write(f"**Started:** {ne['started_at']}")
                        st.write(f"**Ended:** {ne['ended_at']}")
                        
                        if ne['input']:
                            try:
                                input_data = json.loads(ne['input']) if isinstance(ne['input'], str) else ne['input']
                                st.write("**Input Data:**")
                                st.json(input_data)
                            except json.JSONDecodeError:
                                st.write(f"**Input Data:** {ne['input']}")
                        
                        if ne['output']:
                            try:
                                output_data = json.loads(ne['output']) if isinstance(ne['output'], str) else ne['output']
                                st.write("**Output Data:**")
                                st.json(output_data)
                            except json.JSONDecodeError:
                                st.write(f"**Output Data:** {ne['output']}")
                        
                        if ne['error']:
                            st.error(f"**Error:** {ne['error']}")
            else:
                st.write("No node executions found.")
        
        with col2:
            st.subheader("Execution Summary")
            
            execution = execution_data['execution']
            st.write(f"**Execution ID:** {execution['id']}")
            st.write(f"**Status:** {execution['status']}")
            st.write(f"**Started:** {execution['started_at']}")
            st.write(f"**Ended:** {execution['ended_at']}")
            
            if execution['input']:
                try:
                    input_data = json.loads(execution['input']) if isinstance(execution['input'], str) else execution['input']
                    st.write("**Initial Input:**")
                    st.json(input_data)
                except json.JSONDecodeError:
                    st.write(f"**Initial Input:** {execution['input']}")
            
            if execution['error']:
                st.error(f"**Error:** {execution['error']}")
            
            st.markdown("---")
            st.subheader("Workflow Structure")
            
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
    else:
        # Show regular workflow view
        col1, col2 = st.columns([2, 1])
        
        with col1:
            col_title, col_exec = st.columns([3, 1])
            with col_title:
                st.subheader("Workflow Graph")
            with col_exec:
                if st.button("🚀 Execute Now", help="Execute this workflow with default input"):
                    try:
                        with st.spinner("Executing workflow..."):
                            result = visualizer.executor.run_workflow(selected_workflow_id, {"value": 42})
                        if result.get('success', False):
                            st.success("✅ Workflow executed successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Execution failed: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Execution error: {str(e)}")
            
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
