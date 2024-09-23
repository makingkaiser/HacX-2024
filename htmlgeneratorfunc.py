# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
import asyncio
# Standard library imports
import re
from utils.initialize_client import create_openai_completion
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


async def generate_html_content(target_audience: str, stylistic_description: str, content_description: str, format: str) -> str:
    
    user_response_wrapper_prompt = f"""
    Your task is to create Preventive Drug Education material for the Central Narcotics Bureau, the lead agency for preventive drug education in Singapore, dedicated to warning people on the dangers of drugs. 

    Following the following guidelines:
    TARGET AUDIENCE: {target_audience}
    STYLISTIC DESCRIPTION: {stylistic_description}
    CONTENT DESCRIPTION: {content_description}
    FORMAT: {format}
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

    EXAMPLE OUTPUT - for image and text descriptions, you do not have to follow it exactly, but the adjacent text and images should be coherent. :

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Family Drug Awareness - Central Narcotics Bureau</title>
        <style>  
            body {{ 
                font-family: 'Arial', sans-serif;  
                margin: 0;  
                padding: 0;  
                background-color: #f0f4f8;  
                color: #333;  
            }}
            .container {{
                max-width: 1200px;  
                margin: 0 auto;  
                padding: 20px;  
                display: grid;  
                grid-template-columns: repeat(4, 1fr);  
                grid-gap: 20px;  
            }}
            .header {{ 
                grid-column: 1 / -1;  
                background-color: #2c3e50;  
                color: white !important;  
                padding: 40px;  
                text-align: center;  
                border-radius: 10px;  
            }}  
            .content-box {{
                background-color: white;  
                padding: 20px;  
                border-radius: 10px;  
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);  
            }}  
            .span-2 {{  
                grid-column: span 2;  
            }}
            .span-3 {{
                grid-column: span 3;  
            }}
            .full-width {{ 
                grid-column: 1 / -1;  
            }} 
            .content-box img {{  
                width: 100%;  
                height: auto;  
                border-radius: 5px;  
            }}
            .image-placeholder {{  
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
            }}
            .footer {{  
                grid-column: 1 / -1;  
                background-color: #2c3e50;  
                color: white !important;  
                padding: 20px;  
                text-align: center;  
                border-radius: 10px;  
                display: flex;  
                justify-content: space-around;  
                align-items: center;  
            }} 
            .qr-placeholder img {{
                width: 100px; /* Set the desired width */
                height: 100px; /* Set the desired height */
                object-fit: cover; /* Ensure the image covers the area without distortion */
            }}
    
            /* Responsive adjustments */  
        @media (max-width: 768px) {{  
            .container {{  
                grid-template-columns: repeat(2, 1fr);  
            }}  
            .span-2 {{  
                grid-column: span 2;  
            }}  
            .span-3 {{  
                grid-column: span 2;  
            }}  
        }}  
        @media (max-width: 480px) {{  
            .container {{  
                grid-template-columns: 1fr;  
            }}  
            .span-2, .span-3, .full-width {{  
                grid-column: span 1;  
            }}  
        }}   
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
                    [Image: 300x300 - A serene nature scene representing mental clarity and well-being. The image depicts a beautiful landscape with clear water, lush greenery, and a bright sky, symbolizing the benefits of a drug-free lifestyle.]
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
                    [Image: 600x400 - A warm, inviting home environment with subtle visual cues representing a drug-free lifestyle. The image includes family members engaged in various positive activities like playing sports, or cooking together.]
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
                    <a href="https://imgbb.com/"><img src="https://i.ibb.co/6tcJ0tB/qr.png" alt="qr"></a>
                </div>
            </footer>
        </div>
    </body>
    </html>
    """
    response = await create_openai_completion(user_response_wrapper_prompt)
    output = extract_html_content(response.choices[0].message.content)
    return output



