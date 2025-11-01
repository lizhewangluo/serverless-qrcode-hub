#!/usr/bin/env python3
"""
Taokouling Float Tool - Windows always-on-top floating desktop app
"""

import sys
import os
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import TaokoulingApp

def main():
    """Main entry point"""
    try:
        # Create Qt application
        app = TaokoulingApp(sys.argv)
        
        # Run the application
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        print("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.exception(f"Fatal error: {str(e)}")
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()