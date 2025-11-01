#!/usr/bin/env python3
"""
Quick start script for development testing
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def main():
    """Quick start the application for development"""
    print("Starting Taokouling Float Tool (Development Mode)")
    print("=" * 50)
    
    try:
        # Try to import and run the app
        from ui import TaokoulingApp
        
        app = TaokoulingApp(sys.argv)
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nPlease install the required dependencies:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())