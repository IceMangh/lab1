"""Run the Release benchmark, record metadata and save experiment artifacts."""
import argparse
import json
from pathlib import Path
import platform
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=ROOT / "build" / ("structure_benchmarks.exe" if platform.system() == "Windows" else "structure_benchmarks"))
    parser.add_argument("--plot", action="store_true", help="Also create PNG/SVG using matplotlib")
    parser.add_argument("--import-results", action="store_true", help="Refresh artifacts from an existing measured CSV")
    args = parser.parse_args()
    result = ROOT / "benchmarks/results.csv"
    if not args.import_results:
        subprocess.run([str(args.binary.resolve()), str(result)], check=True)
    metadata = {"measured_at_utc": datetime.now(timezone.utc).isoformat(),
                "system": platform.platform(), "processor": platform.machine(),
                "build": "C++20 / CMake Release", "compiler": subprocess.check_output(["c++", "--version"], text=True).splitlines()[0],
                "repetitions": 3, "statistic": "median of each operation separately", "seed": 2026,
                "sizes": [10000, 30000, 100000, 300000, 1000000],
                "input": "unique integers 0..n-1 shuffled using mt19937",
                "operations": {"avl": ["Insert", "Contains", "Remove"], "heap": ["Push", "Top", "Pop"], "queue": ["Push", "Top", "Pop"]}}
    (ROOT / "benchmarks/environment.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n")
    if args.plot:
        subprocess.run([__import__("sys").executable, str(ROOT / "benchmarks/plot.py")],check=True)
    print("Measured data saved in benchmarks/results.csv")

if __name__ == "__main__":
    main()
