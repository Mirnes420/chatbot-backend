# Gentleman Solutions Intelligence Layer

An automated, asynchronous, high-leverage lead analysis backend engine built using FastAPI and powered by the Google Gemini API. This application qualifies prospects instantly, structures systemic technical implementation blueprints, and synthesizes dynamic client deliverables.

## Architectural Capabilities
- **Automated Lead Triage:** Ingests unstructured lead profiles and extracts system gaps.
- **Structured JSON Synthesis:** Enforces hard contracts with LLMs utilizing native schemas via `gemini-2.5-flash-lite`.
- **Dynamic Asset Generation:** Generates on-demand PDF roadmaps mapping out custom AI and integration targets.
- **Production Ready Deployment:** Pre-configured for direct execution on platforms like Render or Railway.

## Tech Stack & Dependencies
- **Runtime:** Python 3.10+
- **Framework:** FastAPI (Asynchronous Web Gateway)
- **Engine:** Google GenAI SDK (`gemini-2.5-flash-lite`)
- **Data Validation:** Pydantic v2
- **Document Rendering:** FPDF

## Step-by-Step Local Deployment

### 1. Environment Setup
Clone the repository and spin up an isolated virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```
2. Configuration (.env)
Create a .env file within the base root directory of the project:

Code snippet
```
GEMINI_API_KEY=your_live_gemini_api_key_here
BASE_URL=http://localhost:8888
PORT=8888
```
3. Running the Server
Execute the application entry script directly:

```
Bash
python main.py
```
The server will bind to http://0.0.0.0:8888. You can interact with the interactive visual documentation at http://localhost:8888/docs.

API Reference
Analyze Inbound Lead Profile
Endpoint: POST /analyze-lead

Content-Type: application/json

Request Schema:
```
JSON
{
  "name": "Alex Mercer",
  "email": "alex@mercerlabs.io",
  "business_volume": "$500k/year ARR",
  "tech_stack": "React, Node.js, PostgreSQL, manual data entry via Excel",
  "primary_goal": "Automate data matching and scale system operations by 4x without scaling headcount"
}
```
Response Contract:
```
JSON
{
  "priority": "High Priority",
  "roadmap": "1. Audit manual spreadsheets... 2. Establish vector data layers... 3. Integrate Gemini processing queues... 4. Establish validation feedback loops.",
  "action_item": "Forward to Founder",
  "pdf_url": "http://localhost:8888/pdfs/roadmap_a1b2c3d4.pdf"
}
```
System Production Deployments (Render / Railway)
When deploying this backend to production setups:

Override the BASE_URL environment variable within your platform dashboard to point directly to your live production domain (e.g., https://api.gentlemansolutions.com).

Ensure disk persistence storage configurations are mounted if utilizing ephemeral systems, or use external storage if handling large file retention profiles.
