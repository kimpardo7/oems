import json
import sys

try:
    with open('Lexus.json', 'r') as f:
        data = json.load(f)
    
    with open('Lexus.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("✅ JSON file fixed successfully!")
    print(f"Total dealers: {data['total_dealers']}")
    print(f"States: {len(data['states'])}")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON Error: {e}")
    print(f"Error at line {e.lineno}, column {e.colno}")
    
    # Try to find the issue
    with open('Lexus.json', 'r') as f:
        lines = f.readlines()
    
    if e.lineno <= len(lines):
        print(f"Problem line: {lines[e.lineno-1].strip()}")
        if e.lineno > 1:
            print(f"Previous line: {lines[e.lineno-2].strip()}")
        if e.lineno < len(lines):
            print(f"Next line: {lines[e.lineno].strip()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
