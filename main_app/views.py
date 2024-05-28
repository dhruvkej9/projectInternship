from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import json
import cv2
import os

def StripDetection(image_path):
    # Load the image from your local folder
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Find contours and select the one corresponding to the strip
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    strip_contour = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = h / w
        if aspect_ratio > 5:  # Assuming the strip is much taller than it is wide
            strip_contour = contour
            break

    if strip_contour is None:
        raise ValueError("Could not find the strip in the image")

    # Crop the strip from the image
    x, y, w, h = cv2.boundingRect(strip_contour)
    strip_img = img[y:y+h, x:x+w]

    # Define regions of interest (ROI) for each color pad
    num_pads = 10
    pad_height = h // num_pads

    strip_coordinates = {
        'URO': (0, 0*pad_height, w, 1*pad_height),
        'BIL': (0, 1*pad_height, w, 2*pad_height),
        'KET': (0, 2*pad_height, w, 3*pad_height),
        'BLD': (0, 3*pad_height, w, 4*pad_height),
        'PRO': (0, 4*pad_height, w, 5*pad_height),
        'NIT': (0, 5*pad_height, w, 6*pad_height),
        'LEU': (0, 6*pad_height, w, 7*pad_height),
        'GLU': (0, 7*pad_height, w, 8*pad_height),
        'SG': (0, 8*pad_height, w, 9*pad_height),
        'PH': (0, 9*pad_height, w, 10*pad_height)
    }

    # Extract and average the color values from each region
    results = {}
    for key, (x1, y1, x2, y2) in strip_coordinates.items():
        roi = strip_img[y1:y2, x1:x2]
        if roi.size == 0:
            avg_color = [0, 0, 0]
        else:
            avg_color = np.mean(roi, axis=(0, 1)).astype(int).tolist()
        results[key] = avg_color

    # Convert the results to JSON
    results_json = json.dumps(results, indent=4)

    os.remove(image_path)
    return results_json


def index(request):
    context = {
        "var": 9
    }
    return render(request, 'index.html', context)

@csrf_exempt
def upload_urine_strip(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['urine_strip']
        # Process the uploaded file as needed
        # For example, save the file to the media directory
        with open('media/' + uploaded_file.name, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        context = {
            "message": "File uploaded successfully!",
            "result": {}
        }
        context["result"] = StripDetection('media/' + uploaded_file.name)
        return render(request, 'index.html', context)
    return render(request, 'index.html')
