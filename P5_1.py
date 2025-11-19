from pathlib import Path
results_dir = Path("/results")
files = sorted([p.name for p in results_dir.glob("*")])
print("Files in results:", files)
