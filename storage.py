import base64
import requests
import json


def get_s3_object(s3, bucket_name, object_key):
    """
    Fetch an object from S3 and return its content.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key of the object in the S3 bucket.

    Returns:
        str: The content of the S3 object.
    """
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    content = response["Body"].read().decode("utf-8")
    return json.loads(content)


def get_image_urls(product_data):
    """
    Extract image URLs from product data.

    Args:
        product_data (dict): The product data containing image URLs.

    Returns:
        list: List of image URLs.
    """
    return product_data[0].get("image_urls", [])


def download_images_to_base64(image_urls, with_data_uri=False):
    """
    Download images from a list of URLs, convert them to base64, and return a list of base64 strings.

    Args:
        image_urls (list): List of image URLs.
        with_data_uri (bool): Whether to include MIME type prefix (useful for HTML embedding).

    Returns:
        list: List of base64-encoded image strings (or data URIs if with_data_uri=True).
    """
    base64_list = []

    for url in image_urls:
        try:
            # Download the image
            response = requests.get(url)
            response.raise_for_status()  # Raise exception if download failed

            # Encode image content to base64
            encoded_string = base64.b64encode(response.content).decode("utf-8")

            if with_data_uri:
                # Try to detect the MIME type from the response header
                mime_type = response.headers.get(
                    "Content-Type", "application/octet-stream"
                )
                encoded_string = f"data:{mime_type};base64,{encoded_string}"

            base64_list.append(encoded_string)

        except Exception as e:
            print(f"Error downloading or encoding image from {url}: {e}")
            # Add None if failed, or you can choose to skip
            base64_list.append(None)

    return base64_list


def get_images(s3, object_key):

    bucket_name = "cm-product-2025"
    product_data = get_s3_object(s3, bucket_name, object_key)
    image_urls = get_image_urls(product_data)
    base64_images = download_images_to_base64(image_urls, with_data_uri=True)
    return base64_images
