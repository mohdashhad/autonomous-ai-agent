# Autonomous AI Agent - Document Generator

This repository contains a Python-based Autonomous AI Agent built as a 60-minute backend engineering challenge. The agent takes a natural language request, autonomously plans a step-by-step execution strategy, writes comprehensive content based on that plan, and outputs a formatted Microsoft Word (`.docx`) document.

## 🚀 Key Features & Engineering Improvements

* **Multi-Step Autonomous Planning:** Implements a two-phase architecture. The agent first uses Pydantic to strictly generate a structured JSON action plan (TODO list) before executing the content generation. This reduces LLM hallucinations and makes the reasoning transparent.
* **Dynamic Model Discovery & Error Recovery:** Solves the common `404 NOT FOUND` issue with deprecated free-tier models. The system dynamically queries the Google Generative Language API to find and initialize the active supported model automatically.
* **Tool Orchestration:** Successfully binds LLM outputs to local system operations, generating and saving physical `.docx` files locally.
* **Resilience:** Implements explicit retry logic (`max_retries`) and robust exception handling to gracefully manage API rate limits (e.g., `503 UNAVAILABLE` errors).

## 🛠️ Tech Stack

* **Framework:** FastAPI, Uvicorn
* **AI / Agent Logic:** LangChain, Google Gemini API (`langchain-google-genai`)
* **Data Validation:** Pydantic
* **Document Generation:** `python-docx`

## 📁 Project Structure

```text
├── main.py              # FastAPI server and core AI Agent logic
├── document_tool.py     # Python tool for generating .docx files
├── test.py              # Automated test script for standard and complex requests
├── .env                 # Environment variables (API Keys)
└── output/              # Directory where generated Word documents are saved
