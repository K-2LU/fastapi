import base64
import json
import logging
import re
from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
import pytesseract

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ImageRequest(BaseModel):
    imageBase64: str

@app.post("/extract-json")
async def extract_json_from_image(request: ImageRequest):
    try:
        header, encoded = request.imageBase64.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image, config="--psm 6").strip()

        extracted_text = re.sub(r"[^\x20-\x7E]", "", extracted_text) 
        logger.info(f"Extracted text: {extracted_text}")

        try:
            extracted_data = json.loads(extracted_text) 
            success = True
            message = "Successfully extracted JSON from image"
        except json.JSONDecodeError:
            extracted_data = {"error": "Failed to parse JSON from image"}
            success = False
            message = "Extracted text, but JSON parsing failed"

        return {
            "data": extracted_data,
        }
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
