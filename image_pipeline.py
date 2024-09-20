import openai  
import re  
# Set up your OpenAI API key  
openai.api_key = 'your-api-key'  
  
# Step 1: Set up initial user input and variables  
TARGET_AUDIENCE = "young adults"  
STYLISTIC_DESCRIPTION = "a modern, visually appealing layout."  
CONTENT_DESCRIPTION = "sections for information, testimonials, and resources"  
FORMAT = "information pamphlet"
# Step 2: Define the prompt template  
prompt_template = """  
I am trying to make a page for the ministry of Health in Singapore, dedicated to warning {AGE_GROUP} on the dangers of drugs.  
Following the following guidelines:
TARGET AUDIENCE: {TARGET_AUDIENCE}
STYLISTIC DESCRIPTION: {STYLISTIC_DESCRIPTION}
CONTENT DESCRIPTION: {CONTENT_DESCRIPTION}
FORMAT: {FORMAT}
Create what is specified using html with ONLY text and visuals, with a modern and sleek look.  
  
Do not include things like <li><a href="#">Home</a></li> <li><a href="#">About</a></li> <li><a href="#">Contact</a></li>   
as it is supposed to look like a static page. Do not just arrange elements in a boring, linear manner.   
  
1. for the text content, it is sufficient to write [PLACEHOLDER_TEXT; Description], replacing "Description" with a short description text describing what is the content supposed to be.   
2. For any images, specify the dimension, then replace the image link with a detailed description of the image suitable for prompting an image model, like this:   
<div class="IMAGE_PLACEHOLDER"> [Image: 600x400] - A supportive scene showing a counselor or support group helping young adults. The image should convey a sense of hope and community, with warm, welcoming colors and expressions.] </div>   
  
Include help hotline at the end and a QR code image placeholder for more information at the bottom.  
"""  
  
# Fill in the template with user input  
prompt = prompt_template.format(target_audience=TARGET_AUDIENCE,stylistic_description=STYLISTIC_DESCRIPTION,content_description=CONTENT_DESCRIPTION,format=FORMAT)
  
# Step 3: Make an API call to GPT  
response = openai.Completion.create(  
    engine="text-davinci-003",  
    prompt=prompt,  
    max_tokens=2048,  
    n=1,  
    stop=None,  
    temperature=0.7,  
)  
  
generated_html = response.choices[0].text.strip()  
  
# Utility function to extract image descriptions  
def extract_image_descriptions(html):  
    pattern = re.compile(r'<div class="IMAGE_PLACEHOLDER"> \[Image: \d+x\d+\] - (.*?) \]</div>')  
    return pattern.findall(html)  ## to test
  
# query gpt4o to improve upon descriptions for prompting, loosely based on stylistic elements of {user_described_desired_layout}


# Utility function to refine image descriptions (if needed)  
def refine_image_description(description):  
    #HAS TO PULL USER INPUT AS JSON AND IS PASSED IN PLACEHOLDER IMAGE DESC
    #image_caption_rag_refinement(user_input, placeholder_image_desc)
    return description  
  
# Utility function to generate image from description  
def generate_image_from_description(description):  
    # Placeholder for image generation logic  
    # For the sake of example, return a mock image URL  
    return f"https://example.com/generated_image?desc={description.replace(' ', '%20')}"  
  
# Utility function to inject images into HTML  
def inject_images_into_html(html, images):  
    pattern = re.compile(r'<div class="IMAGE_PLACEHOLDER"> \[Image: \d+x\d+\] - .*? \]</div>')  
    for img_url in images:  
        html = pattern.sub(f'<img src="{img_url}" alt="Generated Image"/>', html, 1)  
    return html  
  
# Step 4: Extract and refine image descriptions  
image_descriptions = extract_image_descriptions(generated_html)  
  
# Refine image descriptions (if needed)  
refined_image_descriptions = [refine_image_description(desc) for desc in image_descriptions]  
  
# Step 5: Generate images using the refined descriptions  
generated_images = [generate_image_from_description(desc) for desc in refined_image_descriptions]  
  
# Step 6: Inject images into HTML  
final_html = inject_images_into_html(generated_html, generated_images)  
  
# Output the final HTML  
print(final_html)  
