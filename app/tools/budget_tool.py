from langchain_core.tools import tool


@tool
def calculate_budget_manual(
    flight_cost: float,
    hotel_cost: float,
    budget_limit: float
):
    """
    Calculate total travel cost.
    """

    total = flight_cost + hotel_cost

    status = "Approved" if total <= budget_limit else "Rejected"

    return {
        "total": total,
        "status": status
    }
