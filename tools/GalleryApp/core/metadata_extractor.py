import os
from PIL import Image
from PIL.ExifTags import TAGS

class MetadataExtractor:
    def extract(self, file_path):
        metadata = {}

        # Basic file info
        metadata["file_path"] = file_path
        metadata["file_name"] = os.path.basename(file_path)
        metadata["file_size"] = os.path.getsize(file_path)

        # Image resolution + EXIF
        try:
            with Image.open(file_path) as img:
                metadata["width"], metadata["height"] = img.size

                # Extract EXIF if available
                exif_data = img.getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        metadata[tag] = value
        except Exception as e:
            metadata["error"] = str(e)

        return metadata
