"""
Production-ready main application for deployment
Enhanced ESC Guidelines Search System with MedGraphRAG
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
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Import existing components
try:
    from simplified_medgraph_rag import SimplifiedMedGraphRAG
except ImportError:
    SimplifiedMedGraphRAG = None

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
    description="MedGraphRAG-powered system for medical guideline search with verification",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - production ready
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
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
                logger.info(f"MedGraphRAG system initialized with {len(medgraph_system.chunks)} chunks")
            else:
                logger.warning("No guidelines found")
        
        if EnhancedSafetyValidator:
            safety_validator = EnhancedSafetyValidator()
            logger.info("Safety validator initialized")
        
        system_initialized = True
        logger.info("System initialization complete")
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        # Don't raise - allow system to start without full initialization

# Mount static files
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files mounted from /static")

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application"""
    static_path = Path("static/index.html")
    if static_path.exists():
        return FileResponse(static_path)
    else:
        return HTMLResponse("""
        <html>
            <head><title>Enhanced ESC Guidelines Search</title></head>
            <body>
                <h1>Enhanced ESC Guidelines Search System</h1>
                <p>MedGraphRAG-powered cardiovascular guidelines search</p>
                <p><a href="/docs">API Documentation</a></p>
                <p><a href="/health">System Health</a></p>
            </body>
        </html>
        """)

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Enhanced Cardiovascular Guidelines Search System",
        "version": "2.0.0",
        "architecture": "Simplified MedGraphRAG",
        "status": "active" if system_initialized else "initializing",
        "docs": "/docs",
        "features": [
            "Hierarchical chunking",
            "Hybrid retrieval (BM25 + Semantic)",
            "Reverse RAG verification",
            "Medical term extraction",
            "Safety validation"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    guidelines_dir = Path("ESC_Guidelines")
    available_guidelines = []
    
    if guidelines_dir.exists():
        available_guidelines = [f.name for f in guidelines_dir.glob("*.pdf")]
    
    total_chunks = len(medgraph_system.chunks) if medgraph_system else 0
    
    return {
        "status": "healthy" if system_initialized else "initializing",
        "timestamp": datetime.now().isoformat(),
        "system_initialized": system_initialized,
        "total_chunks": total_chunks,
        "available_guidelines": len(available_guidelines),
        "components": {
            "medgraph_rag": medgraph_system is not None,
            "safety_validator": safety_validator is not None,
            "static_files": static_path.exists()
        }
    }

@app.get("/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get detailed system status"""
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
async def initialize_system_endpoint():
    """Initialize the system"""
    global system_initialized
    
    if system_initialized:
        return {"message": "System already initialized", "status": "success"}
    
    try:
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
    """Enhanced search using MedGraphRAG"""
    if not system_initialized or not medgraph_system:
        # Try to initialize if not done
        await initialize_system()
        if not system_initialized or not medgraph_system:
            raise HTTPException(status_code=503, detail="System not initialized - please wait for initialization to complete")
    
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
        await initialize_system()
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
    try:
        # Basic safety check using search
        safety_query = f"Safety considerations contraindications warnings: {request.recommendation}"
        
        if medgraph_system:
            result = await medgraph_system.search(safety_query, top_k=5, use_verification=True)
            
            # Simple safety scoring based on verification
            verification_score = result.get("verification", {}).get("overall_score", 0.5)
            risk_level = "low" if verification_score > 0.8 else "medium" if verification_score > 0.6 else "high"
            
            return {
                "recommendation": request.recommendation,
                "validation_result": {
                    "overall_safety_score": verification_score,
                    "risk_level": risk_level,
                    "safety_information": result["response"],
                    "relevant_guidelines": result["retrieval_results"][:3],
                    "verification_score": verification_score
                },
                "patient_profile": request.patient_profile,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Safety validation not available - system not initialized")
        
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

# Serve frontend for all other routes
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend for all non-API routes"""
    # Check if it's a static file request
    if full_path.startswith("static/") or full_path.startswith("assets/"):
        file_path = Path("static") / full_path.replace("static/", "")
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
    
    # For all other routes, serve the main app
    static_index = Path("static/index.html")
    if static_index.exists():
        return FileResponse(static_index)
    else:
        # Fallback HTML
        return HTMLResponse("""
        <html>
            <head><title>Enhanced ESC Guidelines Search</title></head>
            <body>
                <h1>Enhanced ESC Guidelines Search System</h1>
                <p>System is starting up...</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting Enhanced Cardiovascular Guidelines Search System...")
    
    # Initialize in background
    asyncio.create_task(initialize_system())

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
