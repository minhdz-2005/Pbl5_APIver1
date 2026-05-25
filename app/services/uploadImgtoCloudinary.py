import cloudinary.uploader
from typing import Dict, Any
from app.core.cloudinary import cloudinary  # Ensure cloudinary is configured


async def upload_image_to_cloudinary(
    image_url: str,
    generated_design_id: str
) -> Dict[str, Any]:
    """
    Upload an image to Cloudinary from a URL.
    
    Args:
        image_url (str): The URL of the image to upload
        generated_design_id (str): The ID of the generated design
    
    Returns:
        Dict containing:
            - design_id (str): The generated design ID
            - cloudinary_url (str): The URL of the uploaded image on Cloudinary
            - public_id (str): The public ID of the resource on Cloudinary
    
    Raises:
        Exception: If upload fails
    """
    try:
        # Upload image to Cloudinary from URL
        upload_result = cloudinary.uploader.upload(
            image_url,
            folder=f"pbl5/generated_designs/{generated_design_id}",
            resource_type="auto",
            quality="auto",
            fetch_format="auto"
        )
        
        # Return the design ID and Cloudinary URL
        return {
            "design_id": generated_design_id,
            "cloudinary_url": upload_result.get("secure_url"),
            "public_id": upload_result.get("public_id")
        }
    
    except Exception as e:
        raise Exception(f"Failed to upload image to Cloudinary: {str(e)}")
