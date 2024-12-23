import json
import os
import random
import re
import tempfile

import streamlit as st
from google import genai
from google.genai import Client
from google.genai import types
from PIL import Image, ImageColor, ImageDraw, ImageFont

def call_llm(img: Image, prompt: str) -> str:
    system_prompt = """
    Return bounding boxes as a JSON array with labels. Never return masks or code fencing. Limit to 25 objects.
    If an object is present multiple times, name them according to their unique characteristic (colors, size, position, unique characteristics, etc.).
    Output a JSON list where each entry contains the bounding box in "box_2d" and a text label in "label".
    """

    client = Client(api_key="GEMINI API KEY")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt, img],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.5,
            safety_settings=[types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH")],
        ),
    )

    print("Response from LLM:", response)
    return response.text

def parse_json(json_input: str) -> str:
    # Remove triple backticks and `json` marker
    clean_json = re.sub(r'```json\n|\n```', '', json_input.strip())
    
    # Verify JSON structure
    try:
        json.loads(clean_json)  # Test if it's valid JSON
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        print("Cleaned JSON:", clean_json)
        return "[]"  # Return an empty list if parsing fails

    return clean_json

def plot_bounding_boxes(img: Image, bounding_boxes: str) -> Image:
    width, height = img.size
    colors = list(ImageColor.colormap.keys())
    draw = ImageDraw.Draw(img)

    # Parse JSON
    bounding_boxes = parse_json(bounding_boxes)

    try:
        bounding_boxes = json.loads(bounding_boxes)
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        print("Input JSON:", bounding_boxes)
        return img  # Return the original image if JSON is invalid

    # Debugging: Log the cleaned bounding boxes JSON
    print("Cleaned JSON for bounding boxes:", bounding_boxes)

    for bounding_box in bounding_boxes:
        color = random.choice(colors)

        # Convert normalized coordinates to absolute coordinates
        abs_y1 = int(bounding_box["box_2d"][0] / 1000 * height)
        abs_x1 = int(bounding_box["box_2d"][1] / 1000 * width)
        abs_y2 = int(bounding_box["box_2d"][2] / 1000 * height)
        abs_x2 = int(bounding_box["box_2d"][3] / 1000 * width)

        # Correct order of coordinates if necessary
        abs_x1, abs_x2 = min(abs_x1, abs_x2), max(abs_x1, abs_x2)
        abs_y1, abs_y2 = min(abs_y1, abs_y2), max(abs_y1, abs_y2)

        # Debugging: Output the absolute coordinates and label
        print(f"Absolute Coordinates: {bounding_box['label']}, {abs_y1}, {abs_x1}, {abs_y2}, {abs_x2}")

        # Draw rectangle for bounding box
        draw.rectangle(((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=4)

        # Draw label text
        try:
            font = ImageFont.truetype("Arial.ttf", size=14)
        except IOError:
            font = ImageFont.load_default()

        draw.text(
            (abs_x1 + 8, abs_y1 + 6),
            bounding_box["label"],
            fill=color,
            font=font,
        )

    return img

# Set up the Streamlit app
if __name__ == "__main__":
    st.set_page_config(page_title="Gemini 2.0 Spatial Reference")
    st.header("Gemini 2.0 Spatial Reference")

    with st.sidebar:
        uploaded_image = st.file_uploader(
            "Upload your image here:", type=["jpg", "jpeg", "png"], accept_multiple_files=False
        )

    prompt = st.text_input("Enter your prompt")
    run = st.button("Run!")

    if uploaded_image and prompt and run:
        temp_file = tempfile.NamedTemporaryFile(
            "wb", suffix=f".{uploaded_image.type.split('/')[-1]}", delete=False
        )
        temp_file.write(uploaded_image.getbuffer())
        image_path = temp_file.name

        img = Image.open(image_path)
        width, height = img.size
        resized_image = img.resize(
            (1024, int(1024 * height / width)), Image.Resampling.LANCZOS
        )

        os.unlink(image_path)
        print(
            f"Image Original Size: {img.size} | Resized Image Size: {resized_image.size}"
        )

        with st.spinner("Running...."):
            response = call_llm(resized_image, prompt)
            plotted_image = plot_bounding_boxes(resized_image, response)

        st.image(plotted_image, caption="Image with Bounding Boxes")

