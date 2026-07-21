import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.budget import LLMBudget
from agent.generator import generate_project
from agent.self_heal import self_heal
from agent.validator import run_validation

app = FastAPI(title="ForgePilot Web API")

# Enable CORS so your frontend (Vercel, React, HTML) can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    goal: str

@app.post("/api/generate")
async def generate_code_endpoint(req: GenerateRequest):
    if not req.goal.strip():
        raise HTTPException(status_code=400, detail="Goal cannot be empty.")

    budget = LLMBudget(limit=2)

    # Create an isolated temporary directory for THIS user's execution
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_path = Path(temp_dir)

        # 1. Generation Phase
        try:
            result = generate_project(req.goal, budget)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

        # Write files into the temp directory
        for filename, content in result["files"].items():
            (workspace_path / filename).write_text(content)

        # 2. Validation Phase
        ok, err = run_validation(workspace_path)
        if ok:
            return {
                "status": "success",
                "healed": False,
                "files": result["files"]
            }

        # 3. Self-Heal Phase if initial validation fails
        try:
            healed_result = self_heal(req.goal, err, budget)
            
            # Clear old files and write healed files
            for p in workspace_path.iterdir():
                if p.is_file(): p.unlink()

            for filename, content in healed_result["files"].items():
                (workspace_path / filename).write_text(content)

            # Re-validate
            ok_healed, heal_err = run_validation(workspace_path)
            if ok_healed:
                return {
                    "status": "success",
                    "healed": True,
                    "files": healed_result["files"]
                }
            else:
                raise HTTPException(
                    status_code=422, 
                    detail=f"Validation failed after self-heal:\n{heal_err}"
                )

        except Exception as heal_exception:
            # Fallback response showing the initial pytest failure if self-heal JSON parsing fails
            raise HTTPException(
                status_code=422,
                detail=f"Initial validation failed:\n{err}\n\nSelf-heal failed: {str(heal_exception)}"
            )
