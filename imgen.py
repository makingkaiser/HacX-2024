import asyncio  
import replicate  
from uuid import uuid4  
from typing import List 
import os
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")

class GraphicElement:  
    def __init__(self, element_type, description, dim = None, content = None):  
        self.id = str(uuid4())  
        self.type = element_type
        self.description = description  
        self.content = content
        self.dim = dim

# Asynchronous function to run a prediction and track progress  
async def run_prediction(element: GraphicElement) -> List[GraphicElement]:  
    input_data = {  
        "prompt": element.description  
    }  
    prediction = replicate.predictions.create(  
        model="black-forest-labs/flux-schnell",  
        input=input_data  
    )  
      
    # Check progress asynchronously  
    while prediction.status not in ["succeeded", "failed", "canceled"]:  
        await asyncio.sleep(2)  # Pause for 2 seconds before checking again  
        prediction = replicate.predictions.get(prediction.id)  
        log_output = prediction.logs  
        if log_output:  
            current_iteration = log_output.count("it [")  
            total_iterations = 28  # Fixed number of iterations  
            progress_percentage = (current_iteration / total_iterations) * 100  
            print(f"Prompt: {element.description[:30]}... Progress: {progress_percentage:.2f}%")  
        else:  
            print(f"Prompt: {element.description[:30]}... Progress: Not available yet.")  
      
    # Handle result  
    if prediction.status == "succeeded":  
        print(f"Prompt: {element.description[:30]}... Prediction completed successfully!")  
        element.content = prediction.output  
    else:  
        print(f"Prompt: {element.description[:30]}... Prediction failed with status: {prediction.status}")  
        element.content = "Error generating image"  
  
# Function to run multiple predictions asynchronously  
async def run_multiple_predictions(elements: List[GraphicElement]):  
    tasks = [run_prediction(element) for element in elements if element.type == "image"]  
    await asyncio.gather(*tasks)  
    return elements  
  
# Example usage:  
async def main():  
    # Example list of GraphicElement instances  
    elements = [  
        GraphicElement(  
            element_type="image",  
            description="A serene landscape with mountains in the background and a clear blue sky."  
        ),  
        GraphicElement(  
            element_type="image",  
            description="A futuristic city skyline with tall skyscrapers and flying cars."  
        ),  
        GraphicElement(  
            element_type="text",  
            description="Event details"  
        )  
    ]  
      
    # Run the predictions asynchronously  
    updated_elements = await run_multiple_predictions(elements)  
      
    # Print updated GraphicElements  
    for element in updated_elements:  
        print(f"ID: {element.id}, Type: {element.type}, Description: {element.description}, Content: {element.content}")  
  

if __name__ == "__main__":  
    asyncio.run(main())  

