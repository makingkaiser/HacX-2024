# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Standard library imports
import os
import re
import json
import uuid
# Third-party imports
import dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchIndex,
    SearchField,
    ScoringProfile,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticSearch,
    SemanticField
)
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient

# Retrieve environment variables
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_chat_completions_deployment_name = os.getenv("AZURE_OPENAI_CHAT_COMPLETIONS_DEPLOYMENT_NAME")
azure_openai_embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
embedding_vector_dimensions = int(os.getenv("EMBEDDING_VECTOR_DIMENSIONS"))
azure_search_service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
azure_search_service_admin_key = os.getenv("AZURE_SEARCH_SERVICE_ADMIN_KEY")
search_index_name = os.getenv("SEARCH_INDEX_NAME")

connection_string = os.getenv("CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


openai_client = AzureOpenAI(
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_api_key,
    api_version="2024-06-01"
    )

#User Query Simulation

# response = openai_client.chat.completions.create(
#     model=azure_openai_chat_completions_deployment_name,
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant for retrieving image captions from a database."},
#         {"role": "user", "content": "What are the relevant drug preventative educational material  we have in our knowledge base that are suitable for kids?"}
#     ],
#     extra_body={
#         "data_sources": [
#             {
#                 "type": "azure_search",
#                 "parameters": {
#                     "endpoint": azure_search_service_endpoint,
#                     "index_name": search_index_name,
#                     "authentication": {
#                         "type": "api_key",
#                         "key": azure_search_service_admin_key,
#                     }
#                 }
#             }
#         ]
#     }
# )

def extract_html_content(text):
    # Compile the regular expression pattern
    pattern = re.compile(r'<!DOCTYPE html>(.*?)</html>', re.DOTALL | re.IGNORECASE)
    
    # Search for the pattern in the text
    match = pattern.search(text)
    
    # If a match is found, return the matched content
    if match:
        return match.group(1)
    else:
        return None

# # Example usage
# html_string = """
# Some text before
# <!DOCTYPE html>
# <html>
# <head><title>Test</title></head>
# <body><p>Hello, World!</p></body>
# </html>
# Some text after
# """

# extracted_content = extract_html_content(html_string)
# print(extracted_content)
############ Example flow  ############

#Base query to gpt4-o 


TARGET_AUDIENCE = "general audience" 
STYLISTIC_DESCRIPTION = "90's cartoon style"
CONTENT_DESCRIPTION = "various scenes and landscapes"
FORMAT = "digital art"
 

user_response_wrapper_prompt = """
Your task is to create Preventive Drug Education material for the Central Narcotics Bureau, the lead agency for preventive drug education in Singapore, dedicated to warning people on the dangers of drugs. 

Following the following guidelines:
TARGET AUDIENCE: {TARGET_AUDIENCE}
STYLISTIC DESCRIPTION: {STYLISTIC_DESCRIPTION}
CONTENT DESCRIPTION: {CONTENT_DESCRIPTION}
FORMAT: {FORMAT}
Create what is specified using html with ONLY text and visuals, with a modern and sleek look.

Do not include things like
    <li><a href="#">Home</a></li>  
    <li><a href="#">About</a></li>  
    <li><a href="#">Contact</a></li>  
as it is supposed to look like a static page. 


1. for the text content, it is sufficient to write [DESCRIPTION: ""],  with a short description text describing what is the content supposed to be. e.g: [DESCRIPTION: A brief introduction to the dangers of drug abuse]

2. For any images, specify the dimension, then replace the image link with a detailed description of a single image suitable for prompting an image model, like this: <div class="IMAGE_PLACEHOLDER"> [Image: 600x400] - A supportive scene showing a counselor or support group helping young adults. The image should convey a sense of hope and community, with warm, welcoming colors and expressions.] </div> 
the image descriptions should all follow a similar theme and be similar to stock image descriptions or visual elements for icons. Do not describe textual elements. 
Include this help hotline at the end: CNB Hotline (24-hours): 1800 325 6666 and a QR code image link bottom.

3. For html layouts other than posters, you MUST ensure that the width of the images is set to to 100 percent nd the height to auto so that they can adapt to the size of their containers. Do not just arrange elements in a boring, linear manner. 

EXAMPLE OUTPUT :

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Family Drug Awareness - Central Narcotics Bureau</title>
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
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);  
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
        .content-box img {  
            width: 100%;  
            height: auto;  
            border-radius: 5px;  
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
        .qr-placeholder img {
            width: 100px; /* Set the desired width */
            height: 100px; /* Set the desired height */
            object-fit: cover; /* Ensure the image covers the area without distortion */
        }
  
        /* Responsive adjustments */  
        @media (max-width: 768px) {  
            .container {  
                grid-template-columns: repeat(2, 1fr);  
            }  
            .span-2 {  
                grid-column: span 2;  
            }  
            .span-3 {  
                grid-column: span 2;  
            }  
        }  
        @media (max-width: 480px) {  
            .container {  
                grid-template-columns: 1fr;  
            }  
            .span-2, .span-3, .full-width {  
                grid-column: span 1;  
            }  
        }  
    </style> 
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Protecting Our Families: Understanding and Preventing Drug Abuse</h1>
        </header>

        <div class="content-box span-2">
            <div class="image-placeholder">
                [Image: 600x400 - A diverse group of Singaporean families enjoying quality time together in a park setting. The image should depict parents and children of various ages engaged in activities like picnicking, playing games, and talking, conveying a sense of unity and positive family dynamics.]
            </div>
        </div>

        <div class="content-box span-2">
            [DESCRIPTION: "An introduction to the importance of family involvement in drug prevention, emphasizing the role of parents in guiding and supporting their children."]
        </div>

        <div class="content-box span-3">
            [DESCRIPTION: "Overview of current drug trends in Singapore, including information on commonly abused substances and their effects on individuals and families."]
        </div>

        <div class="content-box">
            <div class="image-placeholder">
                [Image: 300x300 - An infographic-style illustration showing the brain and how different drugs affect its various regions. Use simplified, icon-based visuals to represent different areas of the brain and drug impacts.]
            </div>
        </div>

        <div class="content-box span-2">
            [DESCRIPTION: "Guidance on how to talk to children about drugs, including age-appropriate conversation starters and tips for maintaining open communication."]
        </div>

        <div class="content-box span-2">
            <div class="image-placeholder">
                [Image: 600x300 - An image showing positive parent-child interaction. The scene should depict active listening and engaged conversation between parents and children of various ages.]
            </div>
        </div>

        <div class="content-box full-width">
            [DESCRIPTION: "Signs and symptoms of drug use that parents should be aware of, including behavioral, physical, and social indicators."]
        </div>

        <div class="content-box span-2">
            <div class="image-placeholder">
                [Image: 600x400 - A warm, inviting home environment with subtle visual cues representing a drug-free lifestyle. Include elements like family photos, healthy snacks, sports equipment, and educational materials to suggest a supportive family atmosphere.]
            </div>
        </div>

        <div class="content-box span-2">
            [DESCRIPTION: "Strategies for creating a supportive home environment that discourages drug use, including establishing clear rules, promoting healthy activities, and strengthening family bonds."]
        </div>

        <div class="content-box span-3">
            [DESCRIPTION: "Information on Singapore's drug laws and policies, emphasizing the legal consequences of drug offenses and the importance of prevention."]
        </div>

        <div class="content-box">
            <div class="image-placeholder">
                [Image: 300x300 - A conceptual illustration representing Singapore's strong stance against drugs. Use symbolic elements like a shield, a family silhouette, and iconic Singapore landmarks to convey protection and national unity in drug prevention.]
            </div>
        </div>

        <footer class="footer">
            <div>
                <h3>24/7 CNB Hotline</h3>
                <p>1800 325 6666</p>
            </div>
            <div class="qr-placeholder">
                <img src="qr.png" alt="QR Code">
            </div>
        </footer>
    </div>
</body>
</html>
"""

response = openai_client.chat.completions.create(
    model=azure_openai_chat_completions_deployment_name,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_response_wrapper_prompt}
    ],
    max_tokens=4096,
    temperature=0.7,
    top_p=0.95,
)
output = extract_html_content(response.choices[0].message.content)

with open("first_draft.html", "w") as file:
    file.write(output)


