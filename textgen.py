import asyncio
import re
from uuid import uuid4
from typing import List

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
    Refine this description to be more engaging and suitable for {target_audience} in a {format} format:
    Original Description: {element.description}
    Related Information: {additional_context}
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


async def main():
    # Sample HTML content with text descriptions
    html_content = """
    <div>
        <p>[DESCRIPTION: "The social effects of drug usage for cannabis include isolation and depression."]</p>
        <p>[DESCRIPTION: "The social effects of drug usage for cocaine include aggression and paranoia."]</p>
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
    refined_elements = await run_multiple_text_refinements(
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

