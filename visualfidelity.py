"""
Visual fidelity check for the following 

Check A for relatively simple images
- Vector images after segmentation
- Visual aids (require to remove transparency)


Check B for complex images
- BG
- Multimodal pipeline generation 

"""
import base64
from mimetypes import guess_type
import json
import os
from utils.initialize_client import initialize_azure_openai_client

prompt_a = """
Generate a concise 10-word description focusing on the item in the given vector image. \
Be clear on whether the vector image is malformed or whole i.e. if it can be used as a standalone picture for the item its supposed to be. \ 
If there is text, assess whether it is semantically appropriate and coherent - if it's not, make the last word of the caption be 'gibberish'.
"""
prompt_b = """
Assess the AI-generated image for any signs of deformities or malformations. \
Criteria to consider include: inconsistencies in symmetry where expected, distortions in common shapes and objects, irregular patterns in textures, and any unexpected anomalies in the representation of standard elements (e.g., a tree with two trunks).\
Return 'True' (without quotes) if the image is free of any deformed or malformed elements and represents a cohesive, well-formed visual. \
Otherwise, return 'False' (without quotes) if any malformations or deformities are detected."""

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
    client = initialize_azure_openai_client()
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
                            "text": f"{prompt_a}"
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
    
def rename_image(file_path, caption):
    directory, old_file_name = os.path.split(file_path)
    file_name, file_extension = os.path.splitext(old_file_name)
    safe_caption = caption.lower().replace(' ', '_').replace("'", "").replace('"', '')
    new_file_name = f"{safe_caption}{file_extension}"
    new_file_path = os.path.join(directory, new_file_name)
    os.rename(file_path, new_file_path)
    return 

def visual_fidelity_assessment_a(caption):
    client = initialize_azure_openai_client()
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
                            "text": f"Based on the caption : {caption} \
                             Return only 'True' without the quotes if you think this is a well generated, well formed and semantically coherent vector image. Else return only 'False' without the quotes."
                        },
                    ]
                }
            ],
            max_tokens=300,
            stream=False
        )
       
        response_json = response.to_json()  
        response_json = json.loads(response_json)  
        
        #extract and return only the text content of the caption
        choice = response_json['choices'][0]['message']['content']
        return bool(choice)
    
    except Exception as e:
        print("Failed to get caption:", str(e))
        return f"Error: {str(e)}"
    
def visual_fidelity_assessment_b(data_url):
    client = initialize_azure_openai_client()
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
                            "text": f"{prompt_b}"
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
        choice = response_json['choices'][0]['message']['content']
        return bool(choice)
    
    except Exception as e:
        print("Failed to get caption:", str(e))
        return f"Error: {str(e)}"

def checkvisualfidelity(image_path, check_type):
    """
    This function will:
    1. Convert the local image to a data URL.
    2. Generate a caption based on the image content.
    3. Assess the visual fidelity of the image based on the caption.
    4. If the image is well-formed, rename the image based on the caption.

    :param image_path: The file path of the image to process.
    :return: The result of the visual fidelity assessment.
    """
    
    if check_type == 'A':
        try:
            # Convert image to a data URL
            data_url = local_image_to_data_url(image_path)

            # Generate a caption for the image
            caption = get_image_caption(data_url)
            print(f"Generated Caption: {caption}")

            # Assess the visual fidelity of the image based on the caption
            is_well_formed = visual_fidelity_assessment_a(caption)
            print(f"Visual Fidelity Assessment: {is_well_formed}")

            # If the image is well-formed, rename the image to the description
            # if is_well_formed:
            #     rename_image(image_path, caption)
            #     print(f"Image renamed based on caption: {caption}")

            return is_well_formed

        except Exception as e:
            print(f"Error in checkvisualfidelity: {str(e)}")
            return False
    
    elif check_type == 'B':
        try:
            # Convert image to a data URL
            data_url = local_image_to_data_url(image_path)

            # Assess the visual fidelity of image using vision
            is_well_formed = visual_fidelity_assessment_b(data_url)
            print(f"Visual Fidelity Assessment: {is_well_formed}")

            return is_well_formed

        except Exception as e:
            print(f"Error in checkvisualfidelity: {str(e)}")
            return False