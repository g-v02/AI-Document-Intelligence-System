import streamlit as st
import requests

st.set_page_config(page_title="AI Document Intelligence System", layout="wide")

st.title("📄 AI Document Intelligence System")
st.markdown("*(RAG + Output Parser + Custom Chains)*")

# -----------------------------------------------------------------------------
# 1. Server Configuration (Defined at the top)
# -----------------------------------------------------------------------------
st.sidebar.header("Server Settings")
api_url = st.sidebar.text_input(
    "Backend Base URL", 
    value="https://YOUR-NGROK-URL.ngrok-free.app"
).rstrip("/")

# Custom headers to bypass ngrok browser warning
HEADERS = {"ngrok-skip-browser-warning": "true"}

# Helper function to check connection and fetch documents
def get_documents(url):
    try:
        response = requests.get(f"{url}/documents", headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return response.json().get("documents", []), True
        return [], False
    except requests.exceptions.RequestException:
        return [], False

# -----------------------------------------------------------------------------
# 2. Document Upload Section
# -----------------------------------------------------------------------------
st.sidebar.header("Document Upload")
uploaded_file = st.sidebar.file_uploader("Upload PDF Contract or Report", type=["pdf"])

if uploaded_file is not None:
    if st.sidebar.button("Index Document"):
        with st.spinner("Processing PDF and creating vector embeddings..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                res = requests.post(f"{api_url}/upload", files=files, headers=HEADERS, timeout=120)
                if res.status_code == 200:
                    st.sidebar.success(f"Uploaded: {res.json()['doc_id']}")
                else:
                    st.sidebar.error(f"Upload failed: {res.text}")
            except requests.exceptions.RequestException as e:
                st.sidebar.error(f"Could not connect to backend server: {e}")

# Check backend connection status and fetch active documents
available_docs, is_connected = get_documents(api_url)

if is_connected:
    st.sidebar.success("🟢 Connected to Backend Server")
else:
    st.sidebar.warning("🔴 Cannot connect to Backend Server. Paste your ngrok URL above.")

# -----------------------------------------------------------------------------
# 3. Application Navigation Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["💬 Question Answering (RAG)", "📊 Structured Analysis", "📝 Summarization", "⚖️ Document Comparison"])

# Tab 1: QA
with tab1:
    st.subheader("Ask Questions About Documents")
    selected_doc = st.selectbox("Select Document", available_docs, key="qa_doc")
    question = st.text_input("Enter your question:")
    if st.button("Ask Query"):
        if selected_doc and question:
            with st.spinner("Searching vector DB & generating answer..."):
                try:
                    res = requests.post(f"{api_url}/qa", json={"doc_id": selected_doc, "question": question}, headers=HEADERS, timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                        st.markdown("### Answer")
                        st.write(data["answer"])
                        st.markdown("#### Retrieved References Context")
                        for idx, src in enumerate(data.get("sources", [])):
                            st.info(f"**Source {idx+1}:** {src}")
                    else:
                        st.error(f"Error: {res.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("Please select a document and enter a question.")

# Tab 2: Structured Output Analysis
with tab2:
    st.subheader("Structured Document Extraction")
    selected_doc = st.selectbox("Select Document for Analysis", available_docs, key="struct_doc")
    if st.button("Generate Structured Intelligence"):
        if selected_doc:
            with st.spinner("Analyzing document and formatting JSON output..."):
                try:
                    res = requests.post(f"{api_url}/analyze", json={"doc_id": selected_doc}, headers=HEADERS, timeout=120)
                    if res.status_code == 200:
                        data = res.json()
                        if "parsed" in data:
                            parsed = data["parsed"]
                            st.success("Successfully Parsed JSON Output!")
                            st.write(f"**Document:** {parsed.get('document', selected_doc)}")
                            st.write(f"**Summary:** {parsed.get('summary')}")
                            
                            st.markdown("**Key Points:**")
                            st.write(parsed.get("key_points"))
                            
                            st.markdown("**Risks / Concerns:**")
                            st.write(parsed.get("risks"))
                            
                            st.markdown("**References:**")
                            st.write(parsed.get("references"))
                        else:
                            st.write("Raw Output:")
                            st.write(data.get("raw_output"))
                    else:
                        st.error(f"Error: {res.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("Please select a document.")

# Tab 3: Summarization
with tab3:
    st.subheader("Summarize Document")
    selected_doc = st.selectbox("Select Document to Summarize", available_docs, key="sum_doc")
    if st.button("Summarize"):
        if selected_doc:
            with st.spinner("Generating summary..."):
                try:
                    res = requests.post(f"{api_url}/summarize", json={"doc_id": selected_doc}, headers=HEADERS, timeout=90)
                    if res.status_code == 200:
                        st.write(res.json()["summary"])
                    else:
                        st.error(f"Error: {res.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")

# Tab 4: Document Comparison
with tab4:
    st.subheader("Compare Two Documents")
    col1, col2 = st.columns(2)
    with col1:
        doc1 = st.selectbox("Select Document 1", available_docs, key="cmp_doc1")
    with col2:
        doc2 = st.selectbox("Select Document 2", available_docs, key="cmp_doc2")
        
    if st.button("Compare Documents"):
        if doc1 and doc2:
            with st.spinner("Comparing contents..."):
                try:
                    res = requests.post(f"{api_url}/compare", json={"doc_id1": doc1, "doc_id2": doc2}, headers=HEADERS, timeout=120)
                    if res.status_code == 200:
                        st.markdown("### Comparison Results")
                        st.write(res.json()["comparison"])
                    else:
                        st.error(f"Error: {res.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
        else:
            st.warning("Please select two documents.")