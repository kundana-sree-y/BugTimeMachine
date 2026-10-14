import sys

execution_history = []

def trace_execution(frame, event, arg):
    if frame.f_code.co_name != "calculate_total":
        return trace_execution
    if event == "line":
        variables = {
            name: repr(value)
            for name, value in frame.f_locals.items()
        }
        execution_history.append({
            "line": frame.f_lineno,
            "variables": variables
        })

    elif event == "exception":
        error_type, error_value, _ = arg

        execution_history.append({
            "line": frame.f_lineno,
            "error": f"{error_type.__name__}: {error_value}"
        })

    return trace_execution


def calculate_total(price, quantity, discount):
    subtotal = price * quantity
    total = subtotal + discount  # Intentional bug!
    return total


def investigate_bug(price, quantity, discount, actual, expected):
    subtotal = price * quantity
    correct_total = subtotal - discount

    print("\n===== AUTOMATED BUG ANALYSIS =====")

    if actual != expected and actual != correct_total:
        print("Suspicious calculation detected!")
        print("Calculation used: subtotal + discount")
        print("Expected calculation: subtotal - discount")
        print("Correct total:", correct_total)
        print("Fault location: total calculation")
    elif actual == expected:
        print("No output mismatch detected.")
    else:
        print("Output mismatch found; cause needs further investigation.")


#Run the program with execution tracing enabled
sys.settrace(trace_execution)

try:
    actual = calculate_total(500, 1, 100)
finally:
    sys.settrace(None)

expected = 400
investigate_bug(500, 1, 100, actual, expected)

print("==== BUG TIME MACHINE ====")
print("Expected total:", expected)
print("Actual total:", actual)

print("\n==== EXECUTION TIMELINE ====")

for step, event in enumerate(execution_history, start=1):
    print(f"\nStep {step}: Line {event['line']}")

    if "variabes" in event:
        for name, value in event["variables"].items():
            print(f"  {name} = {value}")
    if "error" in event:
        print(" Eror:", event["error"])

if actual != expected:
    print("\n==== BUG INVESTIGATION REPORT ====")
    print("Expected Output:",expected)
    print("Actual Output:", actual)
    print("Difference:", actual - expected)

    print("\nRecorded Variable History:")

    for  step in execution_history:
        if "variables" in step:
            print("Line:", step["line"])

            for name, value in step["variables"].items():
                print(f"  {name} = {value}")

    print("\nPossible Cause:")
    print("Check the calculation of the total.")