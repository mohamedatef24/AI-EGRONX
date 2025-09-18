from .BaseController import BaseController
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json


class NLPController(BaseController):

    def __init__(self, vectordb_client, generation_client,
                 embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project):
        collection_name = self.create_collection_name(project_id=project["project_id"])
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project):
        collection_name = self.create_collection_name(project_id=project["project_id"])
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_into_vector_db(self, project, chunks: List, chunks_ids: List[int],
                             do_reset: bool = False, batch_size: int = 64):
        
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project["project_id"])

        # step2: manage items
        texts = [ c.page_content for c in chunks ]
        metadata = [ c.metadata for c in chunks ]
        # Embed in batches to respect provider rate limits
        vectors = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            # Use provider batch embedding if available
            if hasattr(self.embedding_client, 'embed_texts'):
                batch_vectors = self.embedding_client.embed_texts(
                    texts=batch_texts,
                    document_type=DocumentTypeEnum.DOCUMENT.value
                )
            else:
                batch_vectors = [
                    self.embedding_client.embed_text(
                        text=t, document_type=DocumentTypeEnum.DOCUMENT.value
                    ) for t in batch_texts
                ]
            vectors.extend(batch_vectors)

        # step3: create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step4: insert into vector db
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True

    def search_vector_db_collection(self, project, text: str, limit: int = 10):

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project["project_id"])

        # step2: get text embedding vector
        vector = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypeEnum.QUERY.value)

        if not vector or len(vector) == 0:
            return False

        # step3: do semantic search
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False

        return results
    
    def answer_rag_question(self, project, query: str, limit: int = 10):
        
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": doc.text,
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt")

        # step3: Construct Generation Client Prompts
        # Choose system role string per provider
        system_role = "system"
        if self.generation_client.__class__.__name__ == "CoHereProvider":
            system_role = "SYSTEM"

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=system_role,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        # step4: Retrieve the Answer with graceful fallback on provider errors
        try:
            answer = self.generation_client.generate_text(
                prompt=full_prompt,
                chat_history=chat_history
            )
        except Exception:
            answer = None

        if not answer:
            # Fallback: return the highest-ranked document text as a best-effort answer
            top_doc = retrieved_documents[0]
            answer = top_doc.text

        return answer, full_prompt, chat_history
