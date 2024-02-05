from flask import Flask, render_template, request, redirect, url_for
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output_images'  # New folder for processed images

# Function to process the uploaded image
def process_image(file_path):
    # Read the image using OpenCV
    image = cv2.imread(file_path)

    # Detect common objects in the image using cvlib
    bbox, label, conf = cv.detect_common_objects(image)

    # Get the count of detected objects
    object_count = len(label)

    # Draw bounding boxes on the image
    output_image = draw_bbox(image, bbox, label, conf)

    # Save the processed image to the output folder
    output_folder = app.config['OUTPUT_FOLDER']
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_path = os.path.join(output_folder, 'output_image.jpg')
    cv2.imwrite(output_path, output_image)

    # Return the path to the processed image and the count of detected objects
    return output_path, object_count


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/input')
def input():
    return render_template('inner-page.html')

# Define the process route for handling image uploads and processing
@app.route('/process', methods=['POST'])
def process():
    # Check if 'image' is present in the request files
    if 'image' not in request.files:
        return redirect(url_for('home'))

    # Get the uploaded image file
    file = request.files['image']

    # Check if the filename is empty
    if file.filename == '':
        return redirect(url_for('home'))

    # If the file is valid, save it to the upload folder
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the uploaded image and get the output path and object count
        output_path, object_count = process_image(file_path)

        # Create paths for displaying images in the template
        original_image_path = os.path.relpath(file_path, 'static')
        processed_image_path = os.path.relpath(output_path, 'static')

        # Render the template with original and processed image paths, and object count
        return render_template('portfolio-details.html', original_image=original_image_path, processed_image=processed_image_path, object_count=object_count)

if __name__ == '__main__':
    app.run(debug=True,port = 5000)
