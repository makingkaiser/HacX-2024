import streamlit as st
import asyncio
from htmlgeneratorfunc import generate_html_content
from main import flesh_out_html
from regenpipeline import regenerate_content

# Example Execution  
if __name__ == "__main__":  
    st.title("HTML Content Regenerator")  
    html_content = '''<!DOCTYPE html>  
<html lang="en">  
<head>  
    <meta charset="UTF-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1.0">  
    <title>Drug Awareness for Young Adults - Central Narcotics Bureau</title>  
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
        .qr-placeholder {  
            width: 100px;  
            height: 100px;  
            background-color: white;  
            display: flex;  
            justify-content: center;  
            align-items: center;  
            font-style: italic;  
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
            <h1>Stay Smart, Stay Safe: Drug Awareness for Young Adults</h1>  
        </header>  
        <div class="content-box span-2">  
            <img src="https://replicate.delivery/yhqm/Ae4hA3p8cL0EASTuVm7qt8EDfFyERkzefnYT7mFOpRRyXo1NB/out-0.webp" alt="[Image: 300x200 - A group of diverse young adults studying together in a cozy library setting, engaged and focused, conveying a sense of purpose and positive peer interaction.]">  
        </div>  
        <div class="content-box span-2">  
            [DESCRIPTION: "An introduction to the importance of drug awareness for young adults, emphasizing the impact of drugs on their future and well-being."]  
        </div>  
        <div class="content-box span-3">  
            [DESCRIPTION: "Overview of the most common drugs abused by young adults in Singapore, including their effects and dangers."]  
        </div>  
        <div class="content-box">  
            <img src="https://replicate.delivery/yhqm/IeKeREzJb5ixwEj2KjYbk7IURAWe3mkXCbLIwGjkySr4L06mA/out-0.webp" alt="[Image: 300x200 - An infographic-style illustration showing the physical and mental effects of drugs on the human body, using simplified, icon-based visuals to represent different organs and their response to drug use.]">  
        </div>  
        <div class="content-box span-2">  
            [DESCRIPTION: "Tips and strategies for resisting peer pressure and making healthy choices, including real-life scenarios and advice."]  
        </div>  
        <div class="content-box span-2">  
            <img src="https://replicate.delivery/yhqm/CLfDAiUYu5TfUkCC4b14kcCxlOWINFhFCNvf35hOQEI7L06mA/out-0.webp" alt="[Image: 300x200 - Young adults participating in a sports activity, depicting camaraderie, physical fitness, and a drug-free lifestyle.]">  
        </div>  
        <div class="content-box full-width">  
            [DESCRIPTION: "Signs and symptoms of drug use that young adults should be aware of in themselves and their peers, including behavioral, physical, and social indicators."]  
        </div>  
        <div class="content-box span-2">  
            <img src="https://replicate.delivery/yhqm/BKUcVoCgL05RAFqEf1MJteHaNGTePiYs8FiTDqzakvH6L06mA/out-0.webp" alt="[Image: 300x200 - A vibrant, youth-friendly community center with educational posters, recreational equipment, and a bulletin board with positive messages about drug-free living.]">  
        </div>  
        <div class="content-box span-2">  
            [DESCRIPTION: "Resources and support available for young adults, including counseling services, hotlines, and community programs."]  
        </div>  
        <div class="content-box span-3">  
            [DESCRIPTION: "Information on Singapore's drug laws and policies, emphasizing the legal consequences of drug offenses and the importance of prevention."]  
        </div>  
        <div class="content-box">  
            <img src="https://replicate.delivery/yhqm/zIUy7LX68qK4OdUlbDGjeGqWhMr0qB8mfuZuykdESl89FadTA/out-0.webp" alt="[Image: 300x200 - A conceptual illustration representing Singapore's strong stance against drugs, using symbolic elements like a shield, a youth silhouette, and iconic Singapore landmarks to convey protection and national unity in drug prevention.]">  
        </div>  
        <footer class="footer">
    </div>  
</body>  
</html>  
'''  
# if st.button("Regenerate Content"):  
    regenerated_html = asyncio.run(regenerate_content(html_content))  




# async def test_gpt_regen_image_desc():  
#     combined_input = "A beautiful sunrise over the mountains. User wants to refine it: Add more vibrant colors and a clear sky."  
#     refined_description = await gpt_regen_image_desc(combined_input)  
#     print(refined_description)  
  
# # Run the test  
# asyncio.run(test_gpt_regen_image_desc())  





# async def test_regenerate_image():  
#     previous_element = GraphicElement(  
#         element_type="image",  
#         description="A beautiful sunrise over the mountains.",
#     )  
#     user_input = "Add more vibrant colors and a clear sky."  
#     regenerated_element = await regenerate_image(user_input, previous_element)  
#     print(f"New Description: {regenerated_element.description}")  
#     print(f"New Image URL: {regenerated_element.content}")  
  
# # Run the test  
# if __name__ == "__main__":  
#     asyncio.run(test_regenerate_image()) 





# async def test_regenerate_text():
#     previous_element = GraphicElement(  
#         element_type="text",  
#         description="This is a sample text that needs improvement."  
#     )  
#     user_input = "Make it more formal and concise."  
#     refined_element = await regenerate_text(user_input, previous_element)  
#     print(refined_element.refined) 

#     # Run the test  
# if __name__ == "__main__":  
#     asyncio.run(test_regenerate_text()) 





# def test_extract_image_links():
#     html_file_path = Path('test.html')
#     html_content = html_file_path.read_text()

#     # Process the HTML content
#     result = extract_image_links(html_content)
#     print(result)



# def test_regenerate_text():
    # previous_element = GraphicElement(  
    #     element_type="text",  
    #     description="This is a sample text that needs improvement."  
    # )  
    # user_input = "Make it more formal and concise."  
    # refined_element = await regenerate_text(user_input, previous_element)  
    # print(refined_element.description)  