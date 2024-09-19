
import asyncio  
import os
import json  
from uuid import uuid4  
import replicate  
import logging  
from extractors import extract_image_descriptions, extract_text_descriptions, replace_image_descriptions, replace_text_descriptions
from imgen import run_multiple_image_predictions, run_image_prediction, run_multiple_image_refinements

# Configure logging  
logging.basicConfig(level=logging.INFO)  
  
class GraphicElement:  
    def __init__(self, element_type, description, refined = None, content = None):  
        self.id = str(uuid4())  
        self.type = element_type
        self.description = description  
        self.content = content
        self.refined = refined
  


async def flesh_out_html(input_html: str, target_audience: str, stylistic_description: str, content_description: str, format: str) -> str:
    # Process the input HTML content
    text_elements = extract_text_descriptions(input_html)
    image_elements = extract_image_descriptions(input_html)
    
    # Refine and generate image elements
    refined_image_elements = await run_multiple_image_refinements(
        image_elements,
        target_audience=target_audience,
        stylistic_description=stylistic_description,
        content_description=content_description,
        format=format
    )
    generated_image_elements = await run_multiple_image_predictions(refined_image_elements)
    
    # Replace image descriptions with generated image elements
    output = replace_image_descriptions(input_html, generated_image_elements)
    
    return output





    



#output: generated graphic 
#stored somewhere: html, list of images, list of text
# {'image_number': 1, 'image_description': "a picture of ...", "image_link": "https://..." }

#{'text_section_number': 1, 'text_description': "a picture of ...", "expanded_text" "a detailed picture of..." }

#provide user a list of all elements they would like to regenerate: either all or 