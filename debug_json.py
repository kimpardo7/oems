import json

# Read the file and try to parse it
with open('Lexus.json', 'r') as f:
    content = f.read()

print(f"File length: {len(content)}")
print(f"Character at position 58556: '{content[58555]}'")
print(f"Characters around position 58556:")
print(repr(content[58550:58565]))

# Try to find the issue by looking for common JSON problems
lines = content.split('\n')
print(f"Total lines: {len(lines)}")

# Check around line 1515
for i in range(1510, 1520):
    if i < len(lines):
        print(f"Line {i+1}: {repr(lines[i])}")

# Try to find unmatched brackets
bracket_count = 0
for i, char in enumerate(content):
    if char == '{':
        bracket_count += 1
    elif char == '}':
        bracket_count -= 1
        if bracket_count < 0:
            print(f"Unmatched closing bracket at position {i}")
            break

print(f"Final bracket count: {bracket_count}")

# Try to find the issue by looking for missing commas
import re
# Look for patterns like "}\n    " (missing comma)
pattern = r'}\s*\n\s*"[A-Z]'
matches = list(re.finditer(pattern, content))
if matches:
    print(f"Found {len(matches)} potential missing commas:")
    for match in matches:
        start = max(0, match.start() - 20)
        end = min(len(content), match.end() + 20)
        print(f"Position {match.start()}: {repr(content[start:end])}")
