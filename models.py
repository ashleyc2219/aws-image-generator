from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class QualityEnum(str, Enum):
    standard = "standard"
    premium = "premium"


class TaskTypeEnum(str, Enum):
    TEXT_IMAGE = "TEXT_IMAGE"
    BACKGROUND_REMOVAL = "BACKGROUND_REMOVAL"
    IMAGE_VARIATION = "IMAGE_VARIATION"
    INPAINTING = "INPAINTING"
    OUTPAINTING = "OUTPAINTING"
    # Add other task types here as needed: INPAINTING, OUTPAINTING, etc.


class ControlModeEnum(str, Enum):
    CANNY_EDGE = "CANNY_EDGE"
    SEGMENTATION = "SEGMENTATION"


class ImageGenerationConfig(BaseModel):
    numberOfImages: int = Field(
        1, ge=1, le=5, description="Number of images to generate, up to 5"
    )
    width: int = Field(
        1024, ge=320, le=4096, description="Image width, must be divisible by 16"
    )
    height: int = Field(
        1024, ge=320, le=4096, description="Image height, must be divisible by 16"
    )
    cfgScale: float = Field(
        6.5, ge=1.1, le=10, description="How closely the prompt will be followed"
    )
    seed: Optional[int] = Field(
        0, ge=0, le=858993459, description="Seed for reproducibility"
    )
    quality: QualityEnum = QualityEnum.premium


class TextImageParams(BaseModel):
    text: str = Field(
        ..., min_length=1, description="Text prompt describing the image to generate"
    )
    conditionImage: str = Field(
        None, description="Base64-encoded reference image to condition generation"
    )
    controlMode: ControlModeEnum = Field(
        None,
        description="Method to analyze the reference image: edge detection or segmentation",
    )
    controlStrength: float = Field(
        None,
        ge=0.2,
        le=1.0,
        description="How strongly the reference image influences the output (0.2-1.0)",
    )


class BackgroundRemovalParams(BaseModel):
    image: str = Field(
        None, description="Base64-encoded reference image to condition generation"
    )


class ImageVariationParams(BaseModel):
    text: str = Field(..., description="Text prompt for image generation")
    images: List[str] = Field(..., description="Base64 encoded reference images")
    similarityStrength: float = Field(
        0.8,
        ge=0.2,
        le=1.0,
        description="How strongly the input images influence the output. From 0.2 through 1.",
    )


class InPaintingParams(BaseModel):
    text: str = Field(
        ..., min_length=1, description="Text prompt describing the image to generate"
    )
    negativeText: str = Field(
        None, description="What to avoid generating inside the mask"
    )
    image: str = Field(
        ...,
        description="image to edit, base64 encoded. The image must be in the same size as the mask.",
    )
    maskPrompt: str = Field(
        None,
        description="A description of the area(s) of the image to change. The mask must be in the same size as the image.",
    )
    maskImage: str = Field(
        None,
        description="A mask image that indicates the area(s) of the image to change. The mask must be in the same size as the image.",
    )


class ImageVariationRequest(BaseModel):
    imageVariationParams: ImageVariationParams
    imageGenerationConfig: ImageGenerationConfig


class TextImageRequest(BaseModel):
    textImageParams: TextImageParams
    imageGenerationConfig: ImageGenerationConfig = ImageGenerationConfig()


class BackgroundRemovalRequest(BaseModel):
    taskType: TaskTypeEnum = TaskTypeEnum.BACKGROUND_REMOVAL
    backgroundRemovalParams: BackgroundRemovalParams


class InPaintingRequest(BaseModel):
    taskType: TaskTypeEnum = TaskTypeEnum.INPAINTING
    inPaintingParams: InPaintingParams
    imageGenerationConfig: ImageGenerationConfig = ImageGenerationConfig()


class ImageResponse(BaseModel):
    image_paths: List[str]
    base64_images: List[str]
