# Tax Genius — Interview Preparation Guide

Use this document with `app.py` (comments mark what to explain line-by-line). Answers are concise; expand with your hackathon submission narrative where useful.

---

## 1. Project & Problem Statement

**Q: What is Tax Genius and who is it for?**  
**A:** An AI tax filing assistant for the Girl Hackathon 2025 Finance track. It helps individual taxpayers and freelancers understand Indian income tax, estimate liability, spot common deductions, and get answers without reading dense legal text alone.

**Q: Why not hire only human CAs?**  
**A:** Humans scale poorly for instant 24/7 Q&A. Tax Genius combines always-on AI guidance with deterministic calculators; complex or high-stakes cases should still go to a chartered accountant.

**Q: What problem from the hackathon did you choose?**  
**A:** *Finance — A Tax Assistant that automates tax filing processes, simplifying calculations, identifying deductions, and minimizing errors.*

---

## 2. Architecture & Design

**Q: Walk me through the high-level architecture.**  
**A:** Single-page Streamlit app. Main area = chat (Groq LLM). Sidebar = rule-based tools (tax slabs, deductions, external links). No database; state in `st.session_state`.

**Q: Why use an LLM for chat but code for tax calculation?**  
**A:** LLMs are strong at language but can hallucinate numbers. Slab tax is fixed law expressed as math—`estimate_income_tax()` is predictable, testable, and explainable in interviews.

**Q: What is `st.session_state` and why do you need it?**  
**A:** Streamlit reruns the script on every interaction. Session state persists `chat_history` across reruns so the UI and API see the full conversation.

**Q: Explain the data flow when a user sends a chat message.**  
**A:**  
1. User input → append to `chat_history`  
2. `build_llm_messages()` adds system prompt + history  
3. `client.chat.completions.create(..., stream=True)`  
4. `st.write_stream(parse_groq_stream(stream))` shows tokens live  
5. Full reply appended to `chat_history`

**Q: Draw or describe components and external dependencies.**  
**A:** Browser ↔ Streamlit ↔ `app.py` ↔ Groq API. Sidebar never calls Groq; only the chat path does.

---

## 3. AI / Groq / Prompting

**Q: Which model do you use and why?**  
**A:** `llama-3.1-8b-instant` on Groq—fast, low-latency streaming, suitable for interactive chat on free-tier hackathon infra.

**Q: What is the system prompt (`CHAT_CONTEXT`) for?**  
**A:** It steers the assistant to act as an Indian tax helper, use plain language, and avoid inventing legal citations—reduces harmful overconfidence.

**Q: What is streaming and how do you implement it?**  
**A:** The API returns chunks; `parse_groq_stream` yields each `delta.content`; `st.write_stream` displays them as they arrive for better UX.

**Q: How do you reduce wrong tax advice from the LLM?**  
**A:** System prompt boundaries; numeric estimates from code not the model; disclaimer in UI; tell users to verify with official portals or a CA.

**Q: Could you use RAG (retrieval augmented generation)?**  
**A:** Yes—embed Income Tax Act circulars / FAQs in a vector DB, retrieve relevant chunks per query, inject into context. Not implemented in v1 due to time and data curation.

**Q: What alternatives to Groq did you consider?**  
**A:** OpenAI, local Ollama, Azure OpenAI. Groq was chosen for speed and simple API for a demo chatbot.

---

## 4. Tax Logic (Code Walkthrough)

**Q: Explain `estimate_income_tax()`.**  
**A:** Iterates `TAX_SLABS` tuples `(upper_income_limit, marginal_rate, cumulative_tax_below_slab)`. When income falls in a slab, tax = `base_tax + (income - previous_limit) * rate`. Returns 0 for non-positive income.

**Q: Give a numeric example.**  
**A:** Income ₹6,00,000: in ₹5L–₹7.5L slab, tax = ₹12,500 + (6,00,000 − 5,00,000) × 10% = **₹22,500** (before cess/rebate). Income ₹8,00,000: ₹37,500 + 50,000 × 15% = **₹45,000**.

**Q: What did you intentionally leave out of the calculator?**  
**A:** Health & education cess, rebate u/s 87A, new tax regime, deductions from taxable income, surcharge, senior citizen slabs, capital gains, TDS. Documented as demo-only.

**Q: How does the deductions feature work?**  
**A:** `DEDUCTION_OPTIONS` dict maps label → short description. Multiselect shows `st.sidebar.info` cards—educational, not automatic rupee savings calculation yet.

---

## 5. Streamlit & Frontend

**Q: Why Streamlit instead of React + FastAPI?**  
**A:** Faster to build a hackathon MVP: Python-only, built-in chat widgets, easy sidebar layout, fast deploy to Streamlit Cloud.

**Q: What does `st.rerun()` do after Clear chat?**  
**A:** Forces a fresh run so the UI redraws without old messages after resetting `chat_history`.

**Q: How do you style the app?**  
**A:** `st.markdown(..., unsafe_allow_html=True)` injects CSS targeting Streamlit chat/sidebar test IDs for brand colors.

---

## 6. Security, Config & DevOps

**Q: How are API keys managed?**  
**A:** `load_secrets()` tries `.env` via `python-dotenv`, else `st.secrets` for cloud. Keys are not hardcoded; `.gitignore` excludes `.env`.

**Q: Do you store user tax data?**  
**A:** No backend persistence in this version—only in-memory session until the tab closes.

**Q: How would you deploy this?**  
**A:** Streamlit Community Cloud, Docker, or GitHub Codespaces; set `GROQ_API_KEY` in secrets; expose port 8501.

**Q: What is in `requirements.txt`?**  
**A:** `groq`, `streamlit`, `python-dotenv`—minimal deps; removed unused `pdfkit`.

---

## 7. Code Quality & Testing

**Q: How would you unit test the tax function?**  
**A:** pytest parametrized cases: 0 income → 0; boundary at ₹2.5L, ₹5L; mid-slab ₹6L → ₹22,500; ₹8L → ₹45,000; high income in 30% slab.

**Q: What bug did you fix in message building?**  
**A:** Earlier code duplicated `INITIAL_RESPONSE` in the API payload (system + history both had greeting). Now `build_llm_messages` sends system once + full history only.

**Q: How would you improve code structure for production?**  
**A:** Split into `tax_engine.py`, `llm_client.py`, `ui/sidebar.py`; add logging, input validation, and pytest CI on GitHub Actions.

---

## 8. Impact, Feasibility & Future Work

**Q: What societal impact do you claim?**  
**A:** Less stress, fewer basic errors, better awareness of deductions and deadlines—especially for first-time filers.

**Q: Rollout strategy?**  
**A:** Beta with real users → tune prompts → add regime toggle and document upload → partner with CAs for validation.

**Q: Top 3 features for v2?**  
**A:** (1) New vs old regime, (2) 80C/80D cap calculator, (3) RAG over official ITD FAQs with citations.

---

## 9. Behavioral / Team

**Q: What was the hardest part?**  
**A:** *(Personalize)* e.g. balancing accurate tax rules vs hackathon timebox; choosing what the LLM vs code should own.

**Q: How did you validate the solution?**  
**A:** Manual test cases on slab boundaries; sample chat questions on 80C, ITR types; peer review of README and disclaimers.

---

## 10. Quick Code Map (for live walkthrough)

| File / symbol | Say this in the interview |
|---------------|---------------------------|
| `TAX_SLABS` | Single source of truth for demo slab rates |
| `estimate_income_tax()` | Core deterministic algorithm |
| `parse_groq_stream()` | Streaming adapter for Groq chunks |
| `load_secrets()` | Local vs cloud configuration |
| `build_llm_messages()` | API message list with system prompt |
| Sidebar `number_input` | User input → tax metric |
| `st.write_stream` | Real-time assistant typing effect |
| `Clear chat` + `st.rerun()` | Session reset UX |

---

## Sample “Tell me about your project” (60 seconds)

> I built Tax Genius for Girl Hackathon 2025—a Streamlit tax assistant for Indian income tax. Users chat with an AI powered by Groq’s Llama model for plain-language answers on filing and deductions. Separately, a sidebar calculator applies progressive tax slabs in code so numbers stay accurate, plus a deduction checklist and links to incometax.gov.in. I kept secrets in environment variables, don’t persist PII, and document that the calculator is educational. Next steps would be regime selection, real deduction math, and RAG on official tax documents.

---

Good luck with your submission and interviews.
