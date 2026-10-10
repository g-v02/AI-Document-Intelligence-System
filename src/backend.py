%%writefile backend.py
import re
import os
import json
import torch
import tempfile
from typing import List, Dict, Any
from dataclasses import dataclass
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.language_models.llms import LLM

# Output Parser Fallback Strategy

try:
    from langchain.output_parsers import ResponseSchema, StructuredOutputParser
except (ModuleNotFoundError, ImportError):
    try:
        from langchain_core.output_parsers import ResponseSchema, StructuredOutputParser
    except (ModuleNotFoundError, ImportError):
        @dataclass
        class ResponseSchema:
            name: str
            description: str

        class StructuredOutputParser:
            def __init__(self, response_schemas):
                self.response_schemas = response_schemas

            @classmethod
            def from_response_schemas(cls, response_schemas):
                return cls(response_schemas)

            def get_format_instructions(self) -> str:
                fields = ",\n".join([f'  "{s.name}": "string values"' for s in self.response_schemas])
                return f"Respond in valid JSON using this format:\n{{\n{fields}\n}}"

            def parse(self, text: str) -> dict:
                return json.loads(text)


# LLM Setup (Mistral-7B Instruct)

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

print("Loading LLM model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

def generate_text(prompt: str, max_new_tokens: int = 1024, temperature: float = 0.3) -> str:
    # Wrap in Mistral instruction tags to prevent echoing prompt
    if "[INST]" not in prompt:
        formatted_prompt = f"<s>[INST] {prompt.strip()} [/INST]"
    else:
        formatted_prompt = prompt

    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
    input_length = inputs.input_ids.shape[1]

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_k=40,
        top_p=0.9,
        temperature=temperature,
        pad_token_id=tokenizer.eos_token_id
    )

    # Slice off input tokens to return strictly new generated text
    generated_tokens = outputs[0][input_length:]
    return tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

class CustomHFLLM(LLM):
    def _call(self, prompt: str, stop: Any = None) -> str:
        return generate_text(prompt, max_new_tokens=1024, temperature=0.7)
    
    @property
    def _llm_type(self) -> str:
        return "custom_huggingface"

llm = CustomHFLLM()


# Embeddings & Vector Databse
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedding_fn = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vector_stores: Dict[str, FAISS] = {}
documents_text: Dict[str, str] = {}


# Output Parser 

response_schemas = [
    ResponseSchema(name="document", description="Name or identifier of the document analyzed"),
    ResponseSchema(name="summary", description="Concise overall summary of the document"),
    ResponseSchema(name="key_points", description="Key points or main clauses found in the document"),
    ResponseSchema(name="risks", description="Potential legal risks, liabilities, or concerns identified"),
    ResponseSchema(name="references", description="Quotes or page reference excerpts cited from the text")
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

def extract_json_block(text: str) -> str:
    # Extract clean JSON block between curly braces
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text


# FastAPI Application

app = FastAPI(title="AI Document Intelligence System API")

class QAQuery(BaseModel):
    doc_id: str
    question: str

class CompareQuery(BaseModel):
    doc_id1: str
    doc_id2: str

class AnalyzeQuery(BaseModel):
    doc_id: str

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        db = FAISS.from_documents(chunks, embedding_fn)
        
        doc_id = file.filename
        vector_stores[doc_id] = db
        documents_text[doc_id] = "\n".join([d.page_content for d in docs[:5]])
        
        return {"status": "success", "doc_id": doc_id, "chunks_indexed": len(chunks)}
    finally:
        os.remove(tmp_path)

@app.get("/documents")
async def list_documents():
    return {"documents": list(vector_stores.keys())}

@app.post("/qa")
async def question_answering(payload: QAQuery):
    if payload.doc_id not in vector_stores:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    db = vector_stores[payload.doc_id]
    retrieved_docs = db.similarity_search(payload.question, k=3)
    context = "\n\n".join([d.page_content for d in retrieved_docs])
    
    prompt = f"""Context information is below:
---------------------
{context}
---------------------
Given the context information above, answer the query concisely.
Query: {payload.question}
Answer:"""
    
    answer = generate_text(prompt, max_new_tokens=500, temperature=0.5)
    return {"answer": answer, "sources": [d.page_content[:200] + "..." for d in retrieved_docs]}

@app.post("/summarize")
async def summarize_doc(payload: AnalyzeQuery):
    if payload.doc_id not in vector_stores:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    context = documents_text[payload.doc_id][:2500]
    prompt = f"Summarize the following document content concisely:\n\n{context}\n\nSummary:"
    summary = generate_text(prompt, max_new_tokens=500, temperature=0.5)
    return {"summary": summary}

@app.post("/compare")
async def compare_documents(payload: CompareQuery):
    if payload.doc_id1 not in vector_stores or payload.doc_id2 not in vector_stores:
        raise HTTPException(status_code=404, detail="One or both documents not found.")
    
    text1 = documents_text[payload.doc_id1][:1500]
    text2 = documents_text[payload.doc_id2][:1500]
    
    prompt = f"""Compare the following two documents and highlight similarities and key differences:

--- Document 1 ({payload.doc_id1}) ---
{text1}

--- Document 2 ({payload.doc_id2}) ---
{text2}

Comparison Analysis:"""
    
    comparison = generate_text(prompt, max_new_tokens=800, temperature=0.5)
    return {"comparison": comparison}

@app.post("/analyze")
async def analyze_structured(payload: AnalyzeQuery):
    if payload.doc_id not in vector_stores:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    context = documents_text[payload.doc_id][:2000]
    
    prompt = f"""You are an expert document intelligence parser. Analyze the document text below and fill in the structured JSON fields.

Document Name: {payload.doc_id}

Document Content:
{context}

Format:
{format_instructions}

Return ONLY valid JSON starting with {{ and ending with }}. Do not add introductory text or extra explanations."""

    raw_response = generate_text(prompt, max_new_tokens=1024, temperature=0.2)
    
    try:
        json_str = extract_json_block(raw_response)
        parsed_output = json.loads(json_str)
        return {"parsed": parsed_output}
    except Exception as e:
        return {"raw_output": raw_response, "error_parsing": str(e)}
