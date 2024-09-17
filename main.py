
import asyncio  
import os
import json  
from uuid import uuid4  
import replicate  
import logging  
from extractors import extract_image_descriptions, extract_text_descriptions, replace_image_descriptions, replace_text_descriptions
from imgen import run_multiple_predictions, run_prediction

# Configure logging  
logging.basicConfig(level=logging.INFO)  
  
class GraphicElement:  
    def __init__(self, element_type, description, dim = None, content = None):  
        self.id = str(uuid4())  
        self.type = element_type
        self.description = description  
        self.content = content
        self.dim = dim
  

async def main():
    # call to llm > output.html
    with open("workinghtmltemplateforbrowser.html", "r") as file:
        file_content = file.read()  # Read the file content as a string
        text_elements = extract_text_descriptions(file_content)
        image_elements = extract_image_descriptions(file_content)
        generated_image_elements = await run_multiple_predictions(image_elements)
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