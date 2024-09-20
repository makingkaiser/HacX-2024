"""
SearchIndexClient to create, update, or delete indexes, SearchClient to load or query an index, 
Note that this use llama_index API instead of OpenAI's for Azure Client instantiation
"""
import asyncio
import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore, IndexManagement, MetadataIndexFieldType

from utils.initialize_client import initialize_azure_openai_client, create_openai_completion

#Configuration
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)
azure_search_service_admin_key = os.getenv('azure_search_service_admin_key')
azure_search_service_endpoint = os.getenv('azure_search_service_endpoint')
credential = AzureKeyCredential(azure_search_service_admin_key)

def text_create_search_index(nodes):
    """
    For text-rag, creates or adds to a search index using nodes generated 
    from llamaindex's semantic chunker
    """

    completion_model_client = AzureOpenAI(
        model="gpt-4o",
        deployment_name=os.getenv("completions_model_name"),
        api_key=os.getenv("api_key_completions"),
        azure_endpoint=os.getenv("completions_endpoint"),
        api_version="2024-06-01" ,
    )
    embed_model_client = AzureOpenAIEmbedding(
        model="text-embedding-ada-002",
        deployment_name=os.getenv("embeddings_model_name"),
        api_key=os.getenv("api_key_embeddings"),
        azure_endpoint=os.getenv("embeddings_endpoint"),
        api_version="2024-06-01" ,
    )

    # creating an index
    index_client  = SearchIndexClient(
        endpoint=azure_search_service_endpoint,
        index_name="text-rag-search-index", 
        credential=credential,
    )

    metadata_fields = {
        "author": "author",
        "theme": ("topic", MetadataIndexFieldType.STRING),
        "director": "director",
    }

    vector_store = AzureAISearchVectorStore(
        search_or_index_client=index_client,
        filterable_metadata_field_keys=metadata_fields,
        index_name= "text-rag-search-index",
        index_management=IndexManagement.CREATE_IF_NOT_EXISTS,
        id_field_key="id",
        chunk_field_key="chunk",
        embedding_field_key="embedding",
        embedding_dimensionality=1536,
        metadata_string_field_key="metadata",
        doc_id_field_key="doc_id",
        language_analyzer="en.lucene",
        vector_algorithm_type="exhaustiveKnn",
        # compression_type="binary" # Option to use "scalar" or "binary": compression is only supported for HNSW
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    Settings.llm = completion_model_client
    Settings.embed_model = embed_model_client

    index = VectorStoreIndex(nodes,storage_context=storage_context)

async def generate_questions(content_description):
    """
    Generates a list of questions specifically tailored to drug 
    preventative education material based on a placeholder 
    description of content.
    """

    prompt = f"Generate an adequate list of questions that can be used find relevant \
            details from knowledge base with drug preventative education material from \
            the Central Narcotics Bureau of Singapore that can be used to expand on this \
            placeholder description of a paragraph: \
            {content_description}. \
            Only return the questions, each on a new line please."
    
    #regular openai api
    client = await create_openai_completion()

    response = await client.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    
    content = response.choices[0].message.content
    questions = content.split('\n')
    # questions = response.choices[0].text.strip().split('\n')
    return questions

async def question_load_and_query_search_index(questions):
    """
    Loads the search index and queries it using a list of questions.
    returns a dictionary where each question is mapped to the retrieved content.
    """
    completion_model_client = await AzureOpenAI.async_create(
        model="gpt-4o",
        deployment_name=os.getenv("completions_model_name"),
        api_key=os.getenv("api_key_completions"),
        azure_endpoint=os.getenv("completions_endpoint"),
        api_version="2024-06-01" ,
    )

    embed_model_client = await AzureOpenAIEmbedding.async_create(
        model="text-embedding-ada-002",
        deployment_name=os.getenv("embeddings_model_name"),
        api_key=os.getenv("api_key_embeddings"),
        azure_endpoint=os.getenv("embeddings_endpoint"),
        api_version="2024-06-01",
    )

    index_client = SearchIndexClient(
        endpoint=azure_search_service_endpoint,
        index_name="text-rag-search-index", 
        credential=credential,
    )

    metadata_fields = {
        "author": "author",
        "theme": ("topic", MetadataIndexFieldType.STRING),
        "director": "director",
    }

    vector_store = AzureAISearchVectorStore(
        search_or_index_client=index_client,
        filterable_metadata_field_keys=metadata_fields,
        index_name = "text-rag-search-index",
        index_management=IndexManagement.CREATE_IF_NOT_EXISTS,
        id_field_key="id",
        chunk_field_key="chunk",
        embedding_field_key="embedding",
        embedding_dimensionality=1536,
        metadata_string_field_key="metadata",
        doc_id_field_key="doc_id",
        language_analyzer="en.lucene",
        vector_algorithm_type="exhaustiveKnn",
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    Settings.llm = completion_model_client
    Settings.embed_model = embed_model_client

    index = VectorStoreIndex.from_documents(
        [],
        storage_context=storage_context,
    )
    
    query_engine = index.as_query_engine(
        response_mode = "refine",
        verbose = False,
    )
    output = {}

    #limit to 5 questions
    questions = questions[:5]

    # for question in questions:
    #     res = query_engine.query(question)
    #     output[question] = res.response

    responses = await asyncio.gather(*(asyncio.to_thread(query_engine.query, question) for question in questions))

    for question, res in zip(questions, responses):
        output[question] = res.response

    return output

##Example Execution
# questions = generate_questions("this paragraph is about the social effects of drug usage for cannabis and cocaine")
# print(questions)
# output = question_load_and_query_search_index(questions)
# print(output)

##Example Output 
"""
data = {
    'What are the social consequences of cannabis usage?': 'The social consequences of cannabis usage include a significant link between early cannabis exposure and an increased risk of using other illicit drugs, as documented by various clinical and epidemiological studies. Additionally, cannabis use, especially when initiated at a younger age, is associated with adverse life outcomes such as lower educational attainment, higher unemployment rates, increased welfare dependence, and lower levels of life satisfaction. Furthermore, jurisdictions that have legalized cannabis, such as Colorado, have observed an increase in traffic accidents and fatalities involving drivers who tested positive for cannabis, a negative impact on the workforce due to local candidates failing drug tests, higher absenteeism among cannabis users, and an increase in crime rates, particularly those linked to drugs.',
    
    'How does cannabis use affect family relationships?': 'The provided information does not specifically address how cannabis use affects family relationships.',
    
    'In what ways does cocaine use impact social behavior?': 'Cocaine use can significantly impact social behavior by weakening family structures, disrupting normal family life, and potentially leading to family disintegration. Additionally, it inflicts harm on public health and safety, with societal costs that affect the broader community.',
    
    "How does drug dependency on cocaine affect one's social life?": "Drug dependency on cocaine can severely affect one's social life by weakening family structures, disrupting normal family life, and potentially leading to family disintegration. It also inflicts harm on public health and safety, with costs borne by society.",
    
    'What are the community-level effects of widespread cannabis consumption?': 'The community-level effects of widespread cannabis consumption include an increase in traffic accidents, as evidenced by the rise in traffic deaths involving drivers who tested positive for cannabis in Colorado. Additionally, there are negative impacts on the workforce, with large businesses in Colorado reporting difficulties in hiring local candidates due to failed pre-employment drug tests. Cannabis users were also more likely to miss work compared to alcohol users and the overall population. Furthermore, contrary to the argument that legalization could reduce crime, there is evidence that crime rates, particularly those linked to drugs, actually increased after cannabis was legalized in Colorado.'
}
""" 