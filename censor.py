from PIL import Image, ImageDraw, ImageFilter, ImageFont

def draw_rectangle(image_path, x, y, width, height, color="black", overwrite=False):
    # Open the image
    img = Image.open(image_path)

    # Convert image to RGB mode
    img = img.convert("RGB")

    # Create Drawing Object
    draw = ImageDraw.Draw(img)

    # Define the coordinates of the rectangle
    upper_left = (x, y)
    lower_right = (x + width, y + height)

    # Draw a rectangle
    draw.rectangle([upper_left, lower_right], fill=color)

    # Save the modified image
    img.save(image_path)

def draw_rectangle_with_text(image_path, x, y, width, height, color="black", text="BLACKED", text_color="white", font=None, fontsize=12):
    # Open the image
    img = Image.open(image_path)

    # Convert image to RGB mode
    img = img.convert("RGB")

    # Create Drawing Object
    draw = ImageDraw.Draw(img)

    # Define the coordinates of the rectangle
    upper_left = (x, y)
    lower_right = (x + width, y + height)

    # Draw a rectangle
    draw.rectangle([upper_left, lower_right], fill=color)

    # Define text position
    text_x = x + width / 2
    text_y = y + height / 2

    # Set default font if not provided
    if font is None:
        font = ImageFont.load_default()
    else:
        # Dynamically calculate fontsize based on width and height
        fontsize = int(min(width, height) * 0.5)  # 20% of the smaller dimension
        font = ImageFont.truetype(ImageFont.load_default(), fontsize)  # Create the font with calculated size

    # Draw text
    fontsize = min(width, height) * 0.5  # 20% of the smaller dimension

    print(fontsize)
    draw.text((text_x, text_y), text, fill=text_color, font=font, anchor="mm", fontsize=fontsize)

    # Save the modified image
    img.save(image_path)


def blur_region(image_path, x, y, width, height, blur_radius=30, overwrite=False):
    # Open the image
    img = Image.open(image_path)

    # Define the region to blur
    region = img.crop((x, y, x + width, y + height))

    # Apply blur filter to the region
    blurred_region = region.filter(ImageFilter.GaussianBlur(blur_radius))

    # Paste the blurred region back onto the original image
    img.paste(blurred_region, (x, y))

    # Save the modified image
    img.save(image_path)


def mosaic_region(image_path, x, y, width, height, mosaic_size=10, overwrite=False):
    # Open the image
    img = Image.open(image_path)

    # Define the region to apply mosaic effect
    region = img.crop((x, y, x + width, y + height))

    # Resize the region to a small size
    small_region = region.resize((int(width / mosaic_size), int(height / mosaic_size)), Image.NEAREST)

    # Resize the small region back to its original size
    mosaic_region = small_region.resize(region.size, Image.NEAREST)

    # Paste the mosaic region back onto the original image
    img.paste(mosaic_region, (x, y))

    # Save the modified image
    img.save(image_path)
