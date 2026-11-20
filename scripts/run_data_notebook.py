"""Run every code cell in 01_data.ipynb in a fresh namespace and save outputs."""
import contextlib
import io
import json
import os
from pathlib import Path
import traceback


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    path = root / "01_data.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}
    execution = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        execution += 1
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                exec(compile("".join(cell["source"]), f"01_data.ipynb cell {execution}", "exec"), namespace)
        except Exception:
            print(output.getvalue())
            traceback.print_exc()
            raise SystemExit(1)
        cell["execution_count"] = execution
        cell["outputs"] = [{
            "output_type": "stream", "name": "stdout",
            "text": output.getvalue().splitlines(keepends=True),
        }] if output.getvalue() else []
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Executed {execution} code cells successfully.")
    print(namespace["monthly_quality"].drop(columns="missing_timestamps").to_string(index=False))
    print(namespace["split_quality"].drop(columns="missing_timestamps").to_string(index=False))
    print(f"Full source checks {len(namespace['independent'])}, spot checks {len(namespace['spot_checks'])}")
    print(f"Handoff CSV changed: {namespace['run_record']['handoff_csv_changed']}")


if __name__ == "__main__":
    main()

