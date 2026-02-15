import sys
import os

# Add the current directory to sys.path so we can import src
sys.path.append(os.getcwd())

from src.index import app

print("URL Rules:")
for rule in app.url_map.iter_rules():
    print(f"{rule} {rule.methods}")
