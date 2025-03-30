import base64
import json
from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
import pytesseract

app = FastAPI()

class ImageRequest(BaseModel):
    imageBase64: str

@app.post("/extract-json")
async def extract_json_from_image(request: ImageRequest):
    try:
        # Decode Base64 Image
        header, encoded = request.imageBase64.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_bytes))

        # Extract text from image
        extracted_text = pytesseract.image_to_string(image)

        # Convert extracted text to structured JSON
        try:
            extracted_data = json.loads(extracted_text)  # Assumes image contains valid JSON
        except json.JSONDecodeError:
            extracted_data = {"error": "Failed to parse JSON from image"}

        return {
            "success": True,
            "data": extracted_data,
            "message": "Successfully extracted JSON from image"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
