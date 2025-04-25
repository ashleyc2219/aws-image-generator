import json
import numpy as np
from fastapi import APIRouter, HTTPException
from models import (
    ImageResponse,
    TextImageRequest,
    TaskTypeEnum,
    BackgroundRemovalRequest,
    ImageVariationRequest,
)
from utils import save_image
import base64

router = APIRouter()


def create_router(config):
    bedrock_client = config["bedrock_client"]
    image_model = config["image_model"]
    output_dir = config["output_dir"]

    @router.post("variation", response_model=ImageResponse)
    async def generate_variation(request: ImageVariationRequest):
        """Generate image based on references iamges(max=5)"""

        body = json.dumps(
            {
                "taskType": TaskTypeEnum.IMAGE_VARIATION,
                "imageVariationParams": request.imageVariationParams,
                "imageGenerationConfig": request.imageGenerationConfig,
            }
        )
        try:
            response = bedrock_client.invoke_model(
                body=body,
                modelId=image_model,
                accept="application/json",
                contentType="application/json",
            )

            response_body = json.loads(response.get("body").read())
            base64_images = response_body.get("images", [])

            image_paths = []
            for i, base64_image in enumerate(base64_images):
                # Generate a unique filename
                image_path = f"{output_dir}/text-to-image_{int(np.random.random() * 1000000)}_{i}.png"
                save_image(base64_image, image_path)
                image_paths.append(image_path)

            return {"image_paths": image_paths, "base64_images": base64_images}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating image: {str(e)}"
            )

    @router.post("/remove-bg", response_model=ImageResponse)
    async def remove_bg(request: BackgroundRemovalRequest):
        """Remove given image background"""

        # for test
        with open("output/text-to-image_572_0.png", "rb") as image_file:
            input_image = base64.b64encode(image_file.read()).decode("utf8")
        request.backgroundRemovalParams.image = input_image

        body = json.dumps(
            {
                "taskType": TaskTypeEnum.BACKGROUND_REMOVAL,
                "backgroundRemovalParams": request.backgroundRemovalParams.dict(
                    exclude_none=True
                ),
            }
        )
        print(body)
        try:
            response = bedrock_client.invoke_model(
                body=body,
                modelId=image_model,
                accept="application/json",
                contentType="application/json",
            )

            response_body = json.loads(response.get("body").read())
            base64_images = response_body.get("images", [])

            image_paths = []
            for i, base64_image in enumerate(base64_images):
                # Generate a unique filename
                image_path = f"{output_dir}/text-to-image_{int(np.random.random() * 1000000)}_{i}.png"
                save_image(base64_image, image_path)
                image_paths.append(image_path)

            return {"image_paths": image_paths, "base64_images": base64_images}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating image: {str(e)}"
            )

    @router.post("/text-to-image", response_model=ImageResponse)
    async def text_to_image(request: TextImageRequest):
        """Generate images based on a text prompt"""
        body = json.dumps(
            {
                "taskType": TaskTypeEnum.TEXT_IMAGE,
                "textToImageParams": request.textImageParams.dict(exclude_none=True),
                "imageGenerationConfig": request.imageGenerationConfig.dict(
                    exclude_none=True
                ),
            }
        )

        print(body)
        try:
            response = bedrock_client.invoke_model(
                body=body,
                modelId=image_model,
                accept="application/json",
                contentType="application/json",
            )

            response_body = json.loads(response.get("body").read())
            base64_images = response_body.get("images", [])

            image_paths = []
            for i, base64_image in enumerate(base64_images):
                # Generate a unique filename
                image_path = f"{output_dir}/text-to-image_{int(np.random.random() * 1000000)}_{i}.png"
                save_image(base64_image, image_path)
                image_paths.append(image_path)

            return {"image_paths": image_paths, "base64_images": base64_images}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating image: {str(e)}"
            )

    @router.get("/")
    async def root():
        """API root endpoint with basic information"""
        return {
            "name": "Amazon Nova Canvas API",
            "version": "1.0.0",
            "endpoints": [
                {
                    "path": "/text-to-image",
                    "method": "POST",
                    "description": "Generate images based on text prompts",
                },
                {
                    "path": "/text-image",
                    "method": "POST",
                    "description": "Generate images based on a design draft",
                },
            ],
        }

    return router
