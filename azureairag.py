import os
from openai import AzureOpenAI
from uuid import uuid4
import asyncio
import re
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = "gpt-4-turbo"
search_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT_AZUREAIRAG")
search_key = os.getenv("AZURE_SEARCH_SERVICE_ADMIN_KEY_AZUREAIRAG")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
embeddings_endpoint = os.getenv("embeddings_endpoint")
embeddings_model_name = "text-embedding-ada-002"

# Initialize Azure OpenAI client with key-based authentication


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

async def refine_text_description_with_rag(element: GraphicElement, target_audience: str, content_description: str, format: str) -> None:
    client = AzureOpenAI(
        azure_endpoint = endpoint,
        api_key = subscription_key,
        api_version = "2024-05-01-preview",
    )
    prompt = f"""
    Your Task is to expand on a section to create a short section of text to fit on one section of a flyer/infographic, targeted at a Singaporean audience. Make use of retrieved documents, if not use your own knowledge. Include specific examples when possible.
    Refine this description to be more engaging and suitable for {target_audience} in a {format} format. use bullet points.
    Original Description: {element.description}
    Content Description: {content_description}
    

    ONLY return the short section of text with no supporting text. it will be directly used in one section of a flyer/infographic.
    EXAMPLE:
    <ul>
        <li><strong>Legal Repercussions</strong>: Under the Misuse of Drugs Act (MDA) 1973, offenses range from possession and consumption of drugs to trafficking, with penalties including fines, imprisonment, and in severe cases, the mandatory death penalty.</li>
        
        <li><strong>Societal Impact</strong>: Drug abuse affects not only the individual but also families and the broader community. It can lead to loss of livelihoods, breakdown of relationships, and a significant burden on social and healthcare systems.</li>
        
        <li><strong>Youth and Prevention</strong>: Singapore's proximity to major drug-producing regions poses a continuous threat. The rising trend in cannabis use among the youth is concerning, with many perceiving it as less harmful than it truly is. This underscores the need for effective drug prevention education.</li>
        
        <li><strong>Community Engagement</strong>: Tools such as handbooks, FAQs, and presentation slides empower communities to spread awareness and uphold Singapore's drug-free stance. Active engagement from all community members is crucial to safeguard against the harms of drugs.</li>
    </ul>
    """

    completion = client.chat.completions.create(
        model=deployment,
        messages= [
        {
            "role": "user",
            "content": prompt
        }
    ],
        
        max_tokens=4096,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    ,
        extra_body={
        "data_sources": [{
            "type": "azure_search",
            "parameters": {
                "filter": None,
                "endpoint": f"{search_endpoint}",
                "index_name": "dynamic-carrot-b392d48b6d",
                "semantic_configuration": "azureml-default",
                "authentication": {
                "type": "api_key",
                "key": f"{search_key}"
                },
                "embedding_dependency": {
                "type": "endpoint",
                "endpoint": f"{embeddings_endpoint}/openai/deployments/{embeddings_model_name}/embeddings?api-version=2023-07-01-preview",
                "authentication": {
                    "type": "api_key",
                    "key": f"{subscription_key}"
                }
                },
                "query_type": "vector_simple_hybrid",
                "in_scope": True,
                "role_information": "",
                "strictness": 3,
                "top_n_documents": 5
            }
            }]
        })
    element.refined = completion.choices[0].message.content


async def run_multiple_text_refinements_rag(elements: List[GraphicElement], target_audience: str, content_description: str, format: str) -> List[GraphicElement]: 
    """
    Runs text refinements asynchronously for a list of GraphicElement instances.
    """
    tasks = [refine_text_description_with_rag(element, target_audience, content_description, format) for element in elements if element.type == "text"]  
    await asyncio.gather(*tasks)
    print("Refined Text Descriptions:")
    for num, element in enumerate(elements):
        print(num, element.refined)
    return elements



async def main():
    # Sample HTML content with text descriptions
    html_content = """
    <div>
        <p[DESCRIPTION: "Information on Singapore's drug laws and policies, emphasizing the legal consequences of drug offenses and the importance of prevention."]</p>
        <p>[DESCRIPTION: "Guidance on how to talk to children about drugs, including age-appropriate conversation starters and tips for maintaining open communication."]</p>
    </div>
    """

    # Extract text descriptions from the HTML content
    text_elements = extract_text_descriptions(html_content)
    print("Extracted Text Descriptions:")
    for element in text_elements:
        print(f"ID: {element.id}, Description: {element.description}")

    # Define parameters for refining text descriptions
    target_audience = "general audience"
    content_description = "social effects of drug usage"
    format = "article"

    # Refine text descriptions
    refined_elements = await run_multiple_text_refinements_rag(
        text_elements,
        target_audience,
        content_description,
        format,
    )

    # Print refined text descriptions
    print("\nRefined Text Descriptions:")
    for element in refined_elements:
        print(f"ID: {element.id}, Refined Description: {element.refined}")

if __name__ == "__main__":
    asyncio.run(main())