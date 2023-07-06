from uuid import uuid4
from PIL import Image
import io


def compress_and_resize(image, size_limit=200, ratio='1:1'):
    # Open the image using Pillow
    img = Image.open(image)
    img = img.convert("RGB")
    # Set the compression quality
    quality = 80
    # Determine the original dimensions of the image
    original_width, original_height = img.size
    # Determine the target dimensions based on the aspect ratio
    if ratio == '1:1':
        target_width = min(original_width, original_height)
        target_height = target_width
    elif ratio == '16:9':
        target_width = min(original_width, int(original_height * 16 / 9))
        target_height = min(original_height, int(original_width * 9 / 16))
    else:
        raise ValueError('Invalid aspect ratio')

    # Resize the image to the target dimensions
    img = img.resize((target_width, target_height), Image.ANTIALIAS)
    # Create a buffer to store the compressed image
    buffer = io.BytesIO()

    # Compress the image using Pillow and save it to the buffer
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    # Determine the file size of the compressed image
    file_size = buffer.tell()
    # If the file size is larger than the size limit, reduce the compression quality and try again
    while file_size > size_limit * 1000 and quality>=50:
        print(file_size)
        quality -= 10
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        file_size = buffer.tell()

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Return the compressed image as a byte string
    return buffer.getvalue()


def generate_unique_filename(filename):
    unique_name = uuid4().hex
    extension = filename.split('.')[-1]
    return f"{unique_name}.{extension}"