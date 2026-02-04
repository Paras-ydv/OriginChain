"""
OriginChain Main Entry Point
"""

import streamlit as st
import subprocess
import sys
import os

if __name__ == "__main__":
    # Run Streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", "services/ui/app.py"])