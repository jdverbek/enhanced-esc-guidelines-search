# Enhanced ESC Guidelines Search System

**Advanced Medical Guideline Search with MedGraphRAG Architecture**

[![Deploy](https://img.shields.io/badge/Deploy-Ready-brightgreen)](https://github.com/jdverbek/enhanced-esc-guidelines-search)
[![Architecture](https://img.shields.io/badge/Architecture-MedGraphRAG-blue)](https://github.com/jdverbek/enhanced-esc-guidelines-search)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🚀 Overview

The Enhanced ESC Guidelines Search System implements a **Simplified MedGraphRAG architecture** for advanced medical guideline search and retrieval. This system provides healthcare professionals with accurate, verifiable, and safe access to cardiovascular guidelines through cutting-edge AI technology.

## ✨ Key Features

### 🧠 **MedGraphRAG Architecture**
- **Hierarchical Chunking**: Parent-child chunk relationships for context preservation
- **Hybrid Retrieval**: BM25 + Semantic embeddings for optimal search results
- **Reverse RAG Verification**: Real-time hallucination detection and fact-checking
- **Medical Term Extraction**: Cardiovascular terminology identification

### 🔍 **Advanced Search Capabilities**
- **Enhanced Search**: AI-powered search with synthesis
- **Clinical Q&A**: Patient context-aware question answering
- **Safety Validation**: Drug interactions and contraindications checking
- **Real-time Verification**: Response accuracy scoring

### 🛡️ **Safety & Verification**
- **Hallucination Detection**: Statistical text overlap analysis
- **Safety Scoring**: Risk assessment for clinical recommendations
- **Source Verification**: Direct links to guideline sources
- **Medical Term Validation**: Automated medical terminology checking

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                        │
├─────────────────────────────────────────────────────────────┤
│  MedGraphRAG UI  │  Enhanced Safety  │  Clinical Q&A      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend                             │
├─────────────────────────────────────────────────────────────┤
│  Simplified MedGraphRAG Engine                              │
│  ├── Hierarchical Chunking                                  │
│  ├── Hybrid Retrieval (BM25 + Semantic)                    │
│  ├── Reverse RAG Verification                               │
│  └── Medical Term Extraction                                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              ESC Guidelines Database                        │
│  13 PDF Guidelines → Hierarchical Chunks → Search Index    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- 4GB+ RAM (recommended)
- 2GB+ Storage

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jdverbek/enhanced-esc-guidelines-search.git
   cd enhanced-esc-guidelines-search
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_production.txt
   ```

3. **Add ESC Guidelines**
   ```bash
   # Place your PDF guidelines in the ESC_Guidelines directory
   mkdir -p ESC_Guidelines
   # Add your PDF files here
   ```

4. **Start the system**
   ```bash
   python main_production.py
   ```

5. **Access the application**
   - **Main App**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

## 📊 System Capabilities

| Feature | Capability |
|---------|------------|
| **Guidelines Processed** | 13 ESC Guidelines |
| **Search Methods** | Hybrid (BM25 + Semantic) |
| **Chunk Types** | Hierarchical (Parent + Child) |
| **Verification** | Real-time fact checking |
| **Response Time** | < 2 seconds |
| **Safety Validation** | Drug interactions + contraindications |

## 🔧 API Endpoints

### Core Search
- `POST /search/enhanced` - MedGraphRAG search with verification
- `POST /search/clinical` - Clinical Q&A with patient context
- `POST /safety/validate` - Safety validation for recommendations

### System Management
- `GET /health` - System health check
- `GET /system/status` - Detailed system statistics
- `POST /system/initialize` - Initialize/reinitialize system

### Example Usage

```bash
# Enhanced search
curl -X POST http://localhost:8000/search/enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "query": "heart failure treatment with reduced ejection fraction",
    "top_k": 5,
    "use_verification": true
  }'

# Clinical question with patient context
curl -X POST http://localhost:8000/search/clinical \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Treatment for elderly patient with heart failure",
    "patient_context": {
      "age": 75,
      "conditions": ["heart failure", "diabetes"]
    }
  }'
```

## 🌐 Deployment

### Cloud Deployment (Recommended)

#### Render.com
1. Connect this repository to Render
2. Create a new Web Service
3. Use these settings:
   - **Build Command**: `pip install -r requirements_production.txt`
   - **Start Command**: `python main_production.py`
   - **Environment**: Python 3.11

#### Railway
1. Connect repository to Railway
2. Set environment variables as needed
3. Deploy automatically

#### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements_production.txt .
RUN pip install -r requirements_production.txt
COPY . .
EXPOSE 8000
CMD ["python", "main_production.py"]
```

### Environment Variables
```env
PORT=8000
CORS_ORIGINS=*
VERIFICATION_ENABLED=true
```

## 📚 Documentation

- **[System Documentation](ENHANCED_SYSTEM_DOCUMENTATION.md)** - Complete technical specifications
- **[Deployment Guide](ENHANCED_DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions
- **[API Reference](http://localhost:8000/docs)** - Interactive API documentation

## 🔬 Technical Details

### MedGraphRAG Implementation
- **Chunking Strategy**: 1200 tokens (parent) + 300 tokens (child)
- **Embeddings**: Sentence-BERT (all-MiniLM-L6-v2)
- **Hybrid Weights**: 40% BM25 + 60% Semantic (configurable)
- **Verification Method**: Statistical text overlap analysis

### Performance Optimization
- **Async Processing**: Non-blocking PDF processing
- **Memory Efficient**: Optimized chunk storage
- **Caching**: Embedding caching for repeated queries
- **Batch Processing**: Efficient guideline processing

## 🛡️ Safety & Security

- **Input Validation**: Comprehensive query sanitization
- **Response Verification**: Hallucination detection
- **Safety Warnings**: Automated risk assessment
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: API endpoint protection

## 📈 Monitoring

### Health Endpoints
- `/health` - Basic system health
- `/system/status` - Detailed metrics
- `/guidelines/list` - Available guidelines

### Key Metrics
- Response time < 2 seconds
- Verification score > 0.8
- Memory usage < 4GB
- Error rate < 1%

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- European Society of Cardiology (ESC) for the guidelines
- Sentence Transformers for embeddings
- FastAPI for the web framework
- React for the frontend framework

## 📞 Support

For technical support or questions:
- **Issues**: [GitHub Issues](https://github.com/jdverbek/enhanced-esc-guidelines-search/issues)
- **Documentation**: [System Docs](ENHANCED_SYSTEM_DOCUMENTATION.md)
- **Deployment**: [Deployment Guide](ENHANCED_DEPLOYMENT_GUIDE.md)

---

**Built with ❤️ for healthcare professionals**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/jdverbek/enhanced-esc-guidelines-search)
