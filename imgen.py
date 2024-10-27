import asyncio
import os
import shutil
from tempfile import NamedTemporaryFile
from typing import List
from uuid import uuid4

import aiohttp
import replicate
import requests
import logging

from RAG.image_caption_rag.image_index_search_engine import image_caption_rag_refinement
from utils.initialize_client import create_openai_completion
from visualfidelity import checkvisualfidelity
from textfidelity import check_text_fidelity

os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

# async def get_base64_image_url(image_url):
#         try:
#             response = requests.get(image_url)
#             response.raise_for_status()  # Ensure the request was successful
#             return "data:image/webp;base64," + base64.b64encode(response.content).decode('utf-8')
#         except requests.RequestException as e:
#             print(f"Error downloading or encoding image: {e}")
#             return None
class GraphicElement:
    def __init__(self, element_type, description, refined=None, content=None):
        self.id = str(uuid4())
        self.type = element_type
        self.description = description
        self.content = content
        self.refined = refined

    async def assess_visual_fidelity(self, image_url, intended_text=None):
        """Asynchronously downloads image, checks visual and text fidelity."""
        visual_result, text_result = False, False
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status != 200:
                    logging.error(f"Failed to download image: {response.status}")
                    response.raise_for_status()

                with NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        tmp_file.write(chunk)
                    tmp_file_path = tmp_file.name

                logging.info(f"Image downloaded and saved to {tmp_file_path}")

        try:
            visual_result = checkvisualfidelity(tmp_file_path, 'B')
            logging.info(f"Visual fidelity check completed with result: {visual_result}")
            text_result = check_text_fidelity(tmp_file_path, intended_text)
            logging.info(f"Text fidelity check completed with result: {text_result}")
        except Exception as e:
            logging.error(f"Error during fidelity checks: {e}")
        finally:
            os.remove(tmp_file_path)
            logging.info(f"Temporary file {tmp_file_path} removed")

        return visual_result, text_result


# Asynchronous function to run a prediction and potentially regenerate based on visual fidelity
async def run_image_prediction(element: GraphicElement) -> None:
    description = element.refined if element.refined else element.description
    input_data = {"prompt": description}
    prediction = replicate.predictions.create(
        model="black-forest-labs/flux-schnell",
        input=input_data
    )

    while prediction.status not in ["succeeded", "failed", "canceled"]:
        await asyncio.sleep(2)
        prediction = replicate.predictions.get(prediction.id)

    if prediction.status == "succeeded":
        element.content = prediction.output
        if isinstance(element.content, list):  # Handle lists
            for image_url in element.content:
                is_well_formed_visual, is_well_formed_text = await element.assess_visual_fidelity(image_url)
                if not (is_well_formed_visual and is_well_formed_text):
                    print(f"Fidelity failure for {image_url}, regenerating...")
                    await run_image_prediction(element)
                    break
        else:
            is_well_formed_visual, is_well_formed_text = await element.assess_visual_fidelity(element.content)
            if not (is_well_formed_visual and is_well_formed_text):
                print("Fidelity failure, regenerating...")
                await run_image_prediction(element)
    else:
        print(f"Prediction failed with status: {prediction.status}")
        element.content = "Error generating image"

async def run_multiple_image_predictions(elements: List[GraphicElement]):  
    #Function to run multiple predictions asynchronously  
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
        
        Return ONLY the expanded description and nothing else. 
        Make sure the generated image does not have any text or textual elements unless explicity specified. 
        If it is specified, restrict to only one textual element.
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

