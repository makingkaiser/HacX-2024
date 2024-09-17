import re  
import json  
from typing import * 
from uuid import uuid4  

class GraphicElement:  
    def __init__(self, element_type, description, dim = None, content = None):  
        self.id = str(uuid4())  
        self.type = element_type
        self.description = description  
        self.content = content
        self.dim = dim
  

def extract_image_descriptions(html_content) -> List[GraphicElement]:
    
    # Define a pattern to match the image placeholders  
    pattern = re.compile(r'<div class="image-placeholder">[\s\S]*?\[Image: (\d+x\d+) - (.*?)\]\s*</div>')  
      
    # Find all matches in the HTML content  
    matches = pattern.findall(html_content)  
      
    # Create a dictionary to store the results  
     # Create a list to store the results  
    image_elements = []  
      
    for dimensions, description in matches:  
        image_element = GraphicElement(  
            element_type="image",  
            description=description,  
            dim=dimensions  
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


html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drug Awareness for Teens - Central Narcotics Bureau</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f4f8;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-gap: 20px;
        }
        .header {
            grid-column: 1 / -1;
            background-color: #2c3e50;
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
        }
        .content-box {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .span-2 {
            grid-column: span 2;
        }
        .span-3 {
            grid-column: span 3;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        .image-placeholder {
            background-color: #e0e0e0;
            height: 200px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 15px;
            border-radius: 5px;
            font-style: italic;
            text-align: center;
            padding: 10px;
        }
        .footer {
            grid-column: 1 / -1;
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 10px;
            display: flex;
            justify-content: space-around;
            align-items: center;
        }
        .qr-placeholder {
            width: 100px;
            height: 100px;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Stay Drug-Free: Essential Information for Teens</h1>
        </header>

        <div class="content-box span-2">
            <div class="image-placeholder">
                [Image: 600x400 - A group of diverse teenagers in a school setting, engaged in a discussion about drug prevention. The image should depict attentive and engaged students, with a teacher or counselor providing information.]
            </div>
        </div>

        <div class="content-box span-2">
            [DESCRIPTION: "Tips on how to resist peer pressure and make positive choices, including practical strategies and real-life scenarios."]
        </div>

        <div class="content-box span-3">
            [DESCRIPTION: "Overview of common drugs abused by teens, including their effects and potential long-term consequences."]
        </div>

        <div class="content-box">
            <div class="image-placeholder">
                [Image: 300x300 - An infographic-style illustration showing the detrimental effects of drugs on the body. Use simplified, icon-based visuals to represent different organs and systems affected by drug use.]
            </div>
        </div>

        <div class="content-box span-2">
            [DESCRIPTION: "Contact information for local support groups and resources."]
        </div>

        <div class="content-box span-2">
            <div class="image-placeholder">
                [Image: 600x300 - An image showing a group of teens engaging in a fun, drug-free activity like playing sports, volunteering, or participating in a hobby club.]
            </div>
        </div>

        <div class="content-box full-width">
            [DESCRIPTION: "Signs of drug use that teens should be aware of in their peers, including behavioral, physical, and social indicators."]
        </div>

        <div class="content-box span-2">
            <div class="image-placeholder">
                [Image: 600x400 - A supportive scene showing a counselor or support group helping young adults. The image should convey a sense of hope and community, with warm, welcoming colors and expressions.]
            </div>
        </div>

        <div class="content-box span-2">
            [DESCRIPTION: "Resources and support available for teens struggling with drug issues, including hotlines, counseling, and community programs."]
        </div>

        <div class="content-box span-3">
            [DESCRIPTION: "An inspiring quote about drug prevention."]
        </div>

        <div class="content-box">
            <div class="image-placeholder">
                [Image: 300x300 - A conceptual illustration representing Singapore's strong stance against drugs. Use symbolic elements like a shield, a family silhouette, and iconic Singapore landmarks to convey protection and national unity in drug prevention.]
            </div>
        </div>

        <footer class="footer">
            <div>
                <h3>24/7 Youth Support Hotline</h3>
                <p>1800-TEEN-CNB</p>
            </div>
            <div class="qr-placeholder">
                [QR Code]
            </div>
        </footer>
    </div>
</body>
</html>
"""

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
                return element.content
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
        dimensions, original_description = match.groups()  
        for element in image_elements:  
            if element.description == original_description and element.dim == dimensions:  
                width, height = dimensions.split("x")  
                #return f'<img src="{element.content}" alt="{original_description}" width="{width}" height="{height}">'
                return f'<img src="{element.content[0].strip("'")}" alt="{original_description}">'   
        return match.group(0)  # Return the original if no match is found  
  
    # Replace all occurrences in the HTML content  
    modified_html = pattern.sub(replacer, html_content)  
      
    return modified_html  
    

# Example usage:  
  
# List of GraphicElement instances with content links  
image_elements = [  
    GraphicElement(  
        element_type="image",  
        description="A group of diverse teenagers in a school setting, engaged in a discussion about drug prevention. The image should depict attentive and engaged students, with a teacher or counselor providing information.",  
        dim="600x400",  
        content="https://example.com/image1.jpg"  
    ),  
    GraphicElement(  
        element_type="image",  
        description="An infographic-style illustration showing the detrimental effects of drugs on the body. Use simplified, icon-based visuals to represent different organs and systems affected by drug use.",  
        dim="300x300",  
        content="https://example.com/image2.jpg"  
    ),  
    GraphicElement(  
        element_type="image",  
        description="An image showing a group of teens engaging in a fun, drug-free activity like playing sports, volunteering, or participating in a hobby club.",  
        dim="600x300",  
        content="https://example.com/image3.jpg"  
    ),  
    GraphicElement(  
        element_type="image",  
        description="A supportive scene showing a counselor or support group helping young adults. The image should convey a sense of hope and community, with warm, welcoming colors and expressions.",  
        dim="600x400",  
        content="https://example.com/image4.jpg"  
    ),  
    GraphicElement(  
        element_type="image",  
        description="A conceptual illustration representing Singapore's strong stance against drugs. Use symbolic elements like a shield, a family silhouette, and iconic Singapore landmarks to convey protection and national unity in drug prevention.",  
        dim="300x300",  
        content="https://example.com/image5.jpg"  
    )  
]  
  
# Replace the original image descriptions with the content links  
# modified_html = replace_image_descriptions(html_content, image_elements)  
  
# print(modified_html) 