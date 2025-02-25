import os
from dotenv import dotenv_values
import streamlit as st
from groq import Groq
import pdfkit  

def parse_groq_stream(stream):
    response_content = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            response_content += chunk.choices[0].delta.content
            yield chunk.choices[0].delta.content
    return response_content

st.set_page_config(
    page_title="Smart Tax Advisor 🧑‍💼",
    page_icon="💰",
    layout="centered",
)

try:
    secrets = dotenv_values(".env")  
    GROQ_API_KEY = secrets["GROQ_API_KEY"]
except Exception as e:
    secrets = st.secrets
    GROQ_API_KEY = secrets["GROQ_API_KEY"]

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

INITIAL_RESPONSE = secrets.get("INITIAL_RESPONSE", "Hello! I am here to assist you with tax finalization.")
CHAT_CONTEXT = secrets.get("CHAT_CONTEXT", 
    "You are a smart tax advisor helping users navigate tax finalization. Offer guidance on tax forms, deductions, credits, and filing deadlines.")

client = Groq(api_key=GROQ_API_KEY)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE},
    ]

st.markdown("""
    <style>
        /* Sidebar Styling - Bluish Theme */
        [data-testid="stSidebarContent"] {
            background: linear-gradient(135deg, #0A74DA, #1E3A8A);
            padding: 18px;
            border-radius: 12px;
            color: white !important;
            box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.2);
        }

        /* Sidebar Headings */
        [data-testid="stSidebarContent"] label, 
        [data-testid="stSidebarContent"] h3 {
            color: white !important;
            font-weight: bold;
        }
        
        /* Chat Message Styling */
        .stChatMessageAssistant {
            background-color: #1E3A8A !important;
            color: white !important;
            padding: 12px 18px;
            border-radius: 15px;
            width: fit-content;
            margin-bottom: 10px;
        }

        .stChatMessageUser {
            background-color: #0078D7 !important;
            color: white !important;
            padding: 12px 18px;
            border-radius: 15px;
            width: fit-content;
            margin-bottom: 10px;
            align-self: flex-end;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💡 Tax Genius: Your Smart Filing Assistant 📈")
st.caption("Your AI-powered tax assistant for hassle-free tax finalization.")

for message in st.session_state.chat_history:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "🧑‍💻" if role == "user" else "🏦"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"], unsafe_allow_html=True)

user_prompt = st.chat_input("Type your tax-related query...")

st.sidebar.title("🛠️ Tax Tools & Resources")
st.sidebar.subheader("💵 Income Tax Estimator")

income = st.sidebar.number_input("Enter your annual income:", min_value=0, step=10000000)

if income:
    tax_estimate = 100
    if income <= 250000:
        tax_estimate = 0
    elif income <= 500000:
        tax_estimate = (income - 250000) * 0.05
    elif income <= 750000:
        tax_estimate = 12500 + (income - 500000) * 0.10
    elif income <= 1000000:
        tax_estimate = 37500 + (income - 750000) * 0.15
    elif income <= 1250000:
        tax_estimate = 75000 + (income - 1000000) * 0.20
    elif income <= 1500000:
        tax_estimate = 125000 + (income - 1250000) * 0.25
    else:
        tax_estimate = 187500 + (income - 1500000) * 0.30

    st.sidebar.write(f"Estimated tax due: ₹{tax_estimate:,.2f}")

    




st.sidebar.subheader("✅ Eligible Deductions")
deductions = ["Healthcare Expenses", "Home Loan Interest", "Education Loan Interest", "Charitable Donations"]
selected_deductions = st.sidebar.multiselect("Select deductions that apply to you:", deductions)
if selected_deductions:
    st.sidebar.write("You have selected:")
    for deduction in selected_deductions:
        st.sidebar.write(f"- {deduction}")

st.sidebar.subheader("📌 Important Tax Links")

st.sidebar.markdown(
    '<a href="https://incometaxindia.gov.in/Pages/downloads/most-used-forms.aspx" style="color: #FFD700; font-weight: bold; text-decoration: none;">📄 IRS Tax Forms</a>',
    unsafe_allow_html=True
)
st.sidebar.markdown(
    '<a href="https://www.incometax.gov.in/iec/foportal/help/how-to-file-itr2-form" style="color: #FFD700; font-weight: bold; text-decoration: none;">⏳ Tax Filing Deadlines</a>',
    unsafe_allow_html=True
)


if user_prompt:
    with st.chat_message("user", avatar="🔨"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        {"role": "assistant", "content": INITIAL_RESPONSE},
        *st.session_state.chat_history,
    ]

    with st.chat_message("assistant", avatar="💼"):
        stream = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            stream=True
        )
        response_content = "".join(parse_groq_stream(stream))
        st.markdown(response_content)
    
    st.session_state.chat_history.append({"role": "assistant", "content": response_content})
