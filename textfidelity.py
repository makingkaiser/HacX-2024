import base64
from mimetypes import guess_type
import json
import os
from utils.initialize_client import initialize_azure_openai_client

# Function to encode a local image into a data URL
def local_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded_data}"

def get_image_text_coherence(data_url, intended_text=None):
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
                            "text": f"Analyze the text within the image for coherence with {intended_text}.\
                             If there is text, return the identified text followed by a semicolon, then determine its coherence and return 'True' without single quotes if it's coherent or 'False' if it's not.\
                             If there's no text, return 'No text:True'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url}
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        response_json = json.loads(response.to_json())
        text_and_coherence = response_json['choices'][0]['message']['content']

        # Handling cases where the expected ":" is not present
        if ':' in text_and_coherence:
            detected_text, coherence = text_and_coherence.split(':', 1)
        else:
            # Default to no text and True if the format is unexpected
            detected_text, coherence = 'No detected text', 'True'

        # Print detected text
        print(f"Detected Text: {detected_text.strip()}")

        return coherence.strip()
    except Exception as e:
        print("Failed to get text coherence:", str(e))
        return "Error"

def check_text_fidelity(image_path, intended_text=None):
    """
    This function will:
    1. Convert the local image to a data URL.
    2. Generate an analysis based on the text content within the image.
    3. Return 'True' if the text is coherent and 'False' otherwise.

    :param image_path: The file path of the image to process.
    :return: Boolean indicating if the text within the image is coherent.
    """
    try:
        data_url = local_image_to_data_url(image_path)
        text_coherence = get_image_text_coherence(data_url)
        print(f"Text Coherence: {text_coherence}")

        is_coherent = text_coherence.lower() == 'true'  # Assuming the response is just 'True' or 'False'
        return is_coherent
    except Exception as e:
        print(f"Error in check_text_fidelity: {str(e)}")
        return False

