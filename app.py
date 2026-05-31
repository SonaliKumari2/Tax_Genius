"""
Tax Genius — Your Smart Filing Assistant

Streamlit web app for Girl Hackathon 2025 (Finance track).
Combines a Groq LLM chatbot with rule-based Indian income-tax estimation
and a deductions checklist in the sidebar.
"""

import os
from dotenv import dotenv_values
import streamlit as st
from groq import Groq


# ---------------------------------------------------------------------------
# Tax slabs (simplified Old Regime estimator — education/demo only)
# Based on progressive slabs commonly used for individual residents in India.
# Not a substitute for official ITR computation or a CA's advice.
# ---------------------------------------------------------------------------
TAX_SLABS = (
    (250_000, 0.00, 0),
    (500_000, 0.05, 0),
    (750_000, 0.10, 12_500),
    (1_000_000, 0.15, 37_500),
    (1_250_000, 0.20, 75_000),
    (1_500_000, 0.25, 125_000),
    (float("inf"), 0.30, 187_500),
)

DEDUCTION_OPTIONS = {
    "Healthcare Expenses (Section 80D)": "Medical insurance premiums and preventive health check-ups.",
    "Home Loan Interest (Section 24)": "Interest on housing loan for self-occupied property (limits apply).",
    "Education Loan Interest (Section 80E)": "Interest paid on education loan for higher studies.",
    "Charitable Donations (Section 80G)": "Donations to qualifying charitable institutions.",
}


def estimate_income_tax(annual_income: float) -> float:
    """
    Compute approximate tax liability using marginal slab rates.

    Walks each slab: for income above the previous threshold up to the
    current cap, tax += (taxable in slab) * rate, plus any cumulative base tax.
    """
    if annual_income <= 0:
        return 0.0

    previous_limit = 0
    for upper_limit, rate, base_tax in TAX_SLABS:
        if annual_income <= upper_limit:
            taxable_in_slab = annual_income - previous_limit
            return base_tax + taxable_in_slab * rate
        previous_limit = upper_limit

    return 0.0


def parse_groq_stream(stream):
    """
    Generator: yields each text token from Groq's streaming chat completion.

    Streamlit displays tokens as they arrive; the caller joins chunks for
    session history storage.
    """
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


def load_secrets():
    """
    Load API keys from .env (local) or Streamlit secrets (cloud deploy).

    dotenv_values does not raise if .env is missing; we fall back to st.secrets
    when GROQ_API_KEY is absent from the env file.
    """
    env = dotenv_values(".env")
    if env.get("GROQ_API_KEY"):
        return env

    try:
        if st.secrets.get("GROQ_API_KEY"):
            return st.secrets
    except (FileNotFoundError, KeyError, AttributeError):
        pass

    st.error(
        "Missing GROQ_API_KEY. Copy `.env.example` to `.env` and add your key, "
        "or set `GROQ_API_KEY` in `.streamlit/secrets.toml`."
    )
    st.stop()


def build_llm_messages(chat_history: list, system_prompt: str) -> list:
    """
    Format chat history for Groq's chat.completions API.

    System prompt sets assistant behavior; history is sent in order so the
    model has full conversational context.
    """
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    return messages


def main():
    """Build the Streamlit UI (chat + sidebar tools). Called when you `streamlit run app.py`."""
    st.set_page_config(
        page_title="Tax Genius — Smart Filing Assistant",
        page_icon="💰",
        layout="centered",
    )

    secrets = load_secrets()
    groq_api_key = secrets["GROQ_API_KEY"]
    os.environ["GROQ_API_KEY"] = groq_api_key

    initial_response = secrets.get(
        "INITIAL_RESPONSE",
        "Hello! I am Tax Genius. Ask me about deductions, ITR forms, or filing deadlines.",
    )
    chat_context = secrets.get(
        "CHAT_CONTEXT",
        "You are Tax Genius, a helpful Indian tax filing assistant. "
        "Explain tax concepts in plain language. Mention when users should consult "
        "a chartered accountant for complex cases. Do not invent specific legal citations.",
    )

    client = Groq(api_key=groq_api_key)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": initial_response},
        ]

    # Custom CSS for chat bubbles and sidebar (bluish theme)
    st.markdown(
        """
    <style>
        [data-testid="stSidebarContent"] {
            background: linear-gradient(135deg, #0A74DA, #1E3A8A);
            padding: 18px;
            border-radius: 12px;
            color: white !important;
            box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.2);
        }
        [data-testid="stSidebarContent"] label,
        [data-testid="stSidebarContent"] h3 {
            color: white !important;
            font-weight: bold;
        }
        .stChatMessageAssistant {
            background-color: #1E3A8A !important;
            color: white !important;
            padding: 12px 18px;
            border-radius: 15px;
        }
        .stChatMessageUser {
            background-color: #0078D7 !important;
            color: white !important;
            padding: 12px 18px;
            border-radius: 15px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("💡 Tax Genius: Your Smart Filing Assistant 📈")
    st.caption("AI-powered tax guidance, estimation, and resources — Girl Hackathon 2025")

    # Render prior messages from session state (survives reruns on each interaction)
    for message in st.session_state.chat_history:
        role = "user" if message["role"] == "user" else "assistant"
        avatar = "🧑‍💻" if role == "user" else "🏦"
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"], unsafe_allow_html=True)

    user_prompt = st.chat_input("Type your tax-related query...")

    # -----------------------------------------------------------------------
    # Sidebar: rule-based tools (no LLM — deterministic and fast)
    # -----------------------------------------------------------------------
    st.sidebar.title("🛠️ Tax Tools & Resources")

    st.sidebar.subheader("💵 Income Tax Estimator")
    income = st.sidebar.number_input(
        "Enter your annual taxable income (₹):",
        min_value=0,
        step=10_000,
        help="Simplified Old Regime estimate. Rebates, cess, and regime choice not included.",
    )

    if income > 0:
        tax_estimate = estimate_income_tax(income)
        st.sidebar.metric("Estimated tax (before cess/rebate)", f"₹{tax_estimate:,.2f}")
        st.sidebar.caption(
            "Demo calculator only. Use incometax.gov.in or a CA for official filing."
        )

    st.sidebar.subheader("✅ Eligible Deductions")
    selected_deductions = st.sidebar.multiselect(
        "Select deductions that may apply:",
        options=list(DEDUCTION_OPTIONS.keys()),
    )
    for name in selected_deductions:
        st.sidebar.info(f"**{name}** — {DEDUCTION_OPTIONS[name]}")

    st.sidebar.subheader("📌 Important Tax Links")
    st.sidebar.markdown(
        '[📄 Income Tax Forms (India)](https://incometaxindia.gov.in/Pages/downloads/most-used-forms.aspx)',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '[⏳ How to file ITR-2](https://www.incometax.gov.in/iec/foportal/help/how-to-file-itr2-form)',
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Clear chat"):
        st.session_state.chat_history = [
            {"role": "assistant", "content": initial_response},
        ]
        st.rerun()

    # -----------------------------------------------------------------------
    # Chat loop: on new user message, call Groq and append assistant reply
    # -----------------------------------------------------------------------
    if user_prompt:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        messages = build_llm_messages(st.session_state.chat_history, chat_context)

        with st.chat_message("assistant", avatar="🏦"):
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                stream=True,
                temperature=0.4,
            )
            response_content = st.write_stream(parse_groq_stream(stream))

        st.session_state.chat_history.append(
            {"role": "assistant", "content": response_content}
        )


# Streamlit sets __name__ == "__main__" when you run: streamlit run app.py
if __name__ == "__main__":
    main()
