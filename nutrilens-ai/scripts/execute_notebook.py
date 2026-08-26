import os
import sys
import io
import json
import base64
import contextlib
import traceback

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def execute_notebook():
    notebook_path = os.path.join("notebooks", "NutriLens_AI_Model.ipynb")
    if not os.path.exists(notebook_path):
        print(f"Error: Notebook not found at {notebook_path}")
        return

    print(f"Loading notebook: {notebook_path}")
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Global execution namespace
    ns = {
        "__name__": "__main__",
        "__file__": notebook_path,
    }

    # Set working directory to notebooks/ folder during execution so relative paths match
    orig_cwd = os.getcwd()
    notebooks_dir = os.path.abspath("notebooks")
    os.chdir(notebooks_dir)

    execution_count = 1

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        plt = None

    for i, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") != "code":
            continue

        source_lines = cell.get("source", [])
        code_str = "".join(source_lines)
        if not code_str.strip():
            continue

        print(f"--> Executing Cell {execution_count} (index {i})...")
        cell["execution_count"] = execution_count
        cell["outputs"] = []

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        # Custom Matplotlib show interceptor
        captured_images = []
        def custom_show(*args, **kwargs):
            if plt and plt.get_fignums():
                img_buf = io.BytesIO()
                plt.savefig(img_buf, format="png", bbox_inches="tight", dpi=150)
                plt.close("all")
                img_buf.seek(0)
                b64_data = base64.b64encode(img_buf.read()).decode("utf-8")
                captured_images.append(b64_data)

        if plt:
            plt.show = custom_show

        try:
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                # Execute the code in the shared global namespace
                exec(code_str, ns)

                # If there are any un-shown figures in plt, save them
                if plt and plt.get_fignums():
                    custom_show()

            out_text = stdout_buf.getvalue()
            err_text = stderr_buf.getvalue()

            if out_text:
                lines = [l + "\n" for l in out_text.splitlines()]
                if out_text.endswith("\n"):
                    lines[-1] = lines[-1].rstrip("\n") + "\n"
                cell["outputs"].append({
                    "output_type": "stream",
                    "name": "stdout",
                    "text": [l if l.endswith("\n") else l + "\n" for l in out_text.split("\n")[:-1]] or [out_text]
                })

            if err_text:
                cell["outputs"].append({
                    "output_type": "stream",
                    "name": "stderr",
                    "text": [l if l.endswith("\n") else l + "\n" for l in err_text.split("\n")[:-1]] or [err_text]
                })

            for b64_img in captured_images:
                cell["outputs"].append({
                    "output_type": "display_data",
                    "data": {
                        "image/png": b64_img,
                        "text/plain": ["<Figure size ...>"]
                    },
                    "metadata": {}
                })

            print(f"    [OK] Cell {execution_count} executed successfully.")

        except Exception as e:
            tb = traceback.format_exc()
            print(f"    [ERROR] Error in Cell {execution_count}: {e}")
            cell["outputs"].append({
                "output_type": "error",
                "ename": type(e).__name__,
                "evalue": str(e),
                "traceback": tb.splitlines()
            })

        execution_count += 1

    os.chdir(orig_cwd)

    # Save executed notebook
    print(f"Saving executed notebook with live outputs to {notebook_path}...")
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print("[SUCCESS] Successfully executed and populated all outputs in NutriLens_AI_Model.ipynb!")

if __name__ == "__main__":
    execute_notebook()
