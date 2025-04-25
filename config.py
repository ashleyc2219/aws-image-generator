import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv


def load_configuration():
    # Load environment variables from .env file
    load_dotenv()

    # Print environment variables for debugging
    print("========== ENVIRONMENT VARIABLES ==========")
    print(f"AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID', 'Not set')}")
    print(
        f"AWS_SECRET_ACCESS_KEY: {os.environ.get('AWS_SECRET_ACCESS_KEY', '[REDACTED]' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'Not set')}"
    )
    print(
        f"AWS_IMAGE_GENERATOR_MODEL: {os.environ.get('AWS_IMAGE_GENERATOR_MODEL', 'Not set')}"
    )
    print("==========================================")

    # Get AWS credentials from environment
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID", "example")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "example")

    print(f"Using AWS Access Key: {aws_access_key}")
    print(f"Using AWS Secret Key: {'[REDACTED]' if aws_secret_key else 'None'}")

    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize Bedrock client
    bedrock_runtime_client = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        config=Config(
            read_timeout=5 * 60,  # 5 minutes timeout
        ),
    )

    # Get image generation model from environment
    image_generation_model = os.environ.get(
        "AWS_IMAGE_GENERATOR_MODEL", "amazon.titan-image-generator-v1"
    )
    print(f"Using image generation model: {image_generation_model}")

    return {
        "bedrock_client": bedrock_runtime_client,
        "image_model": image_generation_model,
        "output_dir": output_dir,
    }
