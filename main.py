from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import os
import traceback
import urllib.request
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from document_tool import create_word_document

# Load environment variables
load_dotenv()

app = FastAPI(title="Autonomous AI Agent API")

# ==========================================
# DYNAMIC MODEL DISCOVERY (The Master Fix)
# Instead of guessing the model name, we auto-fetch the active one.
# ==========================================
def get_active_google_model():
    """Dynamically fetches an available model from Google API to prevent 404 errors."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing in .env file")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            models = data.get("models", [])
            
            # Find models that support generateContent
            valid_models = [
                m["name"].replace("models/", "") 
                for m in models 
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            
            # Prefer 'flash' models for speed
            for m in valid_models:
                if "flash" in m:
                    print(f"Dynamically selected model: {m}")
                    return m
            
            print(f"Dynamically selected fallback model: {valid_models[0]}")
            return valid_models[0]
    except Exception as e:
        print(f"Model auto-detect failed: {e}. Falling back to default.")
        return "gemini-1.5-flash"

# ==========================================
# 1. Pydantic Models for Structured Planning
# ==========================================
class AgentPlan(BaseModel):
    tasks: list[str] = Field(description="Step-by-step logical plan to fulfill the request")
    document_title: str = Field(description="A professional title for the document")

class AgentRequest(BaseModel):
    request: str

class AgentResponse(BaseModel):
    plan: list[str]
    document_path: str
    message: str

# Initialize LLM dynamically
try:
    active_model_name = get_active_google_model()
    llm = ChatGoogleGenerativeAI(
        model=active_model_name, 
        temperature=0.7, 
        max_retries=3
    )
except Exception as e:
    print(f"Failed to initialize LLM: {e}")
    llm = None

@app.post("/agent", response_model=AgentResponse)
async def run_agent(payload: AgentRequest):
    if llm is None:
        raise HTTPException(status_code=500, detail="LLM failed to initialize. Check API key.")
        
    user_request = payload.request
    if not user_request:
        raise HTTPException(status_code=400, detail="Request cannot be empty.")

    try:
        # PHASE 1: AUTONOMOUS PLANNING
        planner_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an autonomous AI planner. Analyze the request, determine necessary steps, and output a structured plan. Provide a clear document title."),
            ("user", "Request: {request}")
        ])
        
        planner_llm = llm.with_structured_output(AgentPlan)
        planner_chain = planner_prompt | planner_llm
        plan_result = planner_chain.invoke({"request": user_request})
        
        # PHASE 2: EXECUTION & GENERATION
        generator_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert document generator. Write a comprehensive professional document using the provided execution plan. Output plain text with paragraphs and bullet points. Do not use Markdown symbols like # or *."),
            ("user", "User Request: {request}\n\nExecution Plan:\n{plan}\n\nGenerate the complete document content now.")
        ])
        
        generator_chain = generator_prompt | llm
        formatted_plan = "\n".join([f"- {task}" for task in plan_result.tasks])
        
        content_result = generator_chain.invoke({
            "request": user_request,
            "plan": formatted_plan
        })
        
        final_content = content_result.content
        
        # PHASE 3: TOOL EXECUTION
        doc_path = create_word_document(
            title=plan_result.document_title,
            content=final_content
        )
        
        return AgentResponse(
            plan=plan_result.tasks,
            document_path=doc_path,
            message=f"Agent successfully planned and generated the document using {active_model_name}."
        )

    except Exception as e:
        print("\n=== AGENT EXECUTION ERROR ===")
        traceback.print_exc()
        print("==============================\n")
        raise HTTPException(status_code=500, detail=f"Agent process failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)