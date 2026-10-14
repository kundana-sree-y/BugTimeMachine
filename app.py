
from flask import Flask, render_template, request, jsonify
import ast
import io
import contextlib
import sys

app = Flask(__name__)


def explain_node(node):
    if isinstance(node, ast.Assign):
        return "Python evaluates the expression and stores its result in a variable."

    if isinstance(node, ast.AugAssign):
        return "Python performs an operation and updates the variable."

    if isinstance(node, ast.If):
        return "Python checks the condition and chooses which branch to execute."

    if isinstance(node, (ast.For, ast.While)):
        return "Python repeats the loop body according to the loop rules."

    if isinstance(node, ast.FunctionDef):
        return "Python defines a function that can be called later."

    if isinstance(node, ast.Return):
        return "Python returns a value from the current function."

    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        return "Python calls a function. Printed text appears in the console."

    return "Python executes this statement."


def trace_code(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return {
            "ok": False,
            "error": (
                f"SyntaxError on line {error.lineno}: "
                f"{error.msg}"
            )
        }

    explanations = {}

    for node in ast.walk(tree):
        if hasattr(node, "lineno"):
            explanations[node.lineno] = explain_node(node)

    events = []
    output = io.StringIO()
    namespace = {"__name__": "__main__"}
    counter = {"steps": 0}

    def tracer(frame, event, arg):
        if (
            frame.f_code.co_filename == "<bugtimemachine>"
            and event == "line"
        ):
            counter["steps"] += 1

            if counter["steps"] > 1000:
                raise RuntimeError(
                    "Stopped at the 1,000-step demo limit."
                )

            values = {}

            for name, value in frame.f_locals.items():
                if name.startswith("__"):
                    continue

                try:
                    rendered = repr(value)
                except Exception:
                    rendered = f"<{type(value).__name__}>"

                if len(rendered) > 160:
                    rendered = rendered[:157] + "..."

                values[name] = rendered

            events.append({
                "line": frame.f_lineno,
                "variables": values,
                "explanation": explanations.get(
                    frame.f_lineno,
                    "Python executes this line."
                )
            })

        return tracer

    try:
        compiled_code = compile(
            tree,
            "<bugtimemachine>",
            "exec"
        )

        with contextlib.redirect_stdout(output):
            with contextlib.redirect_stderr(output):
                sys.settrace(tracer)

                try:
                    exec(compiled_code, namespace, namespace)
                finally:
                    sys.settrace(None)

        return {
            "ok": True,
            "events": events,
            "output": output.getvalue()
        }

    except Exception as error:
        return {
            "ok": False,
            "error": f"{type(error).__name__}: {error}",
            "output": output.getvalue(),
            "events": events
        }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/trace", methods=["POST"])
def trace():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")

    if not isinstance(code, str) or not code.strip():
        return jsonify({
            "ok": False,
            "error": "Please enter some Python code."
        }), 400

    if len(code) > 12000:
        return jsonify({
            "ok": False,
            "error": "Code must be under 12,000 characters."
        }), 400

    return jsonify(trace_code(code))


if __name__ == "__main__":
    app.run(debug=True)
