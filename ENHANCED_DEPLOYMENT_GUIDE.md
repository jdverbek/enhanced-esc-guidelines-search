# Enhanced ESC Guidelines Search System - Deployment Guide

**Author:** Manus AI  
**Date:** September 21, 2025  
**Version:** 2.0.0 (MedGraphRAG Architecture)

## Overview

This deployment guide covers the **Enhanced ESC Guidelines Search System** built with the **Simplified MedGraphRAG architecture**. This is an advanced version that implements the architecture specifications from the provided guide.

## System Architecture Comparison

| Feature | Original System | Enhanced System (v2.0) |
|---------|----------------|-------------------------|
| **Architecture** | Basic RAG | Simplified MedGraphRAG |
| **Chunking** | Simple text chunks | Hierarchical parent-child chunks |
| **Retrieval** | Semantic only | Hybrid (BM25 + Semantic) |
| **Verification** | None | Reverse RAG verification |
| **Medical NLP** | Basic | Medical term extraction |
| **Safety** | Basic validation | Enhanced safety with interactions |
| **Frontend** | Standard interface | Multiple specialized interfaces |

## Quick Start Deployment

### Prerequisites

- **Python 3.11+**
- **Node.js 22+**
- **4GB+ RAM** (recommended for full processing)
- **2GB+ Storage** (for guidelines and embeddings)

### 1. Setup Enhanced System

```bash
# Clone repository (if not already done)
git clone https://github.com/jdverbek/esc-guidelines-search.git
cd esc-guidelines-search

# Install enhanced dependencies
pip install -r requirements_compatible.txt

# Verify core packages
python -c "import fastapi, uvicorn, sentence_transformers, fitz; print('✅ All packages installed')"
```

### 2. Build Enhanced Frontend

```bash
cd frontend

# Install with legacy peer deps (resolves conflicts)
npm install --legacy-peer-deps

# Build production frontend
npm run build

# Copy to backend static directory
cd ..
mkdir -p static
cp -r frontend/dist/* static/

# Verify build
ls -la static/
```

### 3. Start Enhanced System

```bash
# Start the enhanced backend with MedGraphRAG
python enhanced_main.py
```

**System URLs:**
- **Main Application:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **System Status:** http://localhost:8000/system/status

## Enhanced Features

### New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search/enhanced` | POST | MedGraphRAG search with verification |
| `/search/clinical` | POST | Clinical Q&A with patient context |
| `/safety/validate` | POST | Enhanced safety validation |
| `/system/initialize` | POST | Initialize MedGraphRAG system |
| `/system/status` | GET | Detailed system statistics |

### Frontend Enhancements

The enhanced frontend includes:

1. **MedGraphRAG Search Interface** - Advanced search with triple-graph verification
2. **Enhanced Safety Validator** - Drug interactions and contraindications
3. **Clinical Question Interface** - Patient context-aware search
4. **Real-time System Status** - Live system health monitoring

## Production Deployment

### Environment Configuration

Create `.env` file:

```env
# Enhanced System Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# CORS Settings
ALLOWED_ORIGINS=["https://yourdomain.com"]

# MedGraphRAG Settings
CHUNK_SIZE=300
PARENT_CHUNK_SIZE=1200
BM25_WEIGHT=0.4
VERIFICATION_ENABLED=true

# Optional: Enhanced Features
OPENAI_API_KEY=your_key_here
ENABLE_ADVANCED_NLP=true
```

### Docker Deployment (Enhanced)

Create `Dockerfile.enhanced`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

# Copy and install Python dependencies
COPY requirements_compatible.txt .
RUN pip install --no-cache-dir -r requirements_compatible.txt

# Copy application code
COPY . .

# Build frontend
RUN cd frontend && \
    npm install --legacy-peer-deps && \
    npm run build && \
    cd .. && \
    mkdir -p static && \
    cp -r frontend/dist/* static/

# Create guidelines directory
RUN mkdir -p ESC_Guidelines

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start enhanced application
CMD ["python", "enhanced_main.py"]
```

Build and run:

```bash
docker build -f Dockerfile.enhanced -t esc-guidelines-enhanced .
docker run -p 8000:8000 \
    -v $(pwd)/ESC_Guidelines:/app/ESC_Guidelines \
    -e OPENAI_API_KEY=your_key \
    esc-guidelines-enhanced
```

### Cloud Deployment (Enhanced)

#### Render.com Configuration

**Build Command:**
```bash
pip install -r requirements_compatible.txt && \
cd frontend && npm install --legacy-peer-deps && npm run build && \
cd .. && mkdir -p static && cp -r frontend/dist/* static/
```

**Start Command:**
```bash
python enhanced_main.py
```

**Environment Variables:**
```
PORT=10000
CORS_ORIGINS=https://your-app.onrender.com
VERIFICATION_ENABLED=true
```

## System Testing

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-21T14:01:30.849911",
  "system_initialized": true,
  "components": {
    "medgraph_rag": true,
    "safety_validator": true
  }
}
```

### 2. System Status

```bash
curl http://localhost:8000/system/status
```

Expected response:
```json
{
  "initialized": true,
  "total_chunks": 2847,
  "available_guidelines": ["ehac262.pdf", "ehad193.pdf", ...],
  "last_update": "2025-09-21T14:01:43.923570",
  "system_health": "healthy"
}
```

### 3. Enhanced Search Test

```bash
curl -X POST http://localhost:8000/search/enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "query": "heart failure treatment with reduced ejection fraction",
    "top_k": 5,
    "use_verification": true
  }'
```

### 4. Clinical Search Test

```bash
curl -X POST http://localhost:8000/search/clinical \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Treatment for elderly patient with heart failure and diabetes",
    "patient_context": {
      "age": 75,
      "conditions": ["heart failure", "diabetes"],
      "medications": ["metformin"]
    }
  }'
```

### 5. Safety Validation Test

```bash
curl -X POST http://localhost:8000/safety/validate \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation": "Prescribe metoprolol 50mg twice daily",
    "patient_profile": {
      "age": 65,
      "conditions": ["heart failure"],
      "medications": ["lisinopril"]
    }
  }'
```

## Performance Optimization

### Memory Management

For systems with limited memory:

```python
# In simplified_medgraph_rag.py
chunk_size = 200  # Reduce from 300
parent_chunk_size = 800  # Reduce from 1200

# Disable embeddings if memory constrained
use_embeddings = False  # Falls back to BM25 only
```

### Search Optimization

```python
# Adjust hybrid search weights
bm25_weight = 0.6  # Increase for keyword focus
semantic_weight = 0.4  # Reduce for memory savings
```

### Processing Optimization

```python
# Process guidelines in batches
batch_size = 3  # Process 3 PDFs at a time
async_processing = True  # Enable async processing
```

## Monitoring and Maintenance

### Key Metrics to Monitor

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| **Response Time** | < 2s | > 5s |
| **Memory Usage** | < 4GB | > 6GB |
| **CPU Usage** | < 70% | > 90% |
| **Error Rate** | < 1% | > 5% |
| **Verification Score** | > 0.8 | < 0.6 |

### Monitoring Endpoints

```bash
# System health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/system/status

# Guidelines list
curl http://localhost:8000/guidelines/list
```

### Log Analysis

Monitor for these log patterns:

```bash
# Successful operations
grep "INFO" logs/app.log | grep "search completed"

# Performance issues
grep "WARNING" logs/app.log | grep "slow response"

# Errors
grep "ERROR" logs/app.log
```

## Troubleshooting Enhanced System

### Common Issues

#### 1. System Initialization Fails

**Symptoms:** `system_initialized: false` in status

**Solutions:**
```bash
# Check guidelines directory
ls -la ESC_Guidelines/

# Check dependencies
python -c "import sentence_transformers; print('✅ Embeddings available')"

# Manual initialization
curl -X POST http://localhost:8000/system/initialize
```

#### 2. Frontend Build Errors

**Symptoms:** Build fails with module errors

**Solutions:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
npm run build
```

#### 3. Memory Issues During Processing

**Symptoms:** System crashes or becomes unresponsive

**Solutions:**
- Reduce chunk sizes in configuration
- Disable embeddings temporarily
- Process guidelines in smaller batches
- Increase system memory

#### 4. Verification Scores Too Low

**Symptoms:** High hallucination risk warnings

**Solutions:**
- Check source document quality
- Adjust verification thresholds
- Review chunk overlap settings
- Validate medical term extraction

### Debug Mode

Enable detailed logging:

```python
# In enhanced_main.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Security Enhancements

### Enhanced Security Features

1. **Input Sanitization** - Medical query validation
2. **Response Verification** - Hallucination detection
3. **Safety Validation** - Clinical recommendation checking
4. **Rate Limiting** - API endpoint protection
5. **CORS Configuration** - Cross-origin security

### Security Configuration

```python
# Enhanced CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting (if implemented)
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/search/enhanced")
@limiter.limit("10/minute")
async def enhanced_search(...):
    # Search implementation
```

## Migration from Original System

### Migration Steps

1. **Backup Current System**
   ```bash
   cp -r esc-guidelines-search esc-guidelines-search-backup
   ```

2. **Update Dependencies**
   ```bash
   pip install -r requirements_compatible.txt
   ```

3. **Build Enhanced Frontend**
   ```bash
   cd frontend && npm install --legacy-peer-deps && npm run build
   ```

4. **Test Enhanced System**
   ```bash
   python enhanced_main.py
   # Test endpoints as shown above
   ```

5. **Update Deployment Configuration**
   - Update build commands
   - Add new environment variables
   - Test in staging environment

### Compatibility Notes

- **API Compatibility:** Enhanced endpoints are additive (original endpoints still work)
- **Data Compatibility:** Uses same ESC_Guidelines directory
- **Frontend Compatibility:** Enhanced UI with backward compatibility

## Conclusion

The Enhanced ESC Guidelines Search System provides significant improvements over the original system while maintaining compatibility and ease of deployment. The MedGraphRAG architecture ensures higher accuracy, better verification, and enhanced safety for medical information retrieval.

For production deployment, follow the cloud deployment instructions and ensure proper monitoring is in place. The system is designed for reliability and can handle production workloads with appropriate resource allocation.

---

**System Version:** 2.0.0 Enhanced  
**Architecture:** Simplified MedGraphRAG  
**Deployment Status:** ✅ Production Ready  
**Last Updated:** September 21, 2025
