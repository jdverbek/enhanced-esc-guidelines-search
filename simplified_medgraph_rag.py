"""
Simplified MedGraphRAG Implementation
Working with existing dependencies in the system
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import re
from datetime import datetime

# Core ML and NLP (using existing dependencies)
import numpy as np
from sentence_transformers import SentenceTransformer

# PDF processing
import fitz  # PyMuPDF

# Hybrid search
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

@dataclass
class MedicalChunk:
    """Simplified medical chunk"""
    id: str
    text: str
    source_doc: str
    page_number: int
    section_hierarchy: List[str]
    chunk_type: str  # parent or child
    parent_chunk_id: Optional[str] = None
    medical_terms: List[str] = None

@dataclass
class RetrievalResult:
    """Retrieval result with provenance"""
    chunk: MedicalChunk
    score: float
    retrieval_method: str
    verification_score: Optional[float] = None

class SimplifiedMedicalExtractor:
    """Simplified medical term extraction using regex patterns"""
    
    def __init__(self):
        # Common medical term patterns
        self.medical_patterns = [
            # Cardiovascular conditions
            r'\b(heart failure|atrial fibrillation|myocardial infarction|angina|arrhythmia|cardiomyopathy)\b',
            # Medications
            r'\b(metoprolol|atenolol|warfarin|aspirin|lisinopril|amlodipine|digoxin|amiodarone)\b',
            # Procedures
            r'\b(angioplasty|bypass|stent|catheterization|echocardiogram|ECG|EKG)\b',
            # Measurements
            r'\b(blood pressure|heart rate|ejection fraction|cholesterol)\b',
            # Dosages
            r'\b\d+\s*(mg|g|mcg|units?)\b',
        ]
        
    def extract_medical_terms(self, text: str) -> List[str]:
        """Extract medical terms from text"""
        terms = []
        text_lower = text.lower()
        
        for pattern in self.medical_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            terms.extend(matches)
        
        return list(set(terms))  # Remove duplicates

class SimplifiedHybridRetriever:
    """Simplified hybrid search"""
    
    def __init__(self, chunks: List[MedicalChunk]):
        self.chunks = chunks
        self.chunk_texts = [chunk.text for chunk in chunks]
        
        # Initialize BM25
        tokenized_corpus = [text.lower().split() for text in self.chunk_texts]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        # Initialize semantic embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings = self.embedding_model.encode(self.chunk_texts)
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}")
            self.embedding_model = None
            self.embeddings = None
        
    def retrieve(self, query: str, top_k: int = 10, bm25_weight: float = 0.4) -> List[RetrievalResult]:
        """Hybrid retrieval"""
        results = []
        
        # BM25 scores
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        if self.embedding_model and self.embeddings is not None:
            # Semantic scores
            query_embedding = self.embedding_model.encode([query])
            semantic_scores = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Normalize scores
            bm25_scores = (bm25_scores - np.min(bm25_scores)) / (np.max(bm25_scores) - np.min(bm25_scores) + 1e-8)
            semantic_scores = (semantic_scores - np.min(semantic_scores)) / (np.max(semantic_scores) - np.min(semantic_scores) + 1e-8)
            
            # Combine scores
            combined_scores = bm25_weight * bm25_scores + (1 - bm25_weight) * semantic_scores
        else:
            # Use only BM25 if embeddings not available
            combined_scores = bm25_scores
        
        # Get top results
        top_indices = np.argsort(combined_scores)[::-1][:top_k]
        
        for idx in top_indices:
            result = RetrievalResult(
                chunk=self.chunks[idx],
                score=float(combined_scores[idx]),
                retrieval_method="hybrid" if self.embedding_model else "bm25"
            )
            results.append(result)
        
        return results

class SimplifiedVerifier:
    """Simplified verification system"""
    
    def __init__(self, chunks: List[MedicalChunk]):
        self.chunks = chunks
        self.chunk_texts = [chunk.text.lower() for chunk in chunks]
        
    def verify_response(self, response: str, retrieved_chunks: List[MedicalChunk]) -> Dict[str, Any]:
        """Simple verification based on text overlap"""
        sentences = self._extract_sentences(response)
        
        verified_facts = []
        unverified_facts = []
        
        for sentence in sentences:
            if self._verify_sentence(sentence, retrieved_chunks):
                verified_facts.append(sentence)
            else:
                unverified_facts.append(sentence)
        
        overall_score = len(verified_facts) / len(sentences) if sentences else 0
        
        # Determine hallucination risk
        if overall_score >= 0.9:
            risk = "low"
        elif overall_score >= 0.7:
            risk = "medium"
        else:
            risk = "high"
        
        return {
            "overall_score": overall_score,
            "verified_facts": verified_facts,
            "unverified_facts": unverified_facts,
            "hallucination_risk": risk
        }
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        sentences = text.split('. ')
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _verify_sentence(self, sentence: str, chunks: List[MedicalChunk]) -> bool:
        """Verify if sentence is supported by chunks"""
        sentence_lower = sentence.lower()
        
        # Extract key terms from sentence
        words = sentence_lower.split()
        key_words = [w for w in words if len(w) > 3]
        
        if not key_words:
            return False
        
        # Check if enough key words appear in any chunk
        for chunk in chunks:
            chunk_text = chunk.text.lower()
            matches = sum(1 for word in key_words if word in chunk_text)
            if matches >= len(key_words) * 0.5:  # At least 50% of key words
                return True
        
        return False

class SimplifiedMedGraphRAG:
    """Simplified MedGraphRAG system"""
    
    def __init__(self):
        self.chunks: List[MedicalChunk] = []
        self.medical_extractor = SimplifiedMedicalExtractor()
        self.retriever: Optional[SimplifiedHybridRetriever] = None
        self.verifier: Optional[SimplifiedVerifier] = None
        
    async def initialize_system(self, pdf_directory: Path):
        """Initialize the system"""
        logger.info("Initializing Simplified MedGraphRAG system...")
        
        # Process PDFs
        await self._process_pdfs(pdf_directory)
        
        # Initialize retriever and verifier
        if self.chunks:
            self.retriever = SimplifiedHybridRetriever(self.chunks)
            self.verifier = SimplifiedVerifier(self.chunks)
        
        logger.info(f"System initialized with {len(self.chunks)} chunks")
    
    async def _process_pdfs(self, pdf_directory: Path):
        """Process PDFs with hierarchical chunking"""
        for pdf_path in pdf_directory.glob("*.pdf"):
            logger.info(f"Processing {pdf_path.name}")
            
            try:
                doc = fitz.open(pdf_path)
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    if len(text.strip()) < 50:
                        continue
                    
                    # Extract medical terms
                    medical_terms = self.medical_extractor.extract_medical_terms(text)
                    
                    # Create parent chunks
                    parent_chunks = self._create_parent_chunks(text, pdf_path.name, page_num + 1, medical_terms)
                    self.chunks.extend(parent_chunks)
                    
                    # Create child chunks
                    for parent_chunk in parent_chunks:
                        child_chunks = self._create_child_chunks(parent_chunk)
                        self.chunks.extend(child_chunks)
                
                doc.close()
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path.name}: {e}")
    
    def _create_parent_chunks(self, text: str, source_doc: str, page_num: int, medical_terms: List[str]) -> List[MedicalChunk]:
        """Create parent chunks"""
        words = text.split()
        chunk_size = 1200  # Approximate tokens
        
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk_text = ' '.join(words[i:i + chunk_size])
            
            chunk = MedicalChunk(
                id=f"{source_doc}_p{page_num}_parent_{i//chunk_size}",
                text=chunk_text,
                source_doc=source_doc,
                page_number=page_num,
                section_hierarchy=[f"Page {page_num}"],
                chunk_type="parent",
                medical_terms=medical_terms
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_child_chunks(self, parent_chunk: MedicalChunk) -> List[MedicalChunk]:
        """Create child chunks"""
        words = parent_chunk.text.split()
        chunk_size = 300
        
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk_text = ' '.join(words[i:i + chunk_size])
            
            chunk = MedicalChunk(
                id=f"{parent_chunk.id}_child_{i//chunk_size}",
                text=chunk_text,
                source_doc=parent_chunk.source_doc,
                page_number=parent_chunk.page_number,
                section_hierarchy=parent_chunk.section_hierarchy,
                chunk_type="child",
                parent_chunk_id=parent_chunk.id,
                medical_terms=parent_chunk.medical_terms
            )
            chunks.append(chunk)
        
        return chunks
    
    async def search(self, query: str, top_k: int = 10, use_verification: bool = True) -> Dict[str, Any]:
        """Main search method"""
        if not self.retriever:
            raise ValueError("System not initialized")
        
        # Retrieve relevant chunks
        retrieval_results = self.retriever.retrieve(query, top_k)
        
        # Generate response
        response = self._generate_response(query, retrieval_results)
        
        # Verify response
        verification_result = None
        if use_verification and self.verifier:
            retrieved_chunks = [r.chunk for r in retrieval_results]
            verification_result = self.verifier.verify_response(response, retrieved_chunks)
        
        return {
            "query": query,
            "response": response,
            "retrieval_results": [
                {
                    "chunk_id": r.chunk.id,
                    "text": r.chunk.text[:200] + "..." if len(r.chunk.text) > 200 else r.chunk.text,
                    "score": r.score,
                    "source": r.chunk.source_doc,
                    "page": r.chunk.page_number,
                    "method": r.retrieval_method
                }
                for r in retrieval_results
            ],
            "verification": verification_result,
            "metadata": {
                "total_chunks_searched": len(self.chunks),
                "retrieval_time": datetime.now().isoformat(),
                "hallucination_risk": verification_result["hallucination_risk"] if verification_result else "unknown"
            }
        }
    
    def _generate_response(self, query: str, results: List[RetrievalResult]) -> str:
        """Generate response from retrieval results"""
        if not results:
            return "No relevant information found in the guidelines."
        
        # Combine top results
        context_texts = [r.chunk.text for r in results[:3]]
        context = "\n\n".join(context_texts)
        
        # Extract medical terms from query and results
        query_terms = self.medical_extractor.extract_medical_terms(query)
        result_terms = []
        for result in results[:3]:
            if result.chunk.medical_terms:
                result_terms.extend(result.chunk.medical_terms)
        
        # Create a focused response
        response = f"""Based on the cardiovascular guidelines, here is the relevant information for your query: "{query}"

Key findings from the guidelines:

{context[:1000]}...

Relevant medical terms identified: {', '.join(set(query_terms + result_terms)[:10])}

Sources: {', '.join(set(r.chunk.source_doc for r in results[:3]))}
Pages: {', '.join(set(str(r.chunk.page_number) for r in results[:3]))}

Note: This information is extracted from medical guidelines. Always consult with healthcare professionals for clinical decisions."""
        
        return response

# Example usage
async def main():
    """Example usage"""
    medgraph = SimplifiedMedGraphRAG()
    
    pdf_directory = Path("ESC_Guidelines")
    if pdf_directory.exists():
        await medgraph.initialize_system(pdf_directory)
        
        # Test search
        result = await medgraph.search("What are the recommendations for heart failure treatment?")
        print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
