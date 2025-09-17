from fastapi import FastAPI
from routes import base,data
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory


app = FastAPI()

settings = get_settings()
llm_provider_factory = LLMProviderFactory(settings)

app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

app.include_router(base.base_router)
app.include_router(data.data_router)


