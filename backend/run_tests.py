#!/usr/bin/env python3
import subprocess
import re
import sys

result = subprocess.run(
    [
        '/home/solea/venv/bin/python', 'manage.py', 'test', '-v', '2',
        '--settings=config.settings.development',
    ],
    capture_output=True, text=True
)

combined = result.stderr + result.stdout

# Print only test result lines and the separator/summary
for line in combined.splitlines():
    stripped = line.strip()
    if re.search(r'\.\.\. (ok|FAIL|ERROR|skip)', stripped):
        print(line)
    elif stripped.startswith('---') or stripped.startswith('==='):
        print(line)
    elif re.match(r'Ran \d+ tests?', stripped):
        print(line)
    elif stripped in ('OK', 'FAILED'):
        print(stripped)

match = re.search(r'Ran (\d+) tests? in ([\d.]+)s', combined)
if match:
    total = int(match.group(1))
    duration = match.group(2)
    failures = len(re.findall(r'\.\.\. (FAIL|ERROR)', combined))
    passed = total - failures

    print()
    print('=' * 50)
    print(f'  Total tests : {total}')
    print(f'  Passed      : {passed}')
    print(f'  Failed      : {failures}')
    print(f'  Time        : {duration} s')
    print('=' * 50)

sys.exit(result.returncode)
