#!/usr/bin/env python3
"""run_experiment.py — Run or list experiments from the experiments/ directory.

Usage:
    python code/run_experiment.py                          # List all experiments
    python code/run_experiment.py experiments/v15_direction_interaction/  # Run specific experiment
    python code/run_experiment.py --latest                 # Run the latest current experiment
"""
import sys, os, yaml, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENTS_DIR = ROOT / "experiments"
MANIFEST = EXPERIMENTS_DIR / "manifest.yaml"


def load_manifest():
    with open(MANIFEST) as f:
        return yaml.safe_load(f)


def list_experiments():
    manifest = load_manifest()
    print(f"{'ID':<30} {'Ver':<8} {'Status':<12} {'Key Finding'}")
    print("─" * 100)
    for exp in manifest["experiments"]:
        print(f"{exp['id']:<30} {exp['version']:<8} {exp['status']:<12} {exp.get('key_finding', '')[:60]}")


def show_experiment(exp_dir):
    config_path = Path(exp_dir) / "config.yaml"
    if not config_path.exists():
        print(f"No config.yaml found in {exp_dir}")
        return
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    print(f"Experiment: {config['id']}")
    print(f"Version: {config['version']}")
    print(f"Title: {config['title']}")
    print(f"Status: {config['status']}")
    print(f"Date: {config['date']}")
    
    print("\n── Input Data ──")
    for category in ["primary", "supplementary"]:
        if category in config.get("input_data", {}):
            print(f"  {category.upper()}:")
            for item in config["input_data"][category]:
                exists = "✓" if (ROOT / item["path"]).exists() else "✗ MISSING"
                print(f"    [{exists}] {item['path']} — {item['description']}")
    
    print("\n── Model ──")
    if "model" in config:
        print(f"  Primary: {config['model']['primary']}")
        if "controls" in config["model"]:
            for ctrl in config["model"]["controls"]:
                print(f"  Control: {ctrl}")
    
    print("\n── Key Results ──")
    if "results" in config:
        for key, val in config["results"].items():
            if isinstance(val, dict):
                print(f"  {key}: {val}")
            else:
                print(f"  {key}: {val}")
    
    print("\n── Reproduce ──")
    if "reproduce" in config:
        for step, desc in config["reproduce"].items():
            if step == "note":
                print(f"  NOTE: {desc}")
            else:
                print(f"  {step}: {desc}")


def check_data_availability(exp_dir):
    """Check if all input data files exist for an experiment."""
    config_path = Path(exp_dir) / "config.yaml"
    if not config_path.exists():
        return
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    missing = []
    for category in ["primary", "supplementary"]:
        for item in config.get("input_data", {}).get(category, []):
            if not (ROOT / item["path"]).exists():
                missing.append(item["path"])
    
    if missing:
        print(f"\n⚠ Missing data files:")
        for m in missing:
            print(f"  ✗ {m}")
    else:
        print(f"\n✓ All input data files available")


def run_experiment(exp_dir):
    """Run an experiment — for now, validate and show what to run."""
    print(f"═══ Running Experiment: {exp_dir} ═══\n")
    show_experiment(exp_dir)
    check_data_availability(exp_dir)
    
    # Check for run script
    run_script = Path(exp_dir) / "run.py"
    if run_script.exists():
        print(f"\n▶ Found run.py — executing...")
        os.system(f"python3 {run_script}")
    else:
        print(f"\n⚠ No run.py found in {exp_dir}")
        print("  To make this experiment reproducible, create a run.py that:")
        print("  1. Loads input data from config.yaml")
        print("  2. Runs the model specification")
        print("  3. Saves results to results.json")


def find_latest():
    manifest = load_manifest()
    # Find the LAST current experiment (most recent)
    current = None
    for exp in manifest["experiments"]:
        if exp["status"] == "current":
            current = exp
    
    if not current:
        return None
    
    # Find the experiment directory
    exp_dir = EXPERIMENTS_DIR / current["id"]
    if not exp_dir.exists():
        # Try to find by scanning directories
        for d in EXPERIMENTS_DIR.iterdir():
            if d.is_dir() and (d / "config.yaml").exists():
                with open(d / "config.yaml") as f:
                    cfg = yaml.safe_load(f)
                if cfg.get("id") == current["id"]:
                    return d
    return exp_dir


if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_experiments()
    elif sys.argv[1] == "--latest":
        latest = find_latest()
        if latest:
            run_experiment(str(latest))
        else:
            print("No current experiment found")
    else:
        exp_dir = sys.argv[1]
        if not os.path.isabs(exp_dir):
            exp_dir = str(ROOT / exp_dir)
        run_experiment(exp_dir)
