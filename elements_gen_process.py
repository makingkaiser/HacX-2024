"""
elements_gen_process.py
- vector_gen_process
- visual_aids_gen_process
- cards_gen
- bg_gen
- slogan_gen

folders in ./generated_images 
vectors
visualaids
slogans
cards
bgs

"""

from utils.initialize_client import create_openai_completion
import os
import asyncio
import replicate
import requests
from uuid import uuid4
from dotenv import load_dotenv
from visualfidelity import checkvisualfidelity
from textfidelity import check_text_fidelity
from functools import partial 
import shutil
import logging


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function for banner logs to highlight the operation
def banner_log(message):
    logging.info(f"\n{'='*20}\n{message}\n{'='*20}\n")

load_dotenv()

prompt_vector = """
Design vector images that include vector elements of '[insert a few vector elements here]' for a drug prevention poster in the style of '[insert artistic style here]'. \
These vector images should reinforce the point that : '[insert anti-drug message or drug statistic here]'. \
Ensure that the vector images are clear, engaging, and suitable for educational materials, and that they are generated on a WHITE BACKGROUND.
"""
prompt_va = """
Create a visual aid for the statistic '[insert statistic here]' like a '[insert most appropriate visual aid for this statisic like a bar or pie chart]' WITHOUT ANY TEXT . \
Design the visual aid to align with the theme '[insert theme here]' and in the artistic style '[insert style here]'. \
Ensure the visual is clear, engaging, and suitable for educational materials, and that it is generated on a WHITE BACKGROUND with MINIMAL TEXT.
"""
prompt_card = """
Create a simple text box that fits '[insert intended aesthetic or theme here]' for points in an infographic. \
It should have a simple, neutral design with a subtle texture or gradient, suitable for adding text and graphics over it without visual interference. \
It should be versatile and unobtrusive, ideal for data visualization or other informational content.
"""
prompt_bg = """
Generate a detailed and vibrant background image for a drug prevention poster. \
The background should depict '[insert content here]', evoke '[insert emotion here]', and promote '[insert message here]'.
"""
prompt_slogan = """
Create a slogan banner for a drug prevention poster. \
The banner should feature the slogan '[insert slogan text here]' in large, bold, clear, and uplifting typography. \
Ensure the background of the banner is white and includes ONLY THE TEXT SLOGAN.
"""

prompt_list_1 = [prompt_card, prompt_bg, prompt_slogan]
prompt_list_2 = [prompt_vector, prompt_va]

def get_prompts_1():
    return prompt_list_1 

def get_prompts_2():
    return prompt_list_2

# def save_image(url, desc, save_dir):
#     """
#     Save an image from a URL to a local directory, ensuring filename is valid for Windows.
#     """
#     try:
#         # Ensure the directory exists
#         os.makedirs(save_dir, exist_ok=True)
        
#         # Sanitize the description to create a valid filename
#         # Remove problematic characters and limit the length
#         safe_desc = "".join(c for c in desc if c.isalnum() or c in (' ', '_', '-')).rstrip()
#         safe_desc = safe_desc.replace('\n', ' ').replace('\\', '').replace('/', '')  # Remove newlines and slashes
#         safe_desc = safe_desc[:50]  # Limit to 50 characters
#         unique_id = uuid4()  # Generate a unique identifier
        
#         file_name = f"{unique_id}_{safe_desc}.jpg"
#         file_path = os.path.join(save_dir, file_name)

#         # Download and save the image
#         response = requests.get(url, stream=True)
#         response.raise_for_status()  # Raises an HTTPError for bad responses
#         with open(file_path, 'wb') as file:
#             shutil.copyfileobj(response.raw, file)
        
#         logging.info(f"Image successfully saved to {file_path}")
#         return file_path

#     except requests.exceptions.RequestException as e:
#         logging.error(f"Failed to download the image: {e}")
#     except OSError as e:
#         logging.error(f"File operation failed: {e}, Path: {file_path}")
#     except Exception as e:
#         logging.error(f"An unexpected error occurred: {e}")

#     return None

async def expand_flux_prompts(target_audience, stylistic_description, content_description, prompts):

    grounded_prompt = f"""
    Using the given user input as guidelines: 
    Target Audience: {target_audience}
    Stylistic Description: {stylistic_description}
    Content_description: {content_description}
    
    Copy each prompt and fill in the single-quoted portions based on the user input, and make it as detailed as possible to generate cohesive elements for a preventative drug education poster. \
    Make sure no text is generated unless it's a slogan. \
    Then, return ONLY THE EXPANDED PROMPTS IN SEMICOLON SEPARATED LIST AS SUCH prompt1;prompt2;prompt3 \
    Here are the prompts: \ 
    {prompts}
    """
    response = await create_openai_completion(grounded_prompt)
    if response.choices:
        result = response.choices[0].message.content.strip()
        # Normalize and ensure correct splitting
        normalized_result = result.replace("\n", "").replace("]", "").replace("[", "").replace("'", "").strip()
        
        # Split based on semicolons
        if ";" in normalized_result:
            return [part.strip() for part in normalized_result.split(";") if part.strip()]
        else:
            # Logging for debug purposes if delimiter is incorrect
            print("Expected delimiter ';' not found; fallback split applied.")
            return [part.strip() for part in normalized_result.split(",") if part.strip()]
    else:
        return ["Prompts not expanded."]


async def image_prediction(description):
    # Set API token
    os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

    def save_image(url, desc, type):
        """
        Save the image to a directory based on its type. Append a unique ID to the filename to ensure uniqueness.
        Sanitize the description to remove invalid characters and limit the length.
        """
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            target_dir = os.path.join(script_dir, 'generated_images', type)
            os.makedirs(target_dir, exist_ok=True)

            # Sanitize the description for safe filename use and append a unique ID
            safe_desc = "".join(c for c in desc if c.isalnum() or c in (' ', '_', '-')).rstrip()
            safe_desc = safe_desc[:50]  # Limit to 50 characters
            unique_id = str(uuid4())  # Generate a unique identifier
            file_name = f"{unique_id}_{safe_desc}.jpg"

            file_path = os.path.join(target_dir, file_name)

            # Download and save the image
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Check for request errors
            with open(file_path, 'wb') as file:
                shutil.copyfileobj(response.raw, file)

            logging.info(f"Image successfully saved to {file_path}")
            return file_path

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download the image: {e}")
            return None
        except OSError as e:
            logging.error(f"File operation failed: {e}, Path: {file_path}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None

    def classify_description(description):
        """
        Classify the description to determine the type of the image.
        """
        if "vector images" in description:
            return "vectors"
        elif "background image" in description:
            return "bgs"
        elif "slogan banner" in description:
            return "slogans"
        elif "text box" in description:
            return "cards"
        elif "visual aid" in description:
            return "visualaids"
        else:
            return "unclassified"

    def check_fidelity(description, image_url):
        """
        Check fidelity based on description.
        """
        logging.info(f"Checking fidelity for image at {image_path}")
        visual_pass, text_pass = None, None
        if "vector images" in description or "visual aid" in description or "blank box" in description:
            visual_pass = checkvisualfidelity(image_path, 'A')
            text_pass = check_text_fidelity(image_path)
        elif "background image" in description:
            visual_pass = checkvisualfidelity(image_path, 'B')
            text_pass = check_text_fidelity(image_path)
        elif "slogan banner" in description:
            text_pass = check_text_fidelity(image_path)
        
        # Return True only if all necessary checks pass
        return (visual_pass if visual_pass is not None else True) and (text_pass if text_pass is not None else True)


    def safe_delete(file_path):
        """
        Safely delete a file, checking if it exists first.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Deleted: {file_path}")
        else:
            logging.warning(f"File not found, could not delete: {file_path}")


# Replace os.remove(image_path) with safe_delete(image_path) in your script.

    successful = False
    attempts = 0
    max_attempts = 5  # Define max attempts to avoid infinite loops

    while not successful and attempts < max_attempts:
        image_type = classify_description(description)
        banner_log(f"Generating Image Type: {image_type.upper()}, description is {description}")  # Banner log for image type
        input_data = {"prompt": description}
        loop = asyncio.get_running_loop()

        prediction = await loop.run_in_executor(None, partial(replicate.predictions.create,
                                                              model="black-forest-labs/flux-dev",
                                                              input=input_data))

        while prediction.status not in ["succeeded", "failed", "canceled"]:
            await asyncio.sleep(2)
            prediction = replicate.predictions.get(prediction.id)

        if prediction.status == "succeeded":
            try:
                if prediction.output:
                    image_url = prediction.output[0]
                    image_path = save_image(image_url, description, image_type)
                    if check_fidelity(description, image_url):
                        print("Fidelity check passed.")
                        successful = True
                    else:
                        print("Fidelity check failed, regenerating...")
                        safe_delete(image_path)  
                else:
                    print("No image URL available in prediction output.")
            except AttributeError as e:
                print(f"Failed to access image data: {e}")
        else:
            print(f"Prediction failed with status: {prediction.status}")

        attempts += 1

    if not successful:
        print("Failed to generate a valid image after maximum attempts.")

async def multiple_image_prediction(prompts):
    tasks = [image_prediction(prompt) for prompt in prompts]
    await asyncio.gather(*tasks)

# def save_image(image_url, description):
#     """
#     Saves an image from a URL to the appropriate directory based on the description.
#     Description tags determine the subfolder in which the image is saved.
#     """

#     base_dir = "./generated_images"
    
#     # Determine the subfolder based on description
#     if "vector images" in description:
#         subfolder = "vectors"
#     elif "visual aid" in description:
#         subfolder = "visualaids"
#     elif "blank box" in description:
#         subfolder = "cards"
#     elif "background image" in description:
#         subfolder = "bgs"
#     elif "slogan banner" in description:
#         subfolder = "slogans"
#     else:
#         subfolder = "unclassified"  # Default folder for unmatched categories
#         print(f"Warning: Description '{description}' did not match any specific folder. Saving to 'unclassified'.")

#     # Create the folder if it doesn't exist
#     folder_path = os.path.join(base_dir, subfolder)
#     os.makedirs(folder_path, exist_ok=True)
    
#     # Create a unique file name
#     file_name = str(uuid.uuid4()) + '.png'
#     file_path = os.path.join(folder_path, file_name)
    
#     # Download and save the image
#     response = requests.get(image_url)
#     if response.status_code == 200:
#         with open(file_path, 'wb') as file:
#             file.write(response.content)
#         print(f"Image saved successfully in {file_path}")
#     else:
#         print("Failed to download the image.")

# async def main():
#     target_audience = "early teens still in school"
#     stylistic_description = "cartoonish, colorful and engaging"
#     content_description = "the harmful effects of cannabis on growing up; 38% of teens have felt peer pressure to try weed"
    
#     # Await the result from expand_flux_prompts
#     description_list = await expand_flux_prompts(target_audience, stylistic_description, content_description)
    
#     # Call multiple_image_prediction with the result
#     await multiple_image_prediction(description_list)

# if __name__ == "__main__":
#     # Use asyncio.run to run the async main function
#     asyncio.run(main())