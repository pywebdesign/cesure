#!/usr/bin/env python
"""
Helper script for debugging the Cesure application.

This script can be used to:
1. Set breakpoints in the code
2. Run the application with the debugger attached

Usage:
    python scripts/debug_app.py

This will start the application with debugpy listening on port 5678.
"""

import debugpy
import os
import sys
import uvicorn

# Add parent directory to path so we can import cesure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    # Enable debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("⚡ Debugger is listening on 0.0.0.0:5678")
    print("   Waiting for client to attach...")
    
    # Uncomment to pause execution until a debugger attaches
    # debugpy.wait_for_client()
    
    # Run the application
    uvicorn.run(
        "cesure.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

if __name__ == "__main__":
    main()