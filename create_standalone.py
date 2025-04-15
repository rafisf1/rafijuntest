import base64
import os

def image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded_string}"

# Read the original HTML file
with open('index.html', 'r') as file:
    html_content = file.read()

# Get all images from the folder
image_folder = 'images anvi test2'
image_files = [
    'image1.JPG', 'image2.JPG', 'image3.JPG', 'image4.JPG', 'image5.JPG',
    'image6.JPG', 'image7.JPG', 'image8.JPG', 'image9.JPG', 'image10.jpg',
    'image11.JPG', 'image12.JPEG'
]

# Create the images array with base64 data
images_array = []
for i, image_file in enumerate(image_files, 1):
    image_path = os.path.join(image_folder, image_file)
    if os.path.exists(image_path):
        base64_data = image_to_base64(image_path)
        images_array.append(f"{{ id: {i}, url: '{base64_data}', rating: 1200 }}")

# Replace the IMAGES array in the HTML
images_array_str = "let IMAGES = [\n    " + ",\n    ".join(images_array) + "\n];"
html_content = html_content.replace("let IMAGES = [", images_array_str)

# Write the new HTML file
with open('index_standalone.html', 'w') as file:
    file.write(html_content)

print("Standalone version created successfully!") 