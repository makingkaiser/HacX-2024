"""
Stand-alone module meant to initialize the image-caption-rag's search index.
Takes in images in ...
Outputs captions to ... and pushes to search service 
"""

# Standard library imports
import asyncio
import base64
from dotenv import load_dotenv
import os
import sys

# Third-party imports
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
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

# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../utils'))

from initialize_client import initialize_azure_openai_client, create_openai_completion

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

def safe_base64_encode(key):
    #Encode document keys in url safe base64 format
    encoded_bytes = base64.urlsafe_b64encode(key.encode('utf-8'))
    return encoded_bytes.decode('utf-8').rstrip('=')

def get_embeddings_vector(text):
    #Embed documents as vectors for vector search index
    openai_client = initialize_azure_openai_client()
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002",  
        )
        embedding = response.data[0].embedding
        return embedding
    
    except ClientAuthenticationError as e:
        print("Openai client authentication failed:", e)
        raise

    except Exception as e:
        print("Error in get_embeddings_vector:", e)
        raise

def image_create_search_index(caption_directory):
    """
    Configure and manage Azure Search index for handling image captions. 
    This function sets up the index with vector and semantic search capabilities, 
    handles indexing of image captions and manages upload of those captions into 
    Azure Search Service from the specified directory
    """
    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            sortable=True,
            filterable=True,
            facetable=True,
        ),
        SearchableField(name="image_title", type=SearchFieldDataType.String),
        SearchableField(name="image_caption", type=SearchFieldDataType.String),
        SearchField(name="vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536, #1536,
            vector_search_profile_name="myHnswProfile",
        ),
    ]

    #configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            )
        ]
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="image_title"),
            # keywords_fields=[SemanticField(field_name="category")],
            content_fields=[SemanticField(field_name="image_caption")]
        )
    )

    #create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    search_index_name = "index-captions"
    azure_search_service_admin_key = os.getenv('azure_search_service_admin_key')
    azure_search_service_endpoint = os.getenv('azure_search_service_endpoint')
    credential = AzureKeyCredential(azure_search_service_admin_key)

    try: 
        search_index = SearchIndex(
            name=search_index_name, 
            fields=fields,
            vector_search=vector_search, 
            semantic_search=semantic_search)
        
    except ClientAuthenticationError as e:
        print("Search index creation failed:", e)
        raise
    
    try:
    #search index client for updating or querying the index
        search_index_client = SearchIndexClient(
            endpoint=azure_search_service_endpoint, 
            index_name=search_index_name, 
            credential=credential
        )
    except ClientAuthenticationError as e:
        print("Search index client authentication failed:", e)
        raise

    search_index_client.create_or_update_index(search_index)

    try: 
    #search client to upload, query or manage documents
        search_client = SearchClient(
            endpoint=azure_search_service_endpoint, 
            index_name=search_index_name, 
            credential=credential
            )
        
    except ClientAuthenticationError as e:
        print("Search index client authentication failed:", e)
        raise
    
    #for caption in captions:
    for filename in os.listdir(caption_directory):
        if filename.endswith('.txt'):
            with open(os.path.join(caption_directory, filename), 'r', encoding='utf-8') as file:
                image_caption = file.read().strip()  #extract caption
                image_title = filename.replace('.txt', '')  #extract file name

                try:
                    embeddings_vector = get_embeddings_vector(image_caption)
                
                    document = {
                        "id" : safe_base64_encode(filename),
                        "image_title": image_title,
                        "image_caption": image_caption,
                        "vector": embeddings_vector  
                    }

                    result = search_client.upload_documents(documents=[document])
                    print(f"Upload of {filename} succeeded: {result[0].succeeded}")

                except Exception as e:
                    print(f"Failed to process and upload {filename}: {e}")

async def fetch_search_results(user_stylistic_description):
    """
    Fetches relevant captions and their title from image-caption-rag
    and returns list of dictionaries:
    [{'caption': 'The image presents a striking and...', 
    'title': 'Drug_abuse_prevention_(6800434328) (1)_caption'}]
    """
    azure_search_service_endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
    azure_search_service_admin_key = os.getenv('AZURE_SEARCH_SERVICE_ADMIN_KEY')
    search_index_name = "index-captions"

    # Init Azure Search client
    credential = AzureKeyCredential(azure_search_service_admin_key)
    search_client = SearchClient(endpoint=azure_search_service_endpoint,
                                 index_name=search_index_name,
                                 credential=credential)

    try:
        search_results = search_client.search(search_text=user_stylistic_description, 
                                 top=3, 
                                 select="image_caption, image_title"
                                 )

        return [{'caption': result['image_caption'], 'title': result['image_title']} for result in search_results]
    
    except Exception as e:
        print("An error occurred:", e)
        return None
    
#########################################################################################
#@@@@@@@@   BOILERPLATE CALL FOR IMAGE CAPTION RAG (Gpt4o+ Image Caption RAG)   @@@@@@@@#
#########################################################################################
"""
This will be used for idea generation based on graphical description from user input 
i.e. based on graphical description, try to find something similar as reference or 
inspiration

Input : 
    a) User Input (user_stylistic_description, target_audience,content_description)
    b) Rudimentary image description as a string that needs to be expanded upon with 
    references or with inspiration to existing images captions
*Misc is just intended to be an extra parameter we can feed in 
Output :  
    a) Reference Images to show on frontend
    b) Expanded Image Description as a string
"""
async def image_caption_rag_refinement(user_input, placeholder_image_desc, format):
    """
    Expands the placeholder image description based on user input
    and pulled images from image-caption-rag. Refer to bottom 
    for sample output.
    """
    # Correctly awaiting the async function directly
    search_results = await fetch_search_results(user_input['user_stylistic_description'])
    reference_captions = [result['caption'] for result in search_results] if search_results else []

    
    # Construct the grounded prompt for the OpenAI model
    grounded_prompt = f"""
    You are a creative assistant tasked with generating ideas or finding inspirations based on
    user-provided graphical descriptions. Given a baseline and based user content 
    description and stylistic preferences, create an image generation prompt that aligns 
    with the theme and tone suitable for {user_input['target_audience']}. You are given reference
    captions from previous material which you may use for inspiration but do not copy it.

    Baseline: {placeholder_image_desc}
    User Stylistic Description: {user_input['user_stylistic_description']}
    Reference Captions: {reference_captions}
    Content Description: {user_input['content_description']}
    Image will be used in a : {format}
    Guiderails: ONLY DESCRIBE THE IMAGE CONCISELY WITHIN 85 WORDS
    """

    # Correctly using an async call to completions_client if it's properly configured as async
    response = await create_openai_completion(grounded_prompt)

    expanded_description = response.choices[0].message.content if response.choices else "No description generated."

    return {
        "reference_images": search_results,
        "expanded_description": expanded_description
    }

## Example Execution
example_user_input = {
    'user_stylistic_description': "simple pleasure of sugary treats",
    'target_audience': "children 0-12",
    'content_description': "A colorful scene depicting a family game night."
}

"""
Example Execution Response
{
  "reference_images": [
    {
      "caption": "The image showcases five small, transparent plastic bags arranged in a 2x3 grid, each filled with colorful gummy bears. The artistic focus is on simplicity and repetition, emphasizing the playful, vibrant variety of the candy hues. Each packet gleams with a soft holographic sheen indicative of the packaging’s finish, casting a light iridescence that interacts dynamically with the multicolored contents. This interaction creates a visual texture that's both appealing to the eye and suggestive of a candy shop's exuberant energy. The composition’s straightforward symmetry and cluster formation underscore a commercial aesthetic, designed to attract and engage with an emphasis on abundance and accessibility. The overall mood is light-hearted and fun, evoking a sense of childlike wonder through the simple pleasure of sugary treats.",
      "title": "image_page_13_111_caption"
    },
    {
      "caption": "The image, designed for educational purposes, employs a vibrant and approachable artistic style, illustrative of contemporary graphic design focused on public awareness. Dominated by a bright color palette, it features hues of pink, blue, and yellow that capture attention and convey a positive, hopeful mood. The figures are dressed in simple, everyday clothing which aligns with the image’s intention to relate to a broad audience. Graphic elements, such as the bold yellow title and the blue ribbon symbol at the bottom, add informative and directing attributes, guiding the viewer’s focus toward the message of drug prevention. The overall composition is straightforward and clean, with a central alignment that promotes an organized and impactful visual communication. This setup not only reinforces the significance of family unity in the context of the message but also enhances the digestibility of the educational content conveyed.",
      "title": "pde-cnb-booklet-fa5aea07f114a46b78a186ff0000079eb0_caption"
    },
    {
      "caption": "The image adopts a bold and impactful poster design that utilizes a stark color contrast of bright lime green and black to command attention and deliver a powerful message. Centered prominently is the slogan 'Say No to Drugs, Choose Life, Not Addiction' in large, black, block lettering on a vibrant green background, reinforcing the urgency and critical nature of the message. The top right features a monochromatic photograph of two white pills, which starkly contrasts against the green, adding visual interest and focus to the theme of drug abstinence. Below the central message, on a black background, the event details are presented in white and green text, offering clear information without distracting from the main message. The overall composition is simple yet effective, creating an aesthetic that is both authoritative and educational. The style is direct and unambiguous, aimed at delivering a life-saving message compellingly and memorably.",
      "title": "83ae6654-3868-43de-a74b-46f4eefd4ddc (1)_caption"
    }
  ],
  "expanded_description": "A vibrant, engaging illustration showcases a family gathered around a table for game night. The parents and two children, all dressed in cozy, colorful outfits, share laughter and excitement as they play a board game. The table is adorned with playful elements like dice, cards, and a bowl of candy. Bright, cheerful hues of blue, yellow, and red dominate the scene, creating a warm, inviting atmosphere. The background features soft, whimsical patterns that add to the light-hearted, joyful tone, making it perfect for children."
}

"""

## Execution for image_create_search_index
# root_path = sys.path[0]
# caption_directory = os.path.join(root_path, "data-ingress", "images", "image_captions")
# image_create_search_index(caption_directory)

# # Test Execution for fetch_search_results
# result = await fetch_search_results("monopoly board")
# print(result)

## Test Execution for image_caption_rag_refinement

async def main():
    result = await image_caption_rag_refinement(example_user_input, "picture of the negative effects of cocaine", format="pamphlet")
    print(result)

# asyncio.run(main())