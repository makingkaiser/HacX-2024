
import asyncio  
import os
import json  
from uuid import uuid4  
import replicate  
import logging  
from extractors import extract_image_descriptions, extract_text_descriptions, replace_image_descriptions, replace_text_descriptions
from imgen import run_multiple_image_predictions, run_multiple_image_refinements
# from azureairag import run_multiple_text_refinements_rag
from RAG.text_rag.llama_index_text_search_engine import run_multiple_text_refinements

# Configure logging  
logging.basicConfig(level=logging.INFO)  
  
class GraphicElement:  
    def __init__(self, element_type, description, refined = None, content = None):  
        self.id = str(uuid4())  
        self.type = element_type
        self.description = description  
        self.content = content
        self.refined = refined
  


# async def flesh_out_html(input_html: str, target_audience: str, stylistic_description: str, content_description: str, format: str) -> str:
#     # Process the input HTML content
#     text_elements = extract_text_descriptions(input_html)
#     image_elements = extract_image_descriptions(input_html)
    
#     # Refine and generate image elements
#     refined_image_elements, all_titles = await run_multiple_image_refinements(
#         image_elements,
#         target_audience=target_audience,
#         stylistic_description=stylistic_description,
#         content_description=content_description,
#         format=format,
#         rag=True #hardcoded for now
#     )

#     generated_image_elements = await run_multiple_image_predictions(refined_image_elements)
#     refined_text_elements =  await run_multiple_text_refinements_rag(
#         text_elements,
#         target_audience=target_audience,
#         content_description=content_description,
#         format=format
#     )

#     # Replace image descriptions with generated image elements
#     output = replace_image_descriptions(input_html, generated_image_elements)
#     output = replace_text_descriptions(output,refined_text_elements)
#     with open("output1.html", "w") as f:
#         f.write(output)
#     return output

async def flesh_out_html_images(input_html: str, target_audience: str, stylistic_description: str, content_description: str, format: str) -> (str, list):
    # Extract image descriptions from the input HTML
    image_elements = extract_image_descriptions(input_html)
    
    # Refine and generate image elements
    refined_image_elements, all_titles = await run_multiple_image_refinements(
        image_elements,
        target_audience=target_audience,
        stylistic_description=stylistic_description,
        content_description=content_description,
        format=format,
        rag=True  # Hardcoded for now
    )


    generated_image_elements = await run_multiple_image_predictions(refined_image_elements)
    
    # Replace image descriptions with generated image elements in the HTML
    output_html = replace_image_descriptions(input_html, generated_image_elements)
    
    return output_html, all_titles


async def flesh_out_html_text(input_html: str, target_audience: str, content_description: str, format: str) -> str:
    # Extract text elements from the input HTML
    text_elements = extract_text_descriptions(input_html)
    
    # Refine text elements using RAG
    #run_multiple_text_refinements_rag for azureairag
    refined_text_elements = await run_multiple_text_refinements(
        text_elements,
        target_audience=target_audience,
        content_description=content_description,
        format=format
    )
    
    # Replace the original text descriptions with refined text elements in the HTML
    output_html = replace_text_descriptions(input_html, refined_text_elements)
    return output_html





    



#output: generated graphic 
#stored somewhere: html, list of images, list of text
# {'image_number': 1, 'image_description': "a picture of ...", "image_link": "https://..." }

#{'text_section_number': 1, 'text_description': "a picture of ...", "expanded_text" "a detailed picture of..." }

#provide user a list of all elements they would like to regenerate: either all or 