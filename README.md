# Distributed Group Communication Simulator

An interactive educational simulator demonstrating **causal ordering** and
**total ordering** among four distributed processes (P1, P2, P3, P4).

## Features

- Four simulated distributed processes
- Group message broadcasting
- Causal ordering with vector clocks
- Pending-message buffering and manual delivery
- Total ordering with a centralized sequencer
- Message history and delivery statistics
- Streamlit dashboard

## Project structure

```text
Distributed_Group_Communication/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Requirements

- Python 3.9 or newer
- Internet connection for installing Python packages
- VS Code (recommended)

## Installation on macOS

Open this folder in VS Code, then run these commands in the terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit normally opens the application at:

`http://localhost:8501`

## How to demonstrate causal ordering

1. Open **Causal Ordering**.
2. Send a message from P1 (for example, `M1: First message`).
3. Deliver M1 to P2.
4. Send a second message from P2 (for example, `M2: Reply`).
5. Select P3 as the receiver and attempt to deliver M2.
6. M2 is blocked because P3 has not received the earlier causal message M1.
7. Deliver M1 to P3, then deliver M2 to P3.

## How to demonstrate total ordering

1. Open **Total Ordering**.
2. Send messages from different processes.
3. Observe the sequence numbers assigned by the sequencer.
4. Compare P1, P2, P3, and P4 delivery sequences. They will be identical.

## Concepts

- **Vector clock:** A logical clock with one component per process, used to
  represent causal knowledge.
- **Causal ordering:** If message M1 causally precedes M2, a process must not
  deliver M2 before M1.
- **Total ordering:** All participating processes deliver the same messages
  in the same sequence.
- **Sequencer:** A centralized component that assigns a unique increasing
  sequence number to each message.

## Educational scope

This project is a single-process simulation of multiple logical processes.
The causal-ordering module uses vector-clock checks and pending-message
buffering. The total-ordering module models a centralized sequencer that
delivers messages in sequence. It is not a production distributed system,
network multicast implementation, or fault-tolerant consensus protocol.

## Reset

Use **Reset entire simulation** in the sidebar to clear the message history
and vector clocks.
