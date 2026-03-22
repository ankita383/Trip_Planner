import requests

BASE_URL = "http://127.0.0.1:8000"

# UI Helper functions for clear console interaction
def divider(char="─", width=60):
    print(char * width)


def header(text):
    divider("═")
    print(f"  {text}")
    divider("═")


def section(text):
    print(f"\n{'─'*60}")
    print(f"  {text}")
    print(f"{'─'*60}")


# API interaction functions
def post(endpoint, payload):
    try:
        resp = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to server at {BASE_URL}")
        print("Make sure uvicorn is running:  python -m uvicorn app.main:app --reload")
        exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] {e.response.status_code}: {e.response.text}")
        exit(1)


def ask(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else default


def ask_yes_no(prompt):
    while True:
        answer = input(f"{prompt} (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        print("  Please enter yes or no.")



def handle_clarification(data, thread_id):
    """Ask user for missing nights/budget and call /clarify."""
    section("CLARIFICATION NEEDED")
    print(f"\n  {data['question']}\n")

    payload = {"thread_id": thread_id}

    if "nights" in data.get("missing_fields", []):
        while True:
            try:
                payload["nights"] = int(ask("  Number of nights"))
                break
            except (ValueError, TypeError):
                print("  Please enter a valid number.")

    if "budget" in data.get("missing_fields", []):
        while True:
            try:
                payload["budget"] = float(ask("  Total budget (INR)"))
                break
            except (ValueError, TypeError):
                print("  Please enter a valid number.")

    print("\n  Resuming planning...")
    return post("/clarify", payload)


def handle_review(data, thread_id):
    """Show agent output and ask for approve/reject."""
    pending = data.get("pending_review", {})
    agent = pending.get("agent", "Agent")
    message = pending.get("message", "")

    section(f"REVIEW — {agent}")
    print(f"\n{message}\n")

    approved = ask_yes_no("  Approve this result?")

    if approved:
        preference = ask("  Add a preference note (optional, press Enter to skip)", default="")
        payload = {
            "thread_id": thread_id,
            "approved": True,
            "preference": preference if preference else None
        }
        print("\n  Approved. Continuing...\n")
    else:
        feedback = ask("  Enter feedback for the agent")
        payload = {
            "thread_id": thread_id,
            "approved": False,
            "feedback": feedback
        }
        print(f"\n  Rejected. Re-running {agent} with your feedback...\n")

    return post("/resume", payload)


def handle_complete(data):
    """Print the final travel plan."""
    header("YOUR TRAVEL PLAN")
    plan = data.get("plan", [])
    for entry in plan:
        agent = entry.get("agent", "Unknown")
        message = entry.get("message", "")
        print(f"\n[{agent}]\n{message}")
    divider("═")
    print("  Planning complete!")
    divider("═")



def main():
    header("TRAVEL PLANNER — Multi-Agent CLI")

    query = ask("\n  Where would you like to go? (describe your trip)")
    if not query:
        print("No query provided. Exiting.")
        return

    print("\n  Starting plan...\n")
    data = post("/generate-plan", {"user_query": query})
    thread_id = data.get("thread_id")

    while True:
        status = data.get("status")

        if status == "clarification_needed":
            data = handle_clarification(data, thread_id)

        elif status == "awaiting_review":
            data = handle_review(data, thread_id)

        elif status == "complete":
            handle_complete(data)
            break

        else:
            print(f"\n[ERROR] Unexpected status: {status}")
            print(data)
            break


if __name__ == "__main__":
    main()