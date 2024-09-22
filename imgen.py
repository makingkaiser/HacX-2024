import asyncio  
import os
import replicate  

from typing import List 
from uuid import uuid4  

from RAG.image_caption_rag.image_index_search_engine import image_caption_rag_refinement
from utils.initialize_client import create_openai_completion
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

class GraphicElement:  
    def __init__(self, element_type, description, refined = None, content = None):  
        self.id = str(uuid4())  
        self.type = element_type
        self.description = description  
        self.content = content
        self.refined = refined

# Asynchronous function to run a prediction from one single prompt and track progress  
async def run_image_prediction(element: GraphicElement) -> None:
    description = element.refined if element.refined else element.description
    input_data = {  
        "prompt": description  
    }  
    prediction = replicate.predictions.create(  
        model="black-forest-labs/flux-schnell",  
        input=input_data  
    )  
      
    # Check progress asynchronously  
    while prediction.status not in ["succeeded", "failed", "canceled"]:  
        await asyncio.sleep(2)  # Pause for 2 seconds before checking again  
        prediction = replicate.predictions.get(prediction.id)  
        log_output = prediction.logs  
        if log_output:  
            current_iteration = log_output.count("it [")  
            total_iterations = 28  # Fixed number of iterations  
            progress_percentage = (current_iteration / total_iterations) * 100  
            print(f"Prompt: {description[:60]}... Progress: {progress_percentage:.2f}%")  
        else:  
            print(f"Prompt: {description[:60]}... Progress: Not available yet.")  
      
    # Handle result  
    if prediction.status == "succeeded":  
        print(f"Prompt: {description[:60]}... Prediction completed successfully!")  
        element.content = prediction.output  
    else:  
        print(f"Prompt: {description[:60]}... Prediction failed with status: {prediction.status}")  
        element.content = "Error generating image"  
  

async def run_multiple_image_predictions(elements: List[GraphicElement]):  
    #Function to run multiple predictions asynchronously  
    tasks = [run_image_prediction(element) for element in elements if element.type == "image"]  
    await asyncio.gather(*tasks)  
    return elements  

async def refine_image_description(element: GraphicElement, target_audience: str, stylistic_description: str, content_description: str, format: str, rag: bool) -> list:
    if rag:
        user_input = {
            'user_stylistic_description': stylistic_description,
            'target_audience': target_audience,
            'content_description': content_description,
        }
        result = await image_caption_rag_refinement(user_input, element.description, format)
        element.refined = result['expanded_description']
        return [res['title'] for res in result['reference_images']]
    else:
        prompt = f"""Expand upon the following description of an image to about a paragraph length:
        Description: {element.description}
        based on the context that this image is designed to be part of a {format} has the following properties:
        - Target Audience: {target_audience}
        - Stylistic Description: {stylistic_description}
        - Content Description: {content_description}
        
        Return ONLY the expanded description and nothing else. DO NOT include any description of text or textual elements in your expanded description, unless explicity specified. If it is specified, restrict to only one textual element.
        """
        response = await create_openai_completion(prompt)
        element.refined = response.choices[0].message.content
        return []

async def run_multiple_image_refinements(elements: List[GraphicElement], target_audience: str, stylistic_description: str, content_description: str, format: str, rag: bool) -> (List[GraphicElement], set):  
    print("Generating image descriptions...")
    all_titles = set()
    tasks = [refine_image_description(element, target_audience, stylistic_description, content_description, format, rag) for element in elements if element.type == "image"]
    titles_lists = await asyncio.gather(*tasks)
    
    # Flatten list of lists of titles into a single set to remove duplicates
    for titles in titles_lists:
        all_titles.update(titles)
    
    return elements, all_titles


# Example usage
async def main():
    # Example list of GraphicElement instances
    elements = [
        GraphicElement(
            element_type="image",
            description="A serene landscape with mountains in the background and a clear blue sky."
        ),
        GraphicElement(
            element_type="image",
            description="A futuristic city skyline with tall skyscrapers and flying cars."
        ),
        GraphicElement(
            element_type="text",
            description="Event details"
        )
    ]

    # Run the refinements asynchronously
    refined_elements = await run_multiple_image_refinements(
        elements,
        target_audience="general audience",
        stylistic_description="realistic and detailed",
        content_description="various scenes and landscapes",
        format="digital art",
        rag=False
    )

    # Print refined GraphicElements
    for element in refined_elements:
        print(f"ID: {element.id}, Type: {element.type}, Description: {element.refined}, Content: {element.content}")

if __name__ == "__main__":
    asyncio.run(main())

