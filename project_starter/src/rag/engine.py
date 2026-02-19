# src\rag\engine.py
import os
import hashlib
import logging
import chromadb
import glob
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import pdfplumber
import requests
from bs4 import BeautifulSoup

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class RecursiveChunker:

    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""] 
        )

    def split_text(self, text: str) -> list[str]:
        return self.splitter.split_text(text)

class RAGEngine:
    def __init__(self, persist_directory="./chroma_db", collection_name="research_papers"):
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        #embedding
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="intfloat/multilingual-e5-base",
            device="cpu"
        )
        
        # HNSW and similarity (using Cosine similarity)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 200,
                "hnsw:search_ef": 100,
                "hnsw:M": 16,
            }
        )
        
        #Chunking   
        self.chunker = RecursiveChunker(chunk_size=1000, chunk_overlap=200)
     # generate id for each chunk
    def _generate_id(self, text: str, source: str) -> str:
        unique_str = f"{source}_{text}"
        return hashlib.md5(unique_str.encode("utf-8")).hexdigest()

    def add_documents(self, documents: list[dict], batch_size: int = 100):
        total_docs = len(documents)
        for i in range(0, total_docs, batch_size):
            batch = documents[i : i + batch_size]
            
            unique_docs = {}
            for doc in batch:
                text_content = doc["text"]
                source = doc["source"]
                doc_id = self._generate_id(text_content, source)
                
                if doc_id not in unique_docs:
                    unique_docs[doc_id] = {
                        "id": doc_id,
                        "text": f"passage: {text_content}",
                        "metadata": {"source": source, "original_text": text_content}
                    }
            
            ids = [d["id"] for d in unique_docs.values()]
            texts = [d["text"] for d in unique_docs.values()]
            metadatas = [d["metadata"] for d in unique_docs.values()]

            if not ids:
                continue

            try:
                self.collection.upsert(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
                logger.info(f"Batch {i//batch_size + 1} added/updated successfully.")
            except Exception as e:
                logger.error(f"Error adding batch: {e}")
                
    def ingest_pdf(self, file_path: str):
        try:
            full_text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
            
            chunks = self.chunker.split_text(full_text)
            
            docs_to_add = [{"text": chunk, "source": os.path.basename(file_path)} for chunk in chunks]
            self.add_documents(docs_to_add)
            
            print(f" Processed PDF with RecursiveChunker: {os.path.basename(file_path)} ({len(chunks)} chunks)")
        except Exception as e:
            print(f" Error reading PDF {file_path}: {e}")
            
    def ingest_directory(self, directory_path: str):

        pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
        print(f" Found {len(pdf_files)} PDFs in {directory_path}...")
        
        for pdf_file in pdf_files:
            self.ingest_pdf(pdf_file)        

    def ingest_url(self, url: str):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            clean_text = '\n'.join(chunk for chunk in lines if chunk)

            
            chunks = self.chunker.split_text(clean_text)
            
            docs_to_add = [{"text": chunk, "source": url} for chunk in chunks]
            self.add_documents(docs_to_add)
            
            print(f"Processed URL with RecursiveChunker: {url} ({len(chunks)} chunks)")
        except Exception as e:
            print(f"Error reading URL {url}: {e}")

    def search(self, query: str, n_results: int = 5) -> list[dict]: # top-k =5
        query_text = f"query: {query}"
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["metadatas", "distances", "documents"]
        )
        
        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i]
                similarity = 1 - distance 
                
                metadata = results['metadatas'][0][i]
                original_text = metadata.get("original_text", results['documents'][0][i])

                formatted_results.append({
                    "text": original_text,
                    "source": metadata.get("source", "Unknown"),
                    "score": round(similarity, 4)
                })
                
        return formatted_results

rag_engine = RAGEngine()

