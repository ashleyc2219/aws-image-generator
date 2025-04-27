import json
import numpy as np
from fastapi import APIRouter, HTTPException
from models import (
    ImageResponse,
    TextImageRequest,
    TaskTypeEnum,
    BackgroundRemovalRequest,
    ImageVariationRequest,
    InPaintingRequest,
)
from utils import save_image
import base64
from prompt import GenerateImagePrePrompt, SearchPrePrompt
from storage import get_images


router = APIRouter()

image_pre_prompt = "For helping you comprehensive understand the prompt, you could assume that input vocabularies are all about a computer. For example, the case could refer to computer case, the cooler could refer to computer cooler."


def create_router(config):
    bedrock_client = config["bedrock_client"]
    image_model = config["image_model"]
    output_dir = config["output_dir"]
    bedrock_agent = config["bedrock_agent_client"]
    s3_client = config["s3_client"]

    @router.post("/test", response_model=ImageResponse)
    async def test():
        with open("output/01-text-to-image_seed-1.png", "rb") as image_file:
            reference_image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        """Test endpoint to check if the API is working"""

        print("Generating image...")
        print("image model:", image_model)
        body = json.dumps(
            {
                "taskType": "INPAINTING",
                "inPaintingParams": {
                    "text": "a white tshirt with a oliver tree graphic",
                    "negativeText": "animal;people;green;man",
                    "maskPrompt": "dog image",
                    "image": reference_image_base64,
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "cfgScale": 6.5,
                    "seed": 0,
                    "quality": "standard",
                },
            }
        )
        with open("request_body.json", "w") as file:
            file.write(body)

        # image_generation_model_id = "amazon.nova-canvas-v1:0"
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

        return {"image_paths": image_path, "base64_images": base64_images}

    @router.post("/inpainting", response_model=ImageResponse)
    async def inpainting(request: InPaintingRequest):
        """Generate image based on references iamges(max=5)"""

        request.inPaintingParams.text = (
            f"{image_pre_prompt} {request.inPaintingParams.text}"
        )
        request.imageGenerationConfig.seed = np.random.randint(1, 1000001)
        body = json.dumps(
            {
                "taskType": TaskTypeEnum.INPAINTING,
                "inPaintingParams": request.inPaintingParams.dict(exclude_none=True),
                "imageGenerationConfig": request.imageGenerationConfig.dict(
                    exclude_none=True
                ),
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

    @router.post("/variation", response_model=ImageResponse)
    async def generate_variation(request: ImageVariationRequest):
        """Generate image based on references iamges(max=5)"""

        request.imageVariationParams.text = (
            f"{image_pre_prompt} {request.imageVariationParams.text}"
        )
        request.imageGenerationConfig.seed = np.random.randint(1, 1000001)
        body = json.dumps(
            {
                "taskType": TaskTypeEnum.IMAGE_VARIATION,
                "imageVariationParams": request.imageVariationParams.dict(),
                "imageGenerationConfig": request.imageGenerationConfig.dict(),
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

        request.textImageParams.text = (
            f"{image_pre_prompt} {request.textImageParams.text}"
        )

        request.imageGenerationConfig.seed = np.random.randint(1, 1000001)
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
            print(image_model)
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

    @router.post("/generate-prompt-optimize")
    async def generate_prompt_optimize(request: str):
        """
        Optimize the generate prompt.
        """
        # Remove extra spaces and ensure proper formatting
        text_model_id = "amazon.nova-pro-v1:0"
        system_list = [
            {
                "text": "Yor are an assistant to user improve prompt, which is used to input a image generation AI model, so you need to make sure the prompt is clear and easy to understand by AI model."
            },
            {
                "text": "For helping you comprehensive understand the prompt, you could assume that input vocabularies are all about a computer. For example, the case could refer to computer case, the cooler could refer to computer cooler."
            },
            {
                "text": "Your output should be directly used as the input of image generation AI model, so you don't need to add any extra information."
            },
        ]

        # Define one or more messages using the "user" and "assistant" roles.
        message_list = [
            {"role": "user", "content": [{"text": f"{GenerateImagePrePrompt} prompt"}]}
        ]

        # Configure the inference parameters.
        inf_params = {"maxTokens": 500, "topP": 0.9, "topK": 20, "temperature": 0.7}
        request_body = {
            "schemaVersion": "messages-v1",
            "messages": message_list,
            "system": system_list,
            "inferenceConfig": inf_params,
        }

        # Invoke the model with the response stream
        response = bedrock_client.invoke_model_with_response_stream(
            modelId=text_model_id, body=json.dumps(request_body)
        )

        stream = response.get("body")
        text = ""
        if stream:
            for event in stream:
                chunk = event.get("chunk")
                chunk_json = json.loads(chunk.get("bytes").decode())
                if "contentBlockDelta" in chunk_json:
                    delta_text = chunk_json["contentBlockDelta"]["delta"]["text"]
                    text += delta_text
        return {"original_prompt": request, "optimized_prompt": text}

    @router.post("/search-prompt-optimize")
    async def search_prompt_optimize(request: str):
        """
        Optimize the generate prompt.
        """
        # Remove extra spaces and ensure proper formatting
        text_model_id = "amazon.nova-pro-v1:0"
        system_list = [{"text": "MAKE SURE YOUR RESPONSE SHOULD UNDER 800 tokens."}]

        # Define one or more messages using the "user" and "assistant" roles.
        message_list = [
            {"role": "user", "content": [{"text": f"{SearchPrePrompt} prompt"}]}
        ]

        # Configure the inference parameters.
        inf_params = {"maxTokens": 500, "topP": 0.9, "topK": 20, "temperature": 0.7}
        request_body = {
            "schemaVersion": "messages-v1",
            "messages": message_list,
            "system": system_list,
            "inferenceConfig": inf_params,
        }

        # Invoke the model with the response stream
        response = bedrock_client.invoke_model_with_response_stream(
            modelId=text_model_id, body=json.dumps(request_body)
        )

        stream = response.get("body")
        text = ""
        if stream:
            for event in stream:
                chunk = event.get("chunk")
                chunk_json = json.loads(chunk.get("bytes").decode())
                if "contentBlockDelta" in chunk_json:
                    delta_text = chunk_json["contentBlockDelta"]["delta"]["text"]
                    text += delta_text
        text = text.replace("\n", "").replace("\\", "").replace("---", "")[:800]
        return {"original_prompt": request, "optimized_prompt": text}

    @router.post("/search")
    async def generate_prompt(request: str):
        """
        Optimized the search prompt then search the data.
        """
        try:
            # optimize the prompt
            print("optimizing prompt...")
            optimized_prompt = await search_prompt_optimize(request)
            print("optimized prompt:", optimized_prompt)
            response = bedrock_agent.retrieve(
                knowledgeBaseId="53EOF738SO",
                retrievalQuery={"text": request},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {"numberOfResults": 1}
                },
            )

            s3_locations = []
            results = []

            for result in response["retrievalResults"]:
                if "location" in result and "s3Location" in result["location"]:
                    data = dict()
                    s3_uri = result["location"]["s3Location"]["uri"]
                    iamges = get_images(
                        s3_client, s3_uri.replace("s3://cm-product-2025/", "")
                    )
                    data["image_urls"] = iamges
                    results.append(data)

            print(f"Total S3 locations found: {len(s3_locations)}")

            # Return both the original results and the extracted S3 locations
            return {
                "original_prompt": optimized_prompt["original_prompt"],
                "optimized_prompt": optimized_prompt["optimized_prompt"],
                "results": results,
                "s3_locations": s3_locations,
            }
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            raise e

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
