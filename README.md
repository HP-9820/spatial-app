# Gemini 2.0 Spatial Reference

This project uses **Google Gemini 2.0** to identify objects in images and plot bounding boxes with labels. Built as a **Streamlit** web app, it allows users to upload an image, input a prompt, and visualize bounding boxes with labels overlaid on the image.

### Key Features:
- Object detection with **Gemini 2.0** API
- Bounding box plotting with labels
- Interactive **Streamlit** interface

---

## Installation

### Requirements:
- Python 3.x
- Install dependencies:
  ```bash
  pip install -r requirements.txt
## Running the App

1. **Clone the repo**:
   ```bash
   git clone https://github.com/yourusername/gemini-spatial-reference.git

Navigate to the project directory:

1. **Navigate to the project directory**:
   ```bash
   cd gemini-spatial-reference
Run the Streamlit app:


How to Use

Upload Image: Upload an image (JPG/PNG) in the sidebar.

Enter Prompt: Provide a description for object detection (e.g., "Detect all cars").

Click "Run": The app processes the image and overlays bounding boxes with labels.

## API Key Setup

1. Set up a **Google Gemini 2.0 API key**.
2. Replace the placeholder in `call_llm` with your key:
   ```python
   client = Client(api_key="YOUR_API_KEY")
Acknowledgements
1) Streamlit for the interactive app framework.
2) Google Gemini 2.0 for object detection.
3) Pillow for image processing.
