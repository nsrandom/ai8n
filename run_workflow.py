#!/usr/bin/env python3
"""
Command line interface for running workflows.
"""

import json
import logging
import argparse
import sys
from model.workflow import WorkflowExecutor

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run a workflow by its ID with optional initial input data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_workflow.py                    # Run workflow 1 with no input
  python run_workflow.py --workflow-id 2    # Run workflow 2 with no input
  python run_workflow.py --workflow-id 1 --input '{"key": "value"}'  # Run workflow 1 with input data
  python run_workflow.py -w 3 -i '{"name": "test", "count": 42}'     # Run workflow 3 with input data
        """
    )
    
    parser.add_argument(
        '--workflow-id', '-w',
        type=int,
        default=1,
        help='ID of the workflow to execute (default: 1)'
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Initial input data as JSON string (optional)'
    )
    
    parser.add_argument(
        '--db-path', '-d',
        type=str,
        default='data/ai8n.db',
        help='Path to the database file (default: data/ai8n.db)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse input data if provided
    initial_input = None
    if args.input:
        try:
            initial_input = json.loads(args.input)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input data: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Create executor with custom database path
    executor = WorkflowExecutor(args.db_path)
    
    # Run the workflow
    print(f"Running workflow {args.workflow_id}...")
    if initial_input:
        print(f"Initial input: {json.dumps(initial_input, indent=2)}")
    
    result = executor.run_workflow(args.workflow_id, initial_input)
    
    # Print the result
    print("\nWorkflow execution result:")
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    if result.get('success', False):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
