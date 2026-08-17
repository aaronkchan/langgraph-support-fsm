# Deterministic Support FSM with LangGraph & HITL

A stateful support workflow engine engineered to eliminate LLM hallucination risks during sensitive customer operations. Built with LangGraph, it implements deterministic Finite State Machine (FSM) routing gates to separate low-risk automated resolutions from high-risk side effects (e.g., refunds over $50), using persistent memory checkpoints to enforce human-in-the-loop (HITL) authorization before execution.


# Core Architecture
                 [ User Input ]
                       │
                       ▼
             [ Classify Intent ]
              /        │        \
             /         │         \
    (Order Status)     (FAQ)     (Refund)
         │             │          │
         ▼             ▼          ▼
    [ Order Node ]  [ FAQ Node ]  [ Evaluate Risk Threshold ]
         │             │          /                       \
         │             │   (Amount <= $50)          (Amount > $50)
         │             │         │                        │
         │             │         ▼                        ▼
         │             │   [ Auto-Approve ]     [ HITL Review Gate ]
         │             │         │                        │
         │             │         │               (Interrupt / Pause)
         │             │         │                        │
         │             │         │                 [ Human Approval ]
         │             │         │                        │
         │             │         │                        ▼
         │             │         │               [ Execute Refund ]
         \             │         /                        /
          \            │        /                        /
           ▼           ▼       ▼                        ▼
                        [ END / Response ]


# Key Features

- Deterministic Intent Routing: Replaces unconstrained model outputs with structured state transitions across critical customer journeys (Order Status, FAQ, Refunds).
- Risk-Gated Action Interception: Evaluates financial and operational thresholds in real time, automatically routing actions exceeding safety limits into review states.
- Stateful Checkpoint Interrupts: Leverages LangGraph memory checkpoints to safely freeze thread execution state until authorized by a human supervisor.
- Audit-Ready State Schema: Tracks message history, intent classification, transaction values, and approval statuses across a strictly typed state dictionary.

# Project Structure
langgraph-support-fsm/
├── README.md
├── requirements.txt
├── state_machine.py     # Graph definition, state schema, and HITL breakpoints
└── main.py              # Interactive CLI scenario runner

# Architecture & Features
- **Deterministic Intent Routing:** Replaces open-ended generation with strict state transitions for critical customer journeys (Order Status, FAQ, Refunds).
- **Risk Gate Interception:** Automatically evaluates action thresholds; operations exceeding safety limits (e.g., refunds >$50) trigger immediate state suspension.
- **Stateful Checkpointing:** Leverages LangGraph memory checkpoints to hold thread execution state indefinitely until human authorization is granted.



# Quickstart
## Prerequisites
- Python 3.10+
- Virtual environment (recommended)

# Installation
## Clone the repository
git clone https://github.com/aaronkchan/langgraph-support-fsm.git
cd langgraph-support-fsm
## Install dependencies
pip install -r requirements.txt
