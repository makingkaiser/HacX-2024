import asyncio
import re
from uuid import uuid4
from typing import List

from RAG.text_rag.llama_index_text_search_engine import question_load_and_query_search_index, generate_questions

from utils.initialize_client import initialize_azure_openai_client, create_openai_completion

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

async def refine_text_description(element: GraphicElement, target_audience: str, stylistic_description: str, content_description: str, format: str) -> None:
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
    Refine this description to be more engaging and suitable for {target_audience} in a {format} format:
    Original Description: {element.description}
    Related Information: {additional_context}
    """

    # Initialize the AI client and refine the description
    client = await create_openai_completion()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    element.refined = response.choices[0].message.content if response.choices else "No refinement available"

async def run_multiple_text_refinements(elements: List[GraphicElement], target_audience: str, stylistic_description: str, content_description: str, format: str) -> List[GraphicElement]: 
    """
    Runs text refinements asynchronously for a list of GraphicElement instances.
    """
    tasks = [refine_text_description(element, target_audience, stylistic_description, content_description, format) for element in elements if element.type == "text"]  
    await asyncio.gather(*tasks)
    return elements
