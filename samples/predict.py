import pathlib
import pickle
import tarfile
import urllib

import cv2
import pytesseract
import streamlit as st
import tensorflow as tf
from PIL import Image


class PostProcess:
    def __init__(self) -> None:
        self.dn = self.load_dn()
        self.se = self.load_se()

    def load_dn(self):
        text = pathlib.Path("drug_name_labelmap.csv").read_text()
        lines = text.split("\n")[1:-1]
        return tf.io.decode_csv(lines, [str(), str()])

    def load_se(self):
        text = pathlib.Path("se_labelmap.csv").read_text()
        lines = text.split("\n")[1:-1]
        return tf.io.decode_csv(lines, [str(), str(), str()])

    def predict(self, x):
        x = x[0]
        x = str(x)
        x = "'" + x + "'"
        i = 0
        flag = False
        for name in self.dn[1].numpy():
            if name.decode("UTF-8") == x:
                flag = True
                id = self.dn[0][i].numpy().decode("UTF-8")
            i += 1
        if not flag:
            return "OOD"
        i = 0
        out = []
        id = id[:-1]
        id = id[1:]
        for ses in self.se[0].numpy():
            if ses.decode("UTF-8") == id:
                out.append(self.se[2][i].numpy().decode("UTF-8"))
            i += 1
        if out:
            return out[:5]
        else:
            return "OOD"


def load_model():
    if "model" not in st.session_state:
        urllib.request.urlretrieve(
            "https://github.com/Rishit-dagli/DygnosTech/releases/download/weights/model.tar.gz",
        )
        file = tarfile.open("serialized.tar.gz")
        file.extractall("./")
        file.close()

        with open("serialized", "rb") as f:
            st.session_state["model"] = pickle.load(f)
    return st.session_state["model"]


def predict(drug_name):
    return load_model().predict(drug_name)


"""def ocr(file):
    def get_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img = Image.open(file)
    del file
    img = img.save("img.jpg")
    img = cv2.imread("img.jpg")
    custom_config = r"--oem 1 --psm 6"
    a = pytesseract.image_to_string(get_grayscale(img), config=custom_config).split(
        "\n"
    )
    for i in a:
        if i.startswith("Drugs"):
            drugs = i
    pos = 0
    for i in drugs:
        if i == "-":
            drugs = drugs[pos + 1 :]
        pos += 1
    drugs = drugs.lower().split(",")
    drugs_updated = []
    for i in drugs:
        drugs_updated.append(i.strip())
    return drugs_updated"""

def ocr(file):
    def get_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    try:
        with Image.open(image_file) as img:
            # Convert image to RGB mode
            rgb_image = img.convert("RGB")

            # Save the RGB image as JPEG
            rgb_image.save("img.jpg")

        img = cv2.imread("img.jpg")

        custom_config = r"--oem 1 --psm 6"
        ocr_text = pytesseract.image_to_string(get_grayscale(img), config=custom_config)

        drugs_updated = []
        drugs_line = next((line for line in ocr_text.split("\n") if line.startswith("Drugs")), None)
        if drugs_line:
            drugs = drugs_line.split("-")[1].lower().split(",")
            for drug in drugs:
                drugs_updated.append(drug.strip())
        return drugs_updated
    except Exception as e:
        st.error(f"Error performing OCR: {e}")
        return []

"""def ocr(image_path):
    try:
        # Read the image using OpenCV
        img = cv2.imread(image_path)
        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Use Tesseract to do OCR on the grayscale image
        text=[]
        text = pytesseract.image_to_string(gray)
        return text
    except Exception as e:
        print("Error occurred:", e)
        return []"""

"""def ocr(file):
    # Open the image file
    with Image.open(image_path) as img:
        # Use pytesseract to do OCR on the image
        text = pytesseract.image_to_string(img)

        # Split the text into words
        words = text.split()

        return words"""

import requests

def get_remedies_for_symptoms(symptoms, api_key):
    """
    Get remedies for symptoms using OpenAI API.

    Args:
    symptoms (list): List of symptoms.
    api_key (str): OpenAI API key.

    Returns:
    str: Remedies suggested by OpenAI.
    """
    # Flatten the list of lists into a single list of symptoms
    flat_symptoms = [item for sublist in symptoms for item in sublist]
    
    prompt = f"Given the symptoms {', '.join(flat_symptoms)}, provide remedies and medication suggestions."
    
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "model": "text-davinci-turbo",  # Use the GPT-Turbo model
        "max_tokens": 100,
        "temperature": 0.5,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop": ["\n"]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    # Check if the response contains the generated text
    if "choices" in data and data["choices"]:
        completion_text = data["choices"][0]["text"].strip()
        return completion_text
    else:
        return "No remedies found."


remedies = get_remedies_for_symptoms(symptoms_list)
print("Remedies:", remedies)


