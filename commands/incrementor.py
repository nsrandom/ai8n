#!/usr/bin/env python3
"""
Command script that increments a value by 1.
Reads input_data from INPUT_DATA environment variable and returns the incremented value.
"""

import json
import os
import sys


def main():
    """Main function that increments the value from input_data by 1."""
    try:
        # Get input data from environment variable
        input_data_str = os.environ.get('INPUT_DATA', '{}')
        input_data = json.loads(input_data_str)
        
        # Get the value to increment
        value = input_data.get('value')
        if value is None:
            print("Error: 'value' key not found in input_data", file=sys.stderr)
            sys.exit(1)
        
        # Ensure value is numeric
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            print(f"Error: 'value' must be numeric, got: {value}", file=sys.stderr)
            sys.exit(1)
        
        # Increment the value by 1
        incremented_value = numeric_value + 1
        
        # Return the result as JSON
        result = {
            'value': incremented_value,
        }
        
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in INPUT_DATA: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
