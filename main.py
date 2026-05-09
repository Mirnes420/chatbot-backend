import os
import json
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

app = FastAPI(title="Gentleman Solutions Intelligence Layer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure PDFs directory exists and mount it for direct access
os.makedirs("pdfs", exist_ok=True)
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class LeadIntake(BaseModel):
    name: str
    email: str
    business_volume: str
    tech_stack: str
    primary_goal: str

class LeadResponse(BaseModel):
    priority: str
    roadmap: str
    action_item: str
    pdf_url: str

def generate_pdf(name: str, roadmap: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style="B")
    pdf.cell(200, 10, txt=f"Technical Architecture: {name}", ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    # fpdf handles latin-1 better than utf-8 by default; replace common edge cases
    clean_roadmap = roadmap.replace("**", "").replace("*", "- ").encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 8, txt=clean_roadmap)
    
    filename = f"pdfs/roadmap_{uuid.uuid4().hex[:8]}.pdf"
    pdf.output(filename)
    return filename

@app.post("/analyze-lead", response_model=LeadResponse)
async def analyze_lead(lead: LeadIntake):
    try:
        # Structured prompt for high-leverage outcomes
        prompt = f"""
        ACT AS: Elite AI Automation Architect.
        USER DATA:
        - Name: {lead.name}
        - Email: {lead.email}
        - Volume: {lead.business_volume}
        - Stack: {lead.tech_stack}
        - Goal: {lead.primary_goal}

        TASK:
        1. Identify the 'Hidden Inefficiency' in their tech stack or goal.
        2. Categorize Priority (High/Medium/Low).
        3. Create a 4-step 'Bespoke Implementation Roadmap' focusing on AI Integration and ROI.
        
        TONE: Direct, technical, engineering-focused. No marketing fluff.

        SCHEMA:
        {{
            "priority": "string",
            "roadmap": "string",
            "action_item": "Forward to Founder | Send Booking Link | Send Resources"
        }}
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # response.text is guaranteed to be JSON string due to response_mime_type
        result = json.loads(response.text)
        
        # Generate the PDF
        pdf_path = generate_pdf(lead.name, result.get("roadmap", ""))
        
        # Use an environment variable for the base URL in production
        base_url = os.getenv("BASE_URL", "http://localhost:8888")
        
        return LeadResponse(
            priority=result.get("priority", "Medium Priority"),
            roadmap=result.get("roadmap", "Analysis complete."),
            action_item=result.get("action_item", "Send Booking Link"),
            pdf_url=f"{base_url}/{pdf_path}"
        )
        
    except Exception as e:
        print(f"Error processing lead: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error analyzing lead")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)