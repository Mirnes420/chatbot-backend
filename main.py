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

# Pulling environment variables from .env file before starting the app core
load_dotenv()

app = FastAPI(title="Gentleman Solutions Intelligence Layer")

# ==========================================
# 1. CORS CONFIGURATION
# ==========================================
# Allows external frontends (e.g., Vercel, Bubble, Webflow) to hit this backend 
# without triggering browser blockades.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. FILE SYSTEM & ROUTING STORAGE
# ==========================================
# Persist generated PDF roadmaps on disk. Mounting static files lets clients 
# download files directly via URL without writing custom stream endpoints.
os.makedirs("pdfs", exist_ok=True)
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

# Initialize the modern Google GenAI SDK client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 3. DATA VALIDATION SCHEMAS (Pydantic)
# ==========================================
class LeadIntake(BaseModel):
    """Strict validation layer for inbound webhooks and frontend forms."""
    name: str
    email: str
    business_volume: str
    tech_stack: str
    primary_goal: str

class LeadResponse(BaseModel):
    """The unified outbound response structure sent back to the client application."""
    priority: str
    roadmap: str
    action_item: str
    pdf_url: str

# ==========================================
# 4. COMPONENT FUNCTIONS
# ==========================================
def generate_pdf(name: str, roadmap: str) -> str:
    """Generates a dynamic technical asset on-the-fly for lead qualification."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header block Configuration
    pdf.set_font("Arial", size=16, style="B")
    pdf.cell(200, 10, txt=f"Technical Architecture: {name}", ln=1, align='C')
    pdf.ln(10)
    
    # Body configuration
    pdf.set_font("Arial", size=12)
    
    # FPDF1 lacks out-of-the-box UTF-8 support and breaks on markdown formatting. 
    # This strips markdown symbols and forces standard Latin-1 strings.
    clean_roadmap = roadmap.replace("**", "").replace("*", "- ").encode('latin-1', 'replace').decode('latin-1')
    
    # multi_cell automatically calculates line wraps so text does not bleed off the page margins
    pdf.multi_cell(0, 8, txt=clean_roadmap)
    
    # Use short UUID hashes to guarantee clean, non-clashing file naming structures
    filename = f"pdfs/roadmap_{uuid.uuid4().hex[:8]}.pdf"
    pdf.output(filename)
    return filename

# ==========================================
# 5. CORE ENDPOINT / INTELLIGENCE LAYER
# ==========================================
@app.post("/analyze-lead", response_model=LeadResponse)
async def analyze_lead(lead: LeadIntake):
    """
    Ingests inbound lead profiles, executes an automated technical qualification 
    via Gemini, generates a custom client deliverable PDF, and returns routing targets.
    """
    try:
        # High-leverage prompt explicitly engineered for zero fluff, asymmetric output 
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

        # Using gemini-2.5-flash-lite for cost efficiency and ultra-low latency execution profiles
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # Parse the verified JSON payload string directly into a Python dictionary
        result = json.loads(response.text)
        
        # Build the physical client PDF deliverable
        pdf_path = generate_pdf(lead.name, result.get("roadmap", ""))
        
        # Ensure we read the correct host URL domain when running in live multi-tier environments
        base_url = os.getenv("BASE_URL", "http://localhost:8888")
        
        return LeadResponse(
            priority=result.get("priority", "Medium Priority"),
            roadmap=result.get("roadmap", "Analysis complete."),
            action_item=result.get("action_item", "Send Booking Link"),
            pdf_url=f"{base_url}/{pdf_path}"
        )
        
    except Exception as e:
        # Avoid swallowing errors into silence; capture tracing in stdout logs
        print(f"Error processing lead: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error analyzing lead")

# ==========================================
# 6. SERVER ENTRY POINT
# ==========================================
if __name__ == "__main__":
    import uvicorn
    # Port configuration explicitly matches Render platform expectations
    port = int(os.environ.get("PORT", 8888))
    uvicorn.run(app, host="0.0.0.0", port=port)
