"""
SearchIndexClient to create, update, or delete indexes, SearchClient to load or query an index, 
Note that this use llama_index API instead of OpenAI's for Azure Client instantiation
"""
import asyncio
import os
import sys
import backoff
import requests
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.vector_stores.azureaisearch import (
    AzureAISearchVectorStore,
    IndexManagement,
    MetadataIndexFieldType,
)

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../utils'))

from initialize_client import create_openai_completion, initialize_azure_openai_client

#Configuration
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
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

    prompt = f"""Generate an adequate list of questions that can be used find relevant \
            details from knowledge base with drug preventative education material from \
            the Central Narcotics Bureau of Singapore that can be used to expand on this \
            placeholder description of a paragraph: \
            {content_description}. \
            Only return the questions, each on a new line please.
            return a maximum of 8 questions.
            """
    
    #regular openai api
    response = await create_openai_completion(prompt)
    
    content = response.choices[0].message.content
    questions = content.split('\n')
    # questions = response.choices[0].text.strip().split('\n')
    return questions

@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_tries=8)
async def question_load_and_query_search_index(questions):
    """
    Loads the search index and queries it using a list of questions.
    returns a dictionary where each question is mapped to the retrieved content.
    """
    completion_model_client = AzureOpenAI(
        model="gpt-4o",
        deployment_name=os.getenv("completions_model_name"),
        api_key=os.getenv("api_key_completions"),
        azure_endpoint=os.getenv("completions_endpoint"),
        api_version="2024-06-01" ,
    )

    embed_model_client =  AzureOpenAIEmbedding(
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

# async def main():
#     # Sample content description for generating questions
#     content_description = "This text discusses the effects of drug abuse on youth and the importance of early education to prevent drug addiction."
    
#     # Generate questions based on the content description
#     questions = await generate_questions(content_description)
    
#     # Print the generated questions
#     print("Generated Questions:")
#     for question in questions:
#         print(question)
    
#     # Load the search index and query it using the generated questions
#     question_answers = await question_load_and_query_search_index(questions)
    
#     # Print the responses for each question
#     print("\nQuestion and Answers from Search Index:")
#     for question, answer in question_answers.items():
#         print(f"Question: {question}\nAnswer: {answer}\n")

# # Run the main function using asyncio
# if __name__ == "__main__":
#     asyncio.run(main())

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



import asyncio
import re
from typing import List
from uuid import uuid4


class GraphicElement:
    def __init__(self, element_type, description, refined=None, content=None):
        self.id = str(uuid4())
        self.type = element_type
        self.description = description
        self.content = content
        self.refined = refined

def extract_text_descriptions(html_content: str) -> List[GraphicElement]:
    """
    Extracts text descriptions from HTML using a specified pattern and
    returns a list of GraphicElement instances.
    """
    pattern = re.compile(r'\[DESCRIPTION:\s*"(.*?)"\]')
    matches = pattern.findall(html_content)
    text_elements = [GraphicElement(element_type="text", description=desc) for desc in matches]
    return text_elements

async def refine_text_description(element: GraphicElement, target_audience: str, content_description: str, format: str) -> None:
    """
    Asynchronously refines the description of a text element by first querying a search index
    to gather context or related information, and then using this information to query an AI model,
    which updates the element's refined attribute with a more informed description.
    """
    # Query the search index based on the original description to get related information
    placeholder_description = element.description
    questions = await generate_questions(placeholder_description)
    related_info = await question_load_and_query_search_index(questions)
    

    # Use the results from the search index to enhance the prompt for the AI completion
    additional_context = related_info.get(element.description, "No relevant information found.")
    prompt = f"""
    Based on the original description of what the paragraph is meant to be,
    write out the paragraph to be engaging and suitable for {target_audience} in a {format} format:
    Original Description: {element.description}
    Related Information: {additional_context}
    Content Description: {content_description}

    Depending on the prompt original description, decide between paragraph or bullet points to
    convey this information. ONLY return the paragraph itself.  
    
    If you choose bullet points, return in html format as shown:
    <h2>The Social Impact of Cannabis Use</h2>
    <ul>
        <li><strong>Isolation:</strong> Regular cannabis use can sometimes lead to social withdrawal. Users might find themselves spending more time alone, distancing from friends and family.</li>
        <li><strong>Depression:</strong> There is a potential link between frequent cannabis use and increased feelings of depression. This can be due to various factors including changes in brain chemistry and the impact of isolation.</li>
        <li><strong>Social Stigma:</strong> Cannabis users may face judgment or stigma from their peers or society, which can further contribute to feelings of isolation and depression.</li>
        <li><strong>Impact on Relationships:</strong> Cannabis use can strain personal relationships, as changes in behavior and priorities may lead to conflicts or misunderstandings with loved ones.</li>
        <li><strong>Community Engagement:</strong> Conversely, some users might find a sense of community among fellow cannabis enthusiasts, which can mitigate some of the negative social effects.</li>
    </ul>
    """

    # Initialize the AI client and refine the description
    initialize_azure_openai_client()
    response = await create_openai_completion(prompt)
    element.refined = response.choices[0].message.content if response.choices else "No refinement available"

async def run_multiple_text_refinements(elements: List[GraphicElement], target_audience: str, content_description: str, format: str) -> List[GraphicElement]: 
    """
    Runs text refinements asynchronously for a list of GraphicElement instances.
    """
    tasks = [refine_text_description(element, target_audience, content_description, format) for element in elements if element.type == "text"]  
    await asyncio.gather(*tasks)
    return elements


# async def main():
#     # Sample HTML content with text descriptions
#     html_content = """
#     <div>
#         <p[DESCRIPTION: "Signs and symptoms of drug use that parents should be aware of, including behavioral, physical, and social indicators."]</p>
#         <p>[DESCRIPTION: "Strategies for creating a supportive home environment that discourages drug use, including establishing clear rules, promoting healthy activities, and strengthening family bonds."]</p>
#     </div>
#     """

#     # Extract text descriptions from the HTML content
#     text_elements = extract_text_descriptions(html_content)
#     print("Extracted Text Descriptions:")
#     for element in text_elements:
#         print(f"ID: {element.id}, Description: {element.description}")

#     # Define parameters for refining text descriptions
#     target_audience = "general audience"
#     content_description = "social effects of drug usage"
#     format = "article"

#     # Refine text descriptions
#     refined_elements = await run_multiple_text_refinements(
#         text_elements,
#         target_audience,
#         content_description,
#         format,
#     )

#     # Print refined text descriptions
#     print("\nRefined Text Descriptions:")
#     for element in refined_elements:
#         print(f"ID: {element.id}, Refined Description: {element.refined}")

# if __name__ == "__main__":
#     asyncio.run(main())

