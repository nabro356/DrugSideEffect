import pickle
import cv2
import graphviz as graphviz
import pytesseract
import openai
import requests
import json
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from twilio.rest import Client

u = "https://i.ibb.co/vm0FhBN/depositphotos-11673257-stock-photo-caduceus-medical-symbol.webp"
page_title = "Patient"

# Set page title and favicon.
st.set_page_config(page_title=page_title, page_icon=u)


def send_message(number, content):
    account_sid = "ACa708dea8b56ba9ef6951f56d75e394cf"
    auth_token = st.secrets["TWILIO_AUTH"]
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        messaging_service_sid="MG7c8d7300371ad23e00a21e84bc24926f",
        body=content,
        to=number,
    )


def add_bg_from_url():
    st.markdown(
        f"""
         <style>
         .stApp {{
             background-image: url("https://i.ibb.co/HXcJq7g/pngtree-line-light-effect-yellow-and-blue-background-image-771374.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True,
    )


add_bg_from_url()

# Read file and keep in variable
with open("pages/dtech_patient.html", "r") as f:
    html_data = f.read()

# Show in webpage
components.html(html_data, width=2000, height=150)

# Display markdown content
st.markdown(
    f'<h1 style="color:#000000;font-size:35px;">{"Prescription Upload Screen"}</h1>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<h1 style="color:#000000;font-size:18px;">{"Please upload your prescription below:"}</h1>',
    unsafe_allow_html=True,
)

file = st.file_uploader("", type=["jpg", "png"])


def ocr(file):
    """
    Perform OCR on the given image and return a list of words.
    
    Args:
    image_path (str): Path to the image file.
    
    Returns:
    list: List of words extracted from the image.
    """
    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(Image.open(file))

    # Split the text into words and add each word to a list
    words = text.split()

    return words

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
            

with open("pages/serialized", "rb") as f:
    model = pickle.load(f)



if file is None:
    pass
else:
    drugs = ocr(file)
    dictionary = {}
    for i in drugs:
        dictionary[i] = model.predict([i])
    symptoms_list = list(dictionary.values())
    graph = graphviz.Digraph(format="dot")
    graph.graph_attr["rankdir"] = "LR"
    graph.graph_attr["bgcolor"] = "#00000000"

    for k in dictionary:
        graph.edge("Ramayya", k)
        for i in dictionary[k]:
            graph.edge(k, i)

    st.graphviz_chart(graph)

    def get_remedies_for_symptoms(symptoms):
        
        # Flatten the list of lists into a single list of symptoms
        flat_symptoms = [item for sublist in symptoms for item in sublist]


        prompt = f"Given the symptoms {', '.join(flat_symptoms)}, provide remedies and medication suggestions."
    
        # Replace "YOUR_CLAUDE_API_KEY" with your actual Claude API key
        api_key = "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"
        
        url = "https://claude.ai/api/complete"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"prompt": prompt, "max_tokens": 100}
        
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
    
        # Extract the generated text from the response JSON
        if "choices" in data and data["choices"]:
            remedies = data["choices"][0]["text"].strip()
        else:
            remedies = "No remedies found."
    
        return remedies
        
    get_remedies_for_symptoms(symptoms_list)
        
    st.markdown(
        f'<h1 style="color:#000000;font-size:18px;">{"Mobile number, to receive a summary:"}</h1>',
        unsafe_allow_html=True,
    )

    txt = st.text_input("")

    if st.button("Send Summary"):
        if txt.startswith("+"):
            send_message(
                txt,
                """Dear User,Here is a summary of your prescription:
                    Having """
                + drugs[0]
                + " can cause "
                + model.predict([drugs[0]])[0],
            )
            st.success("Message sent!")
        else:
            st.markdown(
                f'<h1 style="color:#000000;font-size:18px;">{"Please enter a valid phone number"}</h1>',
                unsafe_allow_html=True,
            )

    # Get remedies for symptoms
    symptoms = [symptom for symptoms_list in dictionary.values() for symptom in symptoms_list]
    remedies = get_remedies_for_symptoms(symptoms)
    st.write("Remedies for symptoms:", remedies)
