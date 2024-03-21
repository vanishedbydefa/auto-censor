import os

from PIL import Image
from nudenet import NudeDetector


def find_nudity(image_path):
    nude_detector = NudeDetector()
    return nude_detector.detect(image_path) # Returns list of detections

def is_image(file_path, filename):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', ".svg")):
        return False
    try:
        with Image.open(file_path):
            return True
    except (IOError, OSError):
        return False

def get_files(path:str, recursive=False):
    images = []
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
    
        # Check if it's a file (not a directory)
        if is_image(file_path, filename):
            images.append([file_path, filename])
        if recursive and os.path.isdir(file_path):
            more_images = get_files(file_path, recursive=recursive)
            for img in more_images:
                images.append(img)
    return images