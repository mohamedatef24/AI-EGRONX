from .BaseController import BaseController
from .ProjectController import ProjectController
import os
import json
import logging
from langchain_community.document_loaders import JSONLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from models import ProcessingEnum

class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        """Get file extension including the dot (e.g., '.json', '.csv')"""
        return os.path.splitext(file_id.lower())[-1]

    def get_file_loader(self, file_id: str):
        """Get appropriate loader for the file based on its extension"""
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(self.project_path, file_id)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_ext == ProcessingEnum.JSON.value:
            return self.load_custom_json(file_path)
        elif file_ext == ProcessingEnum.CSV.value:
            return CSVLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")

    def load_custom_json(self, file_path: str):
        """Custom JSON loader for Q&A dataset structure"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            documents = []
            
            # Extract data array from JSON structure
            qa_data = data.get('data', [])
            dataset_info = data.get('dataset_info', {})
            
            for item in qa_data:
                # Create content combining question and answer
                content = f"Question: {item.get('question', '')}\nAnswer: {item.get('answer', '')}"
                
                # Create metadata for each Q&A pair
                metadata = {
                    'language': item.get('language', 'unknown'),
                    'category': item.get('category', 'unknown'),
                    'keywords': item.get('keywords', []),
                    'source': item.get('source', 'unknown'),
                    'file_path': file_path,
                    'dataset_total_samples': dataset_info.get('total_samples', 0),
                    'dataset_languages': dataset_info.get('languages', [])
                }
                
                # Create Document object
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logging.error(f"Failed to load custom JSON file {file_path}: {str(e)}")
            raise

    def get_file_content(self, file_id: str):
        """Load and return file content using appropriate loader"""
        try:
            file_ext = self.get_file_extension(file_id=file_id)
            
            if file_ext == ProcessingEnum.JSON.value:
                # For JSON, we already return Document objects from our custom loader
                return self.get_file_loader(file_id)
            else:
                # For CSV and other formats, use standard loaders
                loader = self.get_file_loader(file_id)
                content = loader.load()
                
                if not content:
                    raise ValueError(f"No content loaded from file: {file_id}")
                    
                return content
        except Exception as e:
            logging.error(f"Failed to load file content for {file_id}: {str(e)}")
            raise

    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int = None, overlap_size: int = 20):
        """Process file content into chunks"""
        
        if not file_content:
            raise ValueError("File content is empty")
        
        if chunk_size is None:
            chunk_size = self.app_settings.FILE_DEFAULT_CHUNK_SIZE

        # For Q&A datasets, we want to keep each Q&A pair as a separate chunk
        # rather than splitting them further
        file_ext = self.get_file_extension(file_id=file_id)
        
        if file_ext == ProcessingEnum.JSON.value:
            # For Q&A JSON data, return as-is (each Q&A pair is already a good chunk)
            return file_content
        else:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=overlap_size,
                length_function=len,
            )

            try:
                # Extract text content and metadata
                file_content_texts = [rec.page_content for rec in file_content]
                file_content_metadata = [rec.metadata for rec in file_content]

                # Create chunks
                chunks = text_splitter.create_documents(
                    file_content_texts,
                    metadatas=file_content_metadata
                )

                return chunks
                
            except Exception as e:
                logging.error(f"Failed to process file content for {file_id}: {str(e)}")
                raise

    def process_file(self, file_id: str, chunk_size: int = None, overlap_size: int = 20):
        """Complete pipeline: load file content and process it into chunks"""
        try:
            # Load file content
            file_content = self.get_file_content(file_id)
            
            # Process into chunks
            chunks = self.process_file_content(
                file_content=file_content,
                file_id=file_id,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )
            
            return chunks
            
        except Exception as e:
            logging.error(f"Failed to process file {file_id}: {str(e)}")
            raise

    def get_qa_pairs_by_language(self, file_id: str, language: str = None):
        """Get Q&A pairs filtered by language"""
        try:
            file_ext = self.get_file_extension(file_id=file_id)
            
            if file_ext != ProcessingEnum.JSON.value:
                raise ValueError("Language filtering only supported for JSON files")
            
            content = self.get_file_content(file_id)
            
            if language:
                filtered_content = [
                    doc for doc in content 
                    if doc.metadata.get('language') == language
                ]
                return filtered_content
            
            return content
            
        except Exception as e:
            logging.error(f"Failed to filter Q&A pairs by language: {str(e)}")
            raise

    def get_qa_pairs_by_category(self, file_id: str, category: str = None):
        """Get Q&A pairs filtered by category"""
        try:
            file_ext = self.get_file_extension(file_id=file_id)
            
            if file_ext != ProcessingEnum.JSON.value:
                raise ValueError("Category filtering only supported for JSON files")
            
            content = self.get_file_content(file_id)
            
            if category:
                filtered_content = [
                    doc for doc in content 
                    if doc.metadata.get('category') == category
                ]
                return filtered_content
            
            return content
            
        except Exception as e:
            logging.error(f"Failed to filter Q&A pairs by category: {str(e)}")
            raise