import base64
from mimetypes import guess_type
import json
import os

from utils.initialize_client import initialize_azure_openai_client

# Configuration
base_path = os.path.dirname(__file__)
base_directory = os.path.join(base_path, "..", "..", "data-ingress", "images")
img_directory = os.path.join(base_directory, "source_images")
cpt_directory = os.path.join(base_directory, "image_captions")
img_directory = os.path.abspath(img_directory)
cpt_directory = os.path.abspath(cpt_directory)

os.makedirs(cpt_directory, exist_ok=True)

client = initialize_azure_openai_client()

# Function to encode a local image into a data URL
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

def get_image_caption(data_url):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Generate a detailed 100-word description focusing on the stylistic design and artistic style of the given image. Include key visual elements, the mood conveyed, and any unique characteristics that define the art. Ensure the description captures the essence of the artwork, reflecting on its colors, composition, and overall aesthetic."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
            stream=False
        )
       
        response_json = response.to_json()  
        response_json = json.loads(response_json)  
        
        #extract and return only the text content of the caption
        caption_content = response_json['choices'][0]['message']['content']
        return caption_content

    except Exception as e:
        print("Failed to get caption:", str(e))
        return f"Error: {str(e)}"

#for image in image_directory:
for filename in os.listdir(img_directory):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        filepath = os.path.join(img_directory, filename)
        data_url = local_image_to_data_url(filepath)
        print(f"Processing {filename}...")
        caption = get_image_caption(data_url)
        print(f"Caption for {filename}: {caption}")

        #save caption locally (or upload to blob storage if necessary)
        caption_filename = f"{os.path.splitext(filename)[0]}_caption.txt"
        caption_filepath = os.path.join(cpt_directory, caption_filename)
        with open(caption_filepath, "w", encoding="utf-8") as caption_file:
            caption_file.write(caption)
        print(f"Saved {filename} and its caption locally.")
