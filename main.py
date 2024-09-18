
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
  

async def main():
    # call to llm > output.html
    with open("first_draft.html", "r") as file:
        file_content = file.read()  # Read the file content as a string (file content is first output of llm as of now, replace later with actual function)
        text_elements = extract_text_descriptions(file_content)
        image_elements = extract_image_descriptions(file_content)
        refined_image_elements = await run_multiple_image_refinements(
        image_elements,
        target_audience="general audience",
        stylistic_description="90's cartoon style",
        content_description="various scenes and landscapes",
        format="digital art"
    )
        generated_image_elements = await run_multiple_image_predictions(refined_image_elements)
        output = replace_image_descriptions(file_content, generated_image_elements)

    with open("output.html", "w") as f:
        f.write(output)




# Run the main function
asyncio.run(main())


    



#output: generated graphic 
#stored somewhere: html, list of images, list of text
# {'image_number': 1, 'image_description': "a picture of ...", "image_link": "https://..." }

#{'text_section_number': 1, 'text_description': "a picture of ...", "expanded_text" "a detailed picture of..." }

#provide user a list of all elements they would like to regenerate: either all or 