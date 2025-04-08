from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import io
from PIL import Image, ImageFilter, ImageOps

def apply_filter(image, filter_name):
    if filter_name == 'gray':
        # Convert image to grayscale
        image = image.convert('L')
    elif filter_name == 'sepia':
        # Apply sepia tone filter
        image = image.convert('RGB')
        width, height = image.size
        pixels = image.load()  # create the pixel map
        for py in range(height):
            for px in range(width):
                r, g, b = image.getpixel((px, py))
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
    elif filter_name == 'poster':
        # Posterize image
        image = image.convert('RGB')
        image = ImageOps.posterize(image, bits=3)
    elif filter_name == 'blur':
        # Apply a blur filter using Pillow’s built-in filter
        image = image.filter(ImageFilter.BLUR)
    elif filter_name == 'edge':
        # Apply edge detection filter
        image = image.filter(ImageFilter.FIND_EDGES)
    elif filter_name == 'solar':
        # Apply solarization effect
        image = image.convert('RGB')
        image = ImageOps.solarize(image, threshold=128)
    return image

def image_upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        filter_name = request.POST.get('filter')

        # Open the image using Pillow
        try:
            image = Image.open(uploaded_file)
        except Exception as e:
            return render(request, 'upload.html', {'error': 'Invalid image file.'})

        # Apply the selected filter
        processed_image = apply_filter(image, filter_name)

        # Save processed image to a BytesIO buffer
        buffer = io.BytesIO()
        processed_image.save(buffer, format='PNG')
        buffer.seek(0)

        # Save the image file to S3 via the default storage backend
        file_name = f'processed_{filter_name}_' + uploaded_file.name
        saved_path = default_storage.save(file_name, ContentFile(buffer.read()))
        image_url = default_storage.url(saved_path)

        return render(request, 'result.html', {'image_url': image_url})

    return render(request, 'upload.html')
