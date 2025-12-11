from PIL import Image
import os
from werkzeug.utils import secure_filename

def resize_image(image_path, max_width=800, max_height=600, quality=85):
    """
    Resize an image to fit within specified dimensions while maintaining aspect ratio
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate new dimensions
            width, height = img.size
            if width > max_width or height > max_height:
                # Calculate scaling factor
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save the resized image
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        print(f"Error resizing image: {e}")
        return False

def optimize_image_upload(file, upload_folder, filename):
    """
    Process uploaded image file - resize and optimize
    """
    try:
        # Save the file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Resize and optimize the image
        resize_image(filepath)
        
        return True
    except Exception as e:
        print(f"Error processing image upload: {e}")
        return False

def get_image_info(image_path):
    """
    Get basic information about an image
    """
    try:
        with Image.open(image_path) as img:
            return {
                'width': img.size[0],
                'height': img.size[1],
                'format': img.format,
                'mode': img.mode,
                'size_kb': os.path.getsize(image_path) / 1024
            }
    except Exception as e:
        print(f"Error getting image info: {e}")
        return None 