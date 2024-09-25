# HacX-2024
Submission for the 2024 HacX hackathon

# HacX 2024 - Streamlit App

This repository contains the `HacX-2024` application, a Streamlit-based web application that leverages various AI tools and libraries. The app is built to provide a seamless interface for interacting with machine learning models and cloud services.

## Getting Started

This guide will help you set up and run the `HacX-2024` application on your local machine.

### Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.7 or higher
- [pip](https://pip.pypa.io/en/stable/) (Python package manager)

You'll also need Azure and OpenAI API keys for this project to work, which can be set in environment variables using `.env` file (details in the installation section).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/makingkaiser/HacX-2024.git
   cd HacX-2024

2. **Set up environment variables:**
    Use the .env file provided and transfer them to the root directory and the RAG folder.
   
3. **Install the dependencies:** Install the required Python packages using pip:
   ```bash
   pip install -r requirements.txt

4. **Usage**
   Once you have installed the dependencies, you can run the application using Streamlit:
   ```bash
   streamlit run app.py

## Dependencies:
The project relies on several Python libraries. Below is a list of the core dependencies used in this application:

- Streamlit: A popular Python framework for building data science and machine learning web apps. (version 1.38.0)
- FastAPI: A modern, fast (high-performance) web framework for building APIs. (version 0.115.0)
- Llama Index: A tool for creating large language models, used for vector stores and embeddings. (version 0.11.11)
- OpenAI API: An API for accessing OpenAI models, including GPT. (version 1.47.0)
- Pydantic: Data validation and settings management using Python type annotations. (version 2.9.2)
-Azure Storage Blob: Azure SDK for interacting with blob storage.
- Replicate: A service for running machine learning models via API. (version 0.32.1)
- PymuPDF: A Python binding for the MuPDF PDF and document handling library. (version 1.24.10)
- Python-dotenv: For reading environment variables from .env files. (version 1.0.1)
- Azure Search Documents: SDK for Azure Cognitive Search.
- Additional Llama Index Integrations:
   llama-index-embeddings-azure-openai
   llama-index-embeddings-openai
   llama-index-vector-stores-postgres
   llama-index-vector-stores-azureaisearch
- Other Libraries:
   requests: For making HTTP requests.
   backoff: For retrying failed operations with exponential backoff.
   
