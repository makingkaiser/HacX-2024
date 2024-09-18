from dotenv import load_dotenv
import os
import openai
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient
import asyncio

# Load environment variables from .env file
load_dotenv()

def initialize_openai_client():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai

def initialize_azure_openai_client():
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    return AzureOpenAI(
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_api_key,
        api_version="2024-06-01"
    )

def initialize_blob_service_client():
    connection_string = os.getenv("CONNECTION_STRING")
    return BlobServiceClient.from_connection_string(connection_string)

def initialize_services():
    # Initialize OpenAI client
    openai_client = initialize_openai_client()

    # Initialize Azure OpenAI client
    azure_openai_client = initialize_azure_openai_client()

    # Initialize Blob Service Client
    blob_service_client = initialize_blob_service_client()

    return {
        "openai_client": openai_client,
        "azure_openai_client": azure_openai_client,
        "blob_service_client": blob_service_client
    }

async def create_openai_completion(prompt):
    services = initialize_services()
    azure_openai_client = services["azure_openai_client"]
    azure_openai_chat_completions_deployment_name = os.getenv("AZURE_OPENAI_CHAT_COMPLETIONS_DEPLOYMENT_NAME")

    response = azure_openai_client.chat.completions.create(
        model=azure_openai_chat_completions_deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        temperature=0.7,
        top_p=0.95,
    )
    return response