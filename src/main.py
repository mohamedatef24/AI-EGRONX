from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import base , data , nlp
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from templates.TemplateParser import TemplateParser


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()
llm_provider_factory = LLMProviderFactory(settings)
vectordb_provider_factory = VectorDBProviderFactory(settings)

app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

# Initialize vector database client
app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
app.vectordb_client.connect()

# Simple template parser for RAG prompts
app.template_parser = TemplateParser()

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)


