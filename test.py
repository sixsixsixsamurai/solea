#!/usr/bin/env python3
"""
Solea test runner.

Usage:
  python test.py                 — run all tests
  python test.py apps.orders     — run one app
  NO_COLOR=1 python test.py      — disable colours (e.g. in CI)
"""
import os, re, subprocess, sys
from pathlib import Path

# ── colour helpers ────────────────────────────────────────────────────────────
_TTY = sys.stdout.isatty() and not os.environ.get('NO_COLOR')

def _c(code, t): return f'\033[{code}m{t}\033[0m' if _TTY else t
green  = lambda t: _c('92', t)
red    = lambda t: _c('91', t)
yellow = lambda t: _c('93', t)
bold   = lambda t: _c('1',  t)
dim    = lambda t: _c('2',  t)
cyan   = lambda t: _c('96', t)

# ── find Python ───────────────────────────────────────────────────────────────
ROOT    = Path(__file__).resolve().parent
BACKEND = ROOT / 'backend'

def _find_python() -> str:
    in_venv = hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix
    if in_venv:
        return sys.executable

    scripts = 'Scripts' if sys.platform == 'win32' else 'bin'
    exe     = 'python.exe' if sys.platform == 'win32' else 'python'
    for name in ('venv', '.venv'):
        p = ROOT / name / scripts / exe
        if p.exists():
            return str(p)

    return sys.executable   # hope it's on PATH

# ── constants ─────────────────────────────────────────────────────────────────
W        = 52
SETTINGS = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# ── run ───────────────────────────────────────────────────────────────────────
def main() -> None:
    python  = _find_python()
    targets = sys.argv[1:]

    cmd = [python, 'manage.py', 'test', '-v', '2', f'--settings={SETTINGS}'] + targets

    print()
    print(cyan(bold('─' * W)))
    print(bold(cyan('  SOLEA') + '  Test Suite'))
    print(cyan(bold('─' * W)))
    print(dim('  Running…\n'))
    sys.stdout.flush()

    proc     = subprocess.run(cmd, capture_output=True, text=True, cwd=str(BACKEND), input='yes\n')
    combined = proc.stderr + proc.stdout

    # ── parse per-test lines ──────────────────────────────────────────────────
    # Django -v 2 format:  "test_name (module.Class) ... ok"
    pat = re.compile(r'\(([^)]+)\)\s+\.\.\.\s+(ok|FAIL|ERROR|skip)', re.MULTILINE)

    by_app: dict[str, dict[str, int]] = {}
    for m in pat.finditer(combined):
        dotted, status = m.group(1), m.group(2)
        parts = dotted.split('.')
        app   = '.'.join(parts[:2]) if len(parts) >= 2 else dotted
        if app not in by_app:
            by_app[app] = {'ok': 0, 'fail': 0, 'error': 0, 'skip': 0}
        by_app[app][{'ok': 'ok', 'FAIL': 'fail', 'ERROR': 'error', 'skip': 'skip'}[status]] += 1

    # ── per-app table ─────────────────────────────────────────────────────────
    if by_app:
        col_w = max(len(k) for k in by_app) + 2
        for app in sorted(by_app):
            c      = by_app[app]
            total  = sum(c.values())
            failed = c['fail'] + c['error']
            icon   = green('✓') if not failed else red('✗')
            count  = f'{c["ok"]}/{total}'
            fail_note = f'  {red(f"({failed} failed)")}' if failed else ''
            skip_note = f'  {yellow("(" + str(c["skip"]) + " skipped)")}' if c['skip'] else ''
            note      = fail_note + skip_note
            print(f'  {bold(app.ljust(col_w))}  {icon}   {count}{note}')
    else:
        print(red('  Could not collect tests. Raw output:'))
        for line in combined.splitlines():
            if line.strip():
                print(f'    {dim(line)}')

    # ── totals ────────────────────────────────────────────────────────────────
    m_total  = re.search(r'Ran (\d+) tests? in ([\d.]+)s', combined)
    total_n  = int(m_total.group(1)) if m_total else 0
    duration = m_total.group(2)      if m_total else '?'
    failures = len(re.findall(r'\.\.\. (?:FAIL|ERROR)', combined))
    passed   = total_n - failures

    print()
    print(cyan(bold('─' * W)))
    if total_n == 0:
        status_line = yellow(bold('  ⚠  No tests found'))
    elif failures == 0:
        status_line = green(bold(f'  ✓  {passed}/{total_n} passed'))
    else:
        status_line = red(bold(f'  ✗  {passed} passed,  {failures} failed'))
    print(f'{status_line}   {dim("⏱  " + duration + "s")}')
    print(cyan(bold('─' * W)))
    print()

    # ── failure details ───────────────────────────────────────────────────────
    if failures:
        print(red(bold('  Failed tests:')))
        for line in combined.splitlines():
            if re.match(r'^(FAIL|ERROR): ', line):
                print(f'  {red("✗")} {line[line.index(":")+2:]}')
        print()

    sys.exit(proc.returncode)


if __name__ == '__main__':
    main()
