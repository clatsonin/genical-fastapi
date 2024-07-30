from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Google Generative AI API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables")

genai.configure(api_key=api_key)

# Initialize FastAPI
app = FastAPI()


# Define request model
class QuestionRequest(BaseModel):
    question: str


async def get_gemini_response(question: str) -> str:
    try:
        model = genai.GenerativeModel('gemini-pro')
        agent = "Pharmacists"
        command = """Generate a response that is easy to understand for someone without a medical background. 
Focus on providing details about the medicine's information, primary purpose, precautions or side effects, history, dosage, and common medical formula. 
For the common formula, mention only one main chemical formula. 
Ensure each answer is less than 50 words and easy to understand for someone without a medical background."""
        json_format = """{[
          "response": 
            {
              "medicine_name": "string",
              "medicine_information": "string",
              "history": "string",
              "primary_purpose": "string",
              "precautions": "string",
              "chemical_formula": "string",
              "dosage": "string"
            }]
        }"""

        question = f"You are {agent}. Follow these commands {command} for this medicine:{question}.Output in dictionary with this format {json_format} without triple quotes."
        response = model.generate_content(question)
        response = ' '.join(response.text.split())
        # Remove the surrounding square brackets
        if response.startswith('[') and response.endswith(']'):
            response = response[1:-1]
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Define endpoint to get Gemini response
@app.post("/get-gemini-response/")
async def get_gemini_response_endpoint(request: QuestionRequest):
    response = await get_gemini_response(request.question)
    return {response}
