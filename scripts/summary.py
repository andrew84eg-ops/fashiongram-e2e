"""Turn a JUnit XML result file into a short Markdown summary for the CI run page.

Usage: python scripts/summary.py reports/junit.xml
"""

import sys
import xml.etree.ElementTree as ET


def main(path: str) -> None:
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        print("## E2E tests\n\nNo results file was produced. Check the job log.")
        return

    passed = failed = expected_failures = skipped = 0
    failures: list[str] = []
    known: list[str] = []
    for case in root.iter("testcase"):
        name = f"{case.get('classname', '')}::{case.get('name', '')}"
        skip = case.find("skipped")
        if case.find("failure") is not None or case.find("error") is not None:
            failed += 1
            failures.append(name)
        elif skip is not None and (skip.get("type") == "pytest.xfail" or "xfail" in (skip.get("message") or "")):
            expected_failures += 1
            known.append(skip.get("message") or name)
        elif skip is not None:
            skipped += 1
        else:
            passed += 1

    status = "All checks passed" if failed == 0 else f"{failed} failing"
    print(f"## E2E tests: {status}\n")
    print("| Passed | Failed | Known defects (expected failures) | Skipped |")
    print("| --- | --- | --- | --- |")
    print(f"| {passed} | {failed} | {expected_failures} | {skipped} |\n")
    if failures:
        print("### Failing\n")
        for name in failures:
            print(f"- `{name}`")
        print()
    if known:
        print("### Known defects still open (see BUG_REPORTS.md)\n")
        for message in known:
            print(f"- {message}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "reports/junit.xml")
