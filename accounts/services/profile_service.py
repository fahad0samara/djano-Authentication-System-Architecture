from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

class ProfileService:
    @staticmethod
    def process_profile_picture(image_file, max_size=(300, 300)):
        """Process and optimize profile pictures."""
        if not image_file:
            return None
            
        # Open image and convert to RGB
        image = Image.open(image_file)
        image = image.convert('RGB')
        
        # Resize maintaining aspect ratio
        image.thumbnail(max_size)
        
        # Save optimized image
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=85, optimize=True)
        
        # Generate unique filename
        filename = f"profile_{image_file.name}"
        path = f"profile_pics/{filename}"
        
        # Save to storage
        default_storage.save(path, ContentFile(buffer.getvalue()))
        return path