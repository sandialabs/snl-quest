import os
import sys
from pathlib import Path

dirname = Path(__file__).resolve().parent
def get_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return base_path