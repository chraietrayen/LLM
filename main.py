from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import ollama
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FastAPI app initialization
app = FastAPI()

# Add a root endpoint for testing in browser
@app.get("/", response_class=HTMLResponse)
def root():
    return "<h3>LLM API is running. Use POST /generate with a prompt and API key.</h3>"

# Load API key from environment
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable not set.")

# Set the API keys and credits dictionary
API_KEYS = {API_KEY}
API_KEY_CREDITS = {API_KEY: 5}  # 5 credits initially

# Dependency to verify API key
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # Check if the API key has credits remaining
    credits = API_KEY_CREDITS.get(x_api_key, 0)
    if credits <= 0:
        raise HTTPException(status_code=401, detail="No Credits Available")
    
    return x_api_key

# Define request model for JSON input
class PromptRequest(BaseModel):
    prompt: str

# POST endpoint to generate LLM response
@app.post("/generate")
def generate(request: PromptRequest, api_key: str = Depends(verify_api_key)):
    # Deduct a credit
    API_KEY_CREDITS[api_key] -= 1

    # Call Ollama to generate the response
    response = ollama.chat(model="mistral", messages=[
        {"role": "user", "content": request.prompt}
    ])
    
    return {"response": response["message"]["content"]}

# Optional: Endpoint to check remaining credits
@app.get("/credits")
def check_credits(api_key: str = Depends(verify_api_key)):
    return {"credits": API_KEY_CREDITS.get(api_key, 0)}
