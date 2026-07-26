import os
from companion.models.sig_image import SIGImage

def ingest_screenshots(folder_path):
    images = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            full_path = os.path.join(folder_path, filename)
            images.append(SIGImage(full_path))

    return images
