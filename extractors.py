import re  
import json  
from typing import * 
from uuid import uuid4  

class GraphicElement:  
    def __init__(self, element_type, description, refined = None, content = None):  
        self.id = str(uuid4())  
        self.type = element_type
        self.description = description  
        self.content = content
        self.refined = refined
  

def extract_image_descriptions(html_content) -> List[GraphicElement]:
    """Extracts image descriptions. The expected format is [Image: dimensions - description]."""
    
    # Define a pattern to match the image placeholders  
    pattern = re.compile(r'<div class="image-placeholder">[\s\S]*?\[Image: (\d+x\d+) - (.*?)\]\s*</div>')  
      
    # Find all matches in the HTML content  
    matches = pattern.findall(html_content)  
      
    # Create a dictionary to store the results  
     # Create a list to store the results  
    image_elements = []  
      
    for _, description in matches:  
        image_element = GraphicElement(  
            element_type="image",  
            description=description,  
        )  
        image_elements.append(image_element)  
      
    return image_elements  

def extract_text_descriptions(html_content) -> List[GraphicElement]:  
    """  
    Extracts text descriptions from HTML and returns a list of GraphicElement instances.  
      
    Args:  
        html_content (str): The HTML content as a string.  
      
    Returns:  
        List[GraphicElement]: A list of GraphicElement instances representing text descriptions.  
    """  
    # Define a pattern to match the text placeholders  
    pattern = re.compile(r'\[DESCRIPTION:\s*"(.*?)"\]') 
      
    # Find all matches in the HTML content  
    matches = pattern.findall(html_content)  
      
    # Create a list to store the results  
    text_elements = []  
      
    for description in matches:  
        text_element = GraphicElement(  
            element_type="text",  
            description=description  
        )  
        text_elements.append(text_element)  
      
    return text_elements

def replace_text_descriptions(html_content: str, text_elements: List[GraphicElement]) -> str:  
    """  
    Replaces original text descriptions in HTML with the expanded text descriptions.  
  
    Args:  
        html_content (str): The original HTML content.  
        text_elements (List[GraphicElement]): A list of GraphicElement instances with expanded descriptions.  
  
    Returns:  
        str: The modified HTML content with replaced text descriptions.  
    """  
    # Define a pattern to match the original text descriptions  
    pattern = re.compile(r'\[DESCRIPTION:\s*"(.*?)"\]')  
  
    # Function to replace each match with the corresponding expanded description  
    def replacer(match):  
        original_description = match.group(1)  
        for element in text_elements:  
            if element.description == original_description:  
                return element.refined
        return match.group(0)  # Return the original if no match is found  
  
    # Replace all occurrences in the HTML content  
    modified_html = pattern.sub(replacer, html_content)  
      
    return modified_html

def replace_image_descriptions(html_content: str, image_elements: List[GraphicElement]) -> str:  
    """  
    Replaces original image descriptions in HTML with the links specified in element.content.  
  
    Args:  
        html_content (str): The original HTML content.  
        image_elements (List[GraphicElement]): A list of GraphicElement instances with content links.  
  
    Returns:  
        str: The modified HTML content with replaced image descriptions.  
    """  
    # Define a pattern to match the original image descriptions  
    pattern = re.compile(r'<div class="image-placeholder">[\s\S]*?\[Image: (\d+x\d+) - (.*?)\]\s*</div>')  
  
    # Function to replace each match with the corresponding content link  
    def replacer(match):  
        _, original_description = match.groups()  
        for element in image_elements:  
            if element.description == original_description:   
                
                return f'<img src="{element.content[0].strip()}" alt="{original_description}">'   
        return match.group(0)  # Return the original if no match is found  
  
    # Replace all occurrences in the HTML content  
    modified_html = pattern.sub(replacer, html_content)  
      
    return modified_html  
    
