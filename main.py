from langchain_core.messages import HumanMessage
from state_machine import build_support_fsm

def run_demo():
    app = build_support_fsm()
    
    print("=" * 60)
    print("SCENARIO 1: Low-Risk Action (<$50 Auto-Approval)")
    print("=" * 60)
    config_1 = {"configurable": {"thread_id": "thread-1"}}
    input_1 = {"messages": [HumanMessage(content="I want a refund for $25 for a damaged item.")]}
    
    for event in app.stream(input_1, config=config_1):
        for node_name, state_update in event.items():
            print(f"[{node_name}] -> {state_update.get('messages', [''])[ -1 ]}")

    print("\n" + "=" * 60)
    print("SCENARIO 2: High-Risk Action (>$50 Human-in-the-Loop Intercept)")
    print("=" * 60)
    config_2 = {"configurable": {"thread_id": "thread-2"}}
    input_2 = {"messages": [HumanMessage(content="I need a refund of $120.00 right now.")]}

    # Runs until interrupt breakpoint
    for event in app.stream(input_2, config=config_2):
        for node_name, state_update in event.items():
            print(f"[{node_name}] -> {state_update.get('messages', [''])[ -1 ]}")

    # Inspect halted state
    state = app.get_state(config_2)
    print(f"\n[SYSTEM PAUSED] Pending Nodes: {state.next}")
    print(f"[STATE CHECK] Risk: {state.values.get('risk_level')}, Amount: ${state.values.get('refund_amount')}")

    # Simulate Human Intervention
    user_decision = input("\nSimulate Human Supervisor Decision (approve/reject): ").strip().lower()
    if user_decision == "approve":
        print("\n[SUPERVISOR APPROVED] Resuming pipeline execution...")
        for event in app.stream(None, config=config_2):
            for node_name, state_update in event.items():
                print(f"[{node_name}] -> {state_update.get('messages', [''])[ -1 ]}")
    else:
        print("\n[SUPERVISOR REJECTED] Flow terminated without execution.")

if __name__ == "__main__":
    run_demo()