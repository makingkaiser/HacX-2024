from pydantic import BaseModel

from fastapi import FastAPI, HTTPException

app = FastAPI()

class Specifications(BaseModel):
    AGE_GROUP: str
    STRUCTURE: str
    STYLE: str

@app.post("/generate_html")
async def generate_html(specifications: Specifications):
    AGE_GROUP = specifications.AGE_GROUP
    STRUCTURE = specifications.STRUCTURE
    STYLE = specifications.STYLE
    
