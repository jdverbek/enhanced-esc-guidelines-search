"""
Enhanced Main Application
Integrating simplified MedGraphRAG with existing system
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Import existing components
try:
    from simplified_medgraph_rag import SimplifiedMedGraphRAG
except ImportError:
    SimplifiedMedGraphRAG = None

try:
    from guideline_downloader import AsyncGuidelineDownloader
except ImportError:
    AsyncGuidelineDownloader = None

try:
    from enhanced_safety_validator import EnhancedSafetyValidator, PatientProfile
except ImportError:
    EnhancedSafetyValidator = None
    PatientProfile = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global system state
medgraph_system: Optional[SimplifiedMedGraphRAG] = None
safety_validator: Optional[EnhancedSafetyValidator] = None
system_initialized = False

# Pydantic models
class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query for guidelines")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to return")
    society_filter: Optional[str] = Field(default=None, description="Filter by society")
    year_filter: Optional[str] = Field(default=None, description="Filter by year")
    use_verification: bool = Field(default=True, description="Enable verification")

class ClinicalQuery(BaseModel):
    question: str = Field(..., description="Clinical question")
    patient_context: Optional[Dict[str, Any]] = Field(default=None, description="Patient context")
    evidence_level_required: Optional[str] = Field(default=None, description="Evidence level")

class SafetyValidationRequest(BaseModel):
    recommendation: str = Field(..., description="Clinical recommendation")
    patient_profile: Optional[Dict[str, Any]] = Field(default=None, description="Patient profile")
    check_interactions: bool = Field(default=True, description="Check interactions")
    check_contraindications: bool = Field(default=True, description="Check contraindications")

class SystemStatus(BaseModel):
    initialized: bool
    total_chunks: int
    available_guidelines: List[str]
    last_update: Optional[str]
    system_health: str

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Cardiovascular Guidelines Search System",
    description="Simplified MedGraphRAG-powered system for medical guideline search",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_system():
    """Initialize the system"""
    global medgraph_system, safety_validator, system_initialized
    
    try:
        if SimplifiedMedGraphRAG:
            medgraph_system = SimplifiedMedGraphRAG()
            guidelines_dir = Path("ESC_Guidelines")
            
            if guidelines_dir.exists() and list(guidelines_dir.glob("*.pdf")):
                await medgraph_system.initialize_system(guidelines_dir)
                logger.info("MedGraphRAG system initialized")
            else:
                logger.warning("No guidelines found")
        
        if EnhancedSafetyValidator:
            safety_validator = EnhancedSafetyValidator()
            logger.info("Safety validator initialized")
        
        system_initialized = True
        logger.info("System initialization complete")
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        raise

# API Endpoints

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint"""
    return {
        "message": "Enhanced Cardiovascular Guidelines Search System",
        "version": "2.0.0",
        "architecture": "Simplified MedGraphRAG",
        "status": "active" if system_initialized else "initializing",
        "docs": "/docs"
    }

@app.get("/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status"""
    guidelines_dir = Path("ESC_Guidelines")
    available_guidelines = []
    
    if guidelines_dir.exists():
        available_guidelines = [f.name for f in guidelines_dir.glob("*.pdf")]
    
    total_chunks = len(medgraph_system.chunks) if medgraph_system else 0
    
    return SystemStatus(
        initialized=system_initialized,
        total_chunks=total_chunks,
        available_guidelines=available_guidelines,
        last_update=datetime.now().isoformat() if system_initialized else None,
        system_health="healthy" if system_initialized else "initializing"
    )

@app.post("/system/initialize")
async def initialize_system_endpoint(background_tasks: BackgroundTasks):
    """Initialize the system"""
    global system_initialized
    
    if system_initialized:
        return {"message": "System already initialized", "status": "success"}
    
    try:
        # Check for guidelines
        guidelines_dir = Path("ESC_Guidelines")
        if not guidelines_dir.exists() or not list(guidelines_dir.glob("*.pdf")):
            # Try to download guidelines if downloader is available
            if AsyncGuidelineDownloader:
                downloader = AsyncGuidelineDownloader()
                await downloader.download_all_guidelines()
            else:
                # Create sample guidelines directory
                guidelines_dir.mkdir(exist_ok=True)
                logger.info("Created guidelines directory - please add PDF files")
        
        await initialize_system()
        
        return {
            "message": "System initialized successfully",
            "status": "success",
            "total_chunks": len(medgraph_system.chunks) if medgraph_system else 0
        }
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@app.post("/search/enhanced")
async def enhanced_search(query: SearchQuery):
    """Enhanced search using simplified MedGraphRAG"""
    if not system_initialized or not medgraph_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        start_time = time.time()
        
        result = await medgraph_system.search(
            query=query.query,
            top_k=query.top_k,
            use_verification=query.use_verification
        )
        
        # Add performance metrics
        result["performance"] = {
            "search_time_ms": round((time.time() - start_time) * 1000, 2),
            "verification_enabled": query.use_verification
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/clinical")
async def clinical_search(query: ClinicalQuery):
    """Clinical question answering"""
    if not system_initialized or not medgraph_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Enhanced clinical search
        search_query = query.question
        
        if query.patient_context:
            context_str = ", ".join([f"{k}: {v}" for k, v in query.patient_context.items()])
            search_query += f" (Patient context: {context_str})"
        
        result = await medgraph_system.search(
            query=search_query,
            top_k=15,
            use_verification=True
        )
        
        result["query_type"] = "clinical"
        result["patient_context"] = query.patient_context
        
        return result
        
    except Exception as e:
        logger.error(f"Clinical search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Clinical search failed: {str(e)}")

@app.post("/safety/validate")
async def validate_safety(request: SafetyValidationRequest):
    """Validate safety of clinical recommendations"""
    if not system_initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Simplified safety validation
        if safety_validator and PatientProfile:
            # Create patient profile
            profile_data = request.patient_profile or {}
            patient_profile = PatientProfile(
                age=profile_data.get("age"),
                gender=profile_data.get("gender"),
                conditions=profile_data.get("conditions", []),
                medications=profile_data.get("medications", []),
                allergies=profile_data.get("allergies", [])
            )
            
            validation_result = await safety_validator.validate_recommendation(
                recommendation=request.recommendation,
                patient_profile=patient_profile,
                check_interactions=request.check_interactions,
                check_contraindications=request.check_contraindications
            )
            
            return {
                "recommendation": request.recommendation,
                "validation_result": validation_result,
                "patient_profile": request.patient_profile,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Basic safety check using search
            safety_query = f"Safety considerations contraindications: {request.recommendation}"
            
            if medgraph_system:
                result = await medgraph_system.search(safety_query, top_k=5, use_verification=True)
                
                return {
                    "recommendation": request.recommendation,
                    "validation_result": {
                        "overall_safety_score": 0.8,  # Placeholder
                        "risk_level": "medium",
                        "safety_information": result["response"],
                        "relevant_guidelines": result["retrieval_results"]
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise HTTPException(status_code=503, detail="Safety validation not available")
        
    except Exception as e:
        logger.error(f"Safety validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Safety validation failed: {str(e)}")

@app.get("/guidelines/list")
async def list_guidelines():
    """List available guidelines"""
    guidelines_dir = Path("ESC_Guidelines")
    
    if not guidelines_dir.exists():
        return {"guidelines": [], "message": "Guidelines directory not found"}
    
    guidelines = []
    for pdf_file in guidelines_dir.glob("*.pdf"):
        file_stat = pdf_file.stat()
        guidelines.append({
            "filename": pdf_file.name,
            "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        })
    
    return {
        "guidelines": guidelines,
        "total_count": len(guidelines)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if system_initialized else "initializing",
        "timestamp": datetime.now().isoformat(),
        "system_initialized": system_initialized,
        "components": {
            "medgraph_rag": medgraph_system is not None,
            "safety_validator": safety_validator is not None
        }
    }

# Serve static files for frontend
frontend_path = Path("frontend/dist")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend for all non-API routes"""
    if frontend_path.exists():
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        else:
            # Serve index.html for SPA routing
            return FileResponse(frontend_path / "index.html")
    else:
        raise HTTPException(status_code=404, detail="Frontend not built")

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting Enhanced Cardiovascular Guidelines Search System...")
    
    # Check if guidelines exist and initialize
    guidelines_dir = Path("ESC_Guidelines")
    if guidelines_dir.exists() and list(guidelines_dir.glob("*.pdf")):
        try:
            await initialize_system()
        except Exception as e:
            logger.error(f"Startup initialization failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
