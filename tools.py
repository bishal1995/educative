from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")

@tool
def calculate_discount(price: float, discount_percentage: float) -> float:
    """
    Calculates the final price after applying a discount.

    IMPORTANT:
    - discount_percentage MUST be between 0 and 100
    - Values outside this range are INVALID
    - Do NOT reinterpret invalid values
    - If invalid, do NOT call this tool

    Args:
        price (float): The original price.
        discount_percentage (float): Discount percentage (0–100 only).

    Returns:
        float: Final price after discount.
    """
    if not (0 <= discount_percentage <= 100):
        raise ValueError("Discount percentage must be between 0 and 100")

    discount_amount = price * (discount_percentage / 100)
    return price - discount_amount


llm_with_tools = llm.bind_tools([calculate_discount])

hello_world = llm_with_tools.invoke("Hello world!")
print("Content:", hello_world.content, "\n")

query = """
What is the price of an item that costs $100 after a 20 percent discount?
If invalid, do NOT call the tool and explain why.
"""

result = llm_with_tools.invoke(query)

print("Content:", result.content)
print("Tool Calls:", result.tool_calls)