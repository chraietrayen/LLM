from fastapi import FastAPI, Depends, HTTPException, Header
import ollama
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FastAPI app initialization
app = FastAPI()

# Set the API keys and credits dictionary
API_KEYS = {os.getenv("API_KEY")}
API_KEY_CREDITS = {os.getenv("API_KEY"): 5}  # 5 credits initially

# Dependency to verify API key
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # Check if the API key has credits remaining
    credits = API_KEY_CREDITS.get(x_api_key, 0)
    if credits <= 0:
        raise HTTPException(status_code=401, detail="No Credits Available")
    
    return x_api_key

@app.post("/generate")
def generate(prompt: str, api_key: str = Depends(verify_api_key)):
    # Deduct a credit each time a request is made
    API_KEY_CREDITS[api_key] -= 1

    # Call Ollama to generate the response
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    
    # Return the response from the LLM
    return {"response": response["message"]["content"]}

# Optional: Additional endpoint for checking available credits
@app.get("/credits")
def check_credits(api_key: str = Depends(verify_api_key)):
    return {"credits": API_KEY_CREDITS.get(api_key, 0)}
