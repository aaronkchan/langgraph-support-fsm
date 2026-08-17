from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# 1. Define State
class SupportState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str
    refund_amount: float
    refund_status: str
    risk_level: str

# 2. Define Nodes
def classify_intent(state: SupportState):
    latest_msg = state["messages"][-1].content.lower()
    
    if "refund" in latest_msg or "charge" in latest_msg or "money back" in latest_msg:
        # Simple rule-based/deterministic parsing for the demo
        import re
        numbers = re.findall(r"\$?\d+(?:\.\d+)?", latest_msg)
        amount = float(numbers[0].replace("$", "")) if numbers else 25.0
        return {
            "intent": "refund_request",
            "refund_amount": amount,
            "risk_level": "HIGH" if amount > 50.0 else "LOW"
        }
    elif "status" in latest_msg or "where is" in latest_msg:
        return {"intent": "order_status", "risk_level": "LOW"}
    else:
        return {"intent": "general_faq", "risk_level": "LOW"}

def handle_order_status(state: SupportState):
    return {
        "messages": [AIMessage(content="Your order #10492 is currently in transit and scheduled to arrive in 2 business days.")],
        "refund_status": "NOT_APPLICABLE"
    }

def handle_faq(state: SupportState):
    return {
        "messages": [AIMessage(content="For general account inquiries or settings, you can check our documentation or reach out anytime.")],
        "refund_status": "NOT_APPLICABLE"
    }

def process_low_risk_refund(state: SupportState):
    amount = state.get("refund_amount", 0.0)
    return {
        "messages": [AIMessage(content=f"Your refund request for ${amount:.2f} has been automatically approved and processed.")],
        "refund_status": "AUTO_APPROVED"
    }

def prepare_human_review(state: SupportState):
    amount = state.get("refund_amount", 0.0)
    return {
        "messages": [AIMessage(content=f"Your refund request for ${amount:.2f} exceeds standard limits and requires manager authorization. Routing to an agent...")],
        "refund_status": "PENDING_APPROVAL"
    }

def execute_approved_refund(state: SupportState):
    amount = state.get("refund_amount", 0.0)
    return {
        "messages": [AIMessage(content=f"Human Agent Approved: A refund of ${amount:.2f} has been processed back to your card.")],
        "refund_status": "MANUALLY_APPROVED"
    }

# 3. Routing Logic
def route_by_intent(state: SupportState) -> Literal["order_status", "general_faq", "low_risk_refund", "high_risk_refund"]:
    intent = state.get("intent")
    if intent == "order_status":
        return "order_status"
    elif intent == "refund_request":
        return "high_risk_refund" if state.get("risk_level") == "HIGH" else "low_risk_refund"
    return "general_faq"

# 4. Build Graph
def build_support_fsm():
    workflow = StateGraph(SupportState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("handle_order_status", handle_order_status)
    workflow.add_node("handle_faq", handle_faq)
    workflow.add_node("process_low_risk_refund", process_low_risk_refund)
    workflow.add_node("prepare_human_review", prepare_human_review)
    workflow.add_node("execute_approved_refund", execute_approved_refund)

    workflow.add_edge(START, "classify_intent")
    
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "order_status": "handle_order_status",
            "general_faq": "handle_faq",
            "low_risk_refund": "process_low_risk_refund",
            "high_risk_refund": "prepare_human_review"
        }
    )

    workflow.add_edge("handle_order_status", END)
    workflow.add_edge("handle_faq", END)
    workflow.add_edge("process_low_risk_refund", END)
    
    # State halts at prepare_human_review until human review completes
    workflow.add_edge("prepare_human_review", "execute_approved_refund")
    workflow.add_edge("execute_approved_refund", END)

    # In-memory checkpointer enables HITL pauses
    checkpointer = MemorySaver()
    
    # Interrupt before human execution
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["execute_approved_refund"]
    )
    return app