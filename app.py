import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Distributed Group Communication Simulator",
    page_icon="🌐",
    layout="wide"
)

PROCESSES = ["P1", "P2", "P3", "P4"]


def initialize_state():
    defaults = {
        "clocks": {p: [0, 0, 0, 0] for p in PROCESSES},
        "causal_messages": [],
        "causal_history": [],
        "causal_counter": 0,
        "total_messages": [],
        "total_history": [],
        "total_counter": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_simulation():
    for key in [
        "clocks", "causal_messages", "causal_history",
        "causal_counter", "total_messages", "total_history",
        "total_counter"
    ]:
        st.session_state.pop(key, None)
    initialize_state()


def send_causal_message(sender, message):
    clocks = st.session_state.clocks
    sender_index = PROCESSES.index(sender)

    # Advance the sender's own vector-clock component.
    clocks[sender][sender_index] += 1
    timestamp = clocks[sender].copy()

    st.session_state.causal_counter += 1
    msg = {
        "id": st.session_state.causal_counter,
        "sender": sender,
        "message": message,
        "timestamp": timestamp,
        "pending": [p for p in PROCESSES if p != sender],
    }
    st.session_state.causal_messages.append(msg)

    st.session_state.causal_history.append({
        "Process": sender,
        "Message ID": f"M{msg['id']}",
        "Message": message,
        "Vector Clock": str(timestamp),
        "Status": "Sent",
    })


def can_deliver(receiver, msg):
    local = st.session_state.clocks[receiver]
    received = msg["timestamp"]
    sender_index = PROCESSES.index(msg["sender"])

    # A process must receive the sender's messages in sequence.
    if received[sender_index] != local[sender_index] + 1:
        return False

    # All other causal dependencies must already be known.
    for i in range(len(PROCESSES)):
        if i != sender_index and received[i] > local[i]:
            return False

    return True


def deliver_causal(receiver, msg):
    if receiver not in msg["pending"] or not can_deliver(receiver, msg):
        return False

    local = st.session_state.clocks[receiver]
    received = msg["timestamp"]

    for i in range(len(PROCESSES)):
        local[i] = max(local[i], received[i])

    # Record the receive event in the receiver's own clock.
    receiver_index = PROCESSES.index(receiver)
    local[receiver_index] += 1

    msg["pending"].remove(receiver)
    st.session_state.causal_history.append({
        "Process": receiver,
        "Message ID": f"M{msg['id']}",
        "Message": msg["message"],
        "Vector Clock": str(local.copy()),
        "Status": "Delivered",
    })
    return True


def send_total_message(sender, message):
    # The central sequencer assigns one unique, increasing sequence number.
    st.session_state.total_counter += 1
    sequence = st.session_state.total_counter

    msg = {
        "Sequence": sequence,
        "Sender": sender,
        "Message": message,
    }
    st.session_state.total_messages.append(msg)

    # In this simulator, the sequencer delivers in order to every process.
    for process in PROCESSES:
        st.session_state.total_history.append({
            "Process": process,
            "Sequence": sequence,
            "Sender": sender,
            "Message": message,
            "Status": "Delivered",
        })


initialize_state()

st.title("🌐 Distributed Group Communication Simulator")
st.caption(
    "Interactive simulation of causal ordering and total ordering "
    "among four distributed processes."
)

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Choose a module",
        [
            "Dashboard",
            "Causal Ordering",
            "Total Ordering",
            "Message History",
            "About Project",
        ],
    )
    st.divider()
    if st.button("🔄 Reset entire simulation", use_container_width=True):
        reset_simulation()
        st.rerun()

if page == "Dashboard":
    st.subheader("System Dashboard")
    causal_sent = st.session_state.causal_counter
    causal_deliveries = sum(
        row["Status"] == "Delivered"
        for row in st.session_state.causal_history
    )
    total_sent = st.session_state.total_counter

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Processes", len(PROCESSES))
    c2.metric("Causal messages", causal_sent)
    c3.metric("Total-order messages", total_sent)
    c4.metric("Causal deliveries", causal_deliveries)

    st.divider()
    st.subheader("Distributed Processes")
    cols = st.columns(4)
    for i, process in enumerate(PROCESSES):
        with cols[i]:
            st.info(f"🖥️ **{process}**")
            st.caption("Current vector clock")
            st.code(str(st.session_state.clocks[process]))

    st.subheader("Communication model")
    st.markdown(
        """
        ```text
              ┌──────┐       ┌──────┐
              │  P1  │───────│  P2  │
              └──┬───┘       └──┬───┘
                 │              │
                 │  Group       │
                 │  Messages    │
                 │              │
              ┌──┴───┐       ┌──┴───┐
              │  P3  │───────│  P4  │
              └──────┘       └──────┘
        ```
        """
    )
    st.success("The simulator is ready. Select a module from the sidebar.")

elif page == "Causal Ordering":
    st.subheader("🔗 Causal Ordering")
    st.write(
        "Broadcast messages and deliver them manually. A message is blocked "
        "until its causal dependencies have been delivered."
    )

    left, right = st.columns(2)
    with left:
        with st.form("causal_send_form"):
            sender = st.selectbox("Sender process", PROCESSES)
            message = st.text_input("Message content", placeholder="Example: Hello P2")
            send_clicked = st.form_submit_button(
                "📨 Broadcast causal message",
                use_container_width=True,
            )
        if send_clicked:
            if message.strip():
                send_causal_message(sender, message.strip())
                st.success("Message broadcast to the other processes.")
                st.rerun()
            else:
                st.warning("Enter a message before broadcasting.")

    with right:
        receiver = st.selectbox(
            "Receiving process",
            PROCESSES,
            key="causal_receiver",
        )
        pending = [
            msg for msg in st.session_state.causal_messages
            if receiver in msg["pending"]
        ]
        st.markdown("**Messages waiting for this process**")
        if pending:
            for msg in pending:
                st.write(
                    f"M{msg['id']} from {msg['sender']}: {msg['message']}"
                )
                st.caption(f"Timestamp: {msg['timestamp']}")
        else:
            st.info("No pending messages for this process.")

    st.divider()
    st.markdown("**Attempt message delivery**")
    available = [
        msg for msg in st.session_state.causal_messages
        if receiver in msg["pending"]
    ]

    if available:
        selected = st.selectbox(
            "Choose a message",
            available,
            format_func=lambda m: (
                f"M{m['id']} | {m['sender']} → {receiver} | {m['message']}"
            ),
            key="causal_message_choice",
        )
        if st.button("Attempt delivery", use_container_width=False):
            if deliver_causal(receiver, selected):
                st.success(f"M{selected['id']} delivered to {receiver}.")
            else:
                st.warning(
                    "Delivery blocked: an earlier message or causal "
                    "dependency must be delivered first."
                )
            st.rerun()

        if st.button("Deliver all currently deliverable messages"):
            delivered_count = 0
            made_progress = True
            while made_progress:
                made_progress = False
                for msg in list(st.session_state.causal_messages):
                    if receiver in msg["pending"] and deliver_causal(receiver, msg):
                        delivered_count += 1
                        made_progress = True
            st.success(f"Delivered {delivered_count} message(s) to {receiver}.")
            st.rerun()
    else:
        st.info("There are no messages to deliver to this process.")

    st.divider()
    st.subheader("Vector clocks")
    clock_df = pd.DataFrame([
        {"Process": p, "Vector Clock": str(st.session_state.clocks[p])}
        for p in PROCESSES
    ])
    st.dataframe(clock_df, use_container_width=True, hide_index=True)

    st.caption(
        "Vector-clock components are ordered as [P1, P2, P3, P4]. "
        "A process's own component advances for each local send or receive event."
    )

elif page == "Total Ordering":
    st.subheader("🔢 Total Ordering")
    st.write(
        "A central sequencer assigns every broadcast a unique sequence number. "
        "The simulator delivers messages to all processes in that sequence."
    )

    with st.form("total_send_form"):
        sender = st.selectbox("Sender process", PROCESSES, key="total_sender")
        message = st.text_input(
            "Message content",
            placeholder="Example: Meeting at 10 AM",
            key="total_message",
        )
        send_clicked = st.form_submit_button(
            "📢 Broadcast total-order message",
            use_container_width=True,
        )

    if send_clicked:
        if message.strip():
            send_total_message(sender, message.strip())
            st.success("Sequencer assigned a number and delivered the message.")
            st.rerun()
        else:
            st.warning("Enter a message before broadcasting.")

    st.divider()
    st.subheader("Total-order delivery history")
    if st.session_state.total_history:
        total_df = pd.DataFrame(st.session_state.total_history)
        st.dataframe(total_df, use_container_width=True, hide_index=True)

        st.subheader("Delivery sequence at each process")
        for process in PROCESSES:
            sequence = [
                str(row["Sequence"])
                for row in st.session_state.total_history
                if row["Process"] == process
            ]
            st.success(f"**{process}:** " + " → ".join(sequence))
        st.success("All processes have the same message sequence.")
    else:
        st.info("No total-order messages have been sent yet.")

elif page == "Message History":
    st.subheader("📜 Message History")

    st.markdown("**Causal ordering history**")
    if st.session_state.causal_history:
        st.dataframe(
            pd.DataFrame(st.session_state.causal_history),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No causal messages recorded.")

    st.divider()
    st.markdown("**Total ordering history**")
    if st.session_state.total_history:
        st.dataframe(
            pd.DataFrame(st.session_state.total_history),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No total-order messages recorded.")

    causal_deliveries = sum(
        row["Status"] == "Delivered"
        for row in st.session_state.causal_history
    )
    total_deliveries = len(st.session_state.total_history)
    chart_df = pd.DataFrame({
        "Communication Type": ["Causal deliveries", "Total-order deliveries"],
        "Deliveries": [causal_deliveries, total_deliveries],
    })
    st.subheader("📊 Delivery statistics")
    fig = px.bar(
        chart_df,
        x="Communication Type",
        y="Deliveries",
        text="Deliveries",
        title="Message delivery statistics",
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "About Project":
    st.subheader("📘 About the Project")
    st.markdown(
        """
        ### Objective
        To simulate group communication among multiple distributed processes
        and demonstrate causal ordering and total ordering.

        ### Technologies
        - Python
        - Streamlit
        - Pandas
        - Plotly

        ### Concepts
        **Causal ordering:** Vector clocks track causal dependencies. A
        receiver buffers a message until the required earlier events have
        been delivered.

        **Total ordering:** A centralized sequencer assigns monotonically
        increasing sequence numbers. Every process receives the same ordered
        message stream.

        ### Applications
        - Distributed databases
        - Replicated services
        - Group messaging systems
        - Collaborative applications

        ### Scope
        This is an educational, single-application simulation. It models
        multiple processes in Streamlit session state; it does not create
        separate computers or implement fault-tolerant consensus.
        """
    )

st.divider()
st.caption(
    "Distributed Group Communication Simulator | "
    "Python • Streamlit • Vector Clocks • Sequencer"
)
