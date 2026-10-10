# AI-Document-Intelligence-System

# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October) 2026

> 🎓 This project was built during the [ **Tips Hindawi** ](https://www.tipshindawi.com/) **Internship (August–October) 2026**.

## 👤 Participant

| Field            | Value                                       |
| ---------------- | ------------------------------------------- |
| Full Name        | Ganna Khaled Abdelnasser                    |
| Project Name     | AI Document Intelligence System             |
| GitHub Username  | g-v02                                       |
| Internship Batch | August–October 2026                         |
| Training Program | Large Language Models (LLMs) Program        |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en) |

---

# 📖 Project Overview

The **AI Document Intelligence System** is a Retrieval-Augmented Generation (RAG) platform designed to analyze, query, summarize, and extract structured insights from documents such as contracts, reports, and multi-page PDFs.
It utilizes a decoupled client-server architecture, allowing heavy GPU model inference to run remotely while presenting a responsive, user-friendly interface locally.


---

# ✨ Features

- **RAG-Powered Question Answering**: Upload documents and ask specific questions. The system retrieves relevant passages using vector similarity search and generates context-grounded answers with source citations.
- **Structured Output Parsing**: Uses custom schemas to parse unstructured text into formatted JSON containing summaries, key points/clauses, risk assessments, and exact reference quotes.
- **Document Summarization**: Generates high-level executive summaries from long-form text documents.
- **Document Comparison**: Compares two uploaded documents side-by-side to highlight key similarities, operational differences, and conflicting terms.

---

# 🛠️ Technologies Used

**Language Model**: `mistralai/Mistral-7B-Instruct-v0.2` (Hugging Face Transformers, PyTorch, 4-bit / Float16 Precision)
- **Embeddings & Vector Database**: `sentence-transformers/all-MiniLM-L6-v2` & FAISS (`langchain-community`)
- **Backend API Framework**: FastAPI, Uvicorn, PyPDF Loader, Pydantic
- **Tunneling**: `pyngrok`
- **Frontend Framework**: Streamlit & Requests
---

# ⚙️ Installation

### 1. Backend Setup (GPU Server / Kaggle / Google Colab)
- Install backend dependencies in requirements.txt

- Execute backend.py and runner.py in your notebook environment to launch Uvicorn and open the ngrok tunnel

- Copy the generated public URL from the console output (e.g., https://xxxx.ngrok-free.app).

### 1. Frontend Setup (Local Machine)
- Install local dependencies (streamlit, requests) in your PowerShell

- Navigate to your local project directory and launch Streamlit:
  cd path\to\your\directory
  python -m streamlit run frontend.py)
  
- Paste your ngrok backend URL into the sidebar input field in the streamlit web application
---

# 🚀 Usage

Upload & Index: Use the sidebar to upload a PDF file and click Index Document to generate vector embeddings.

Question Answering: Select an indexed document in the 'Question Answering' tab and ask questions.

Structured Extraction: Go to 'Structured Analysis' to generate parsed JSON key insights and risk evaluations.

Summarize: Switch to 'Summarization' to get concise document overviews.

Compare: Select two uploaded files in 'Document Comparison' to perform comparative analysis.

---

# 📸 Demo

Add screenshots, GIFs, or a demo video.

---

# 📈 Results

Zero-Prompt-Echo Inference: Sliced input token sequences during decoding to deliver clean, answer-only responses.

Strict Output Parsing: Standardized non-deterministic LLM output into validated JSON schemas.

Efficient Cloud-to-Local Bridge: Connected local user interfaces seamlessly to high-performance remote GPU backends via ngrok tunneling.
---

# 🔮 Future Improvements

- Add support for multi-format file parsing (DocX, CSV, TXT).

- Integrate persistent vector storage using ChromaDB or Pinecone.

- Implement 4-bit bitsandbytes quantization options directly in UI configuration settings.

---

# 📚 About the Internship

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**, and it will be showcased on the official [Tips Hindawi](https://www.tipshindawi.com/) website.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the internship encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.
