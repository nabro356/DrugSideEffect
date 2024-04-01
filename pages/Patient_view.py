import pickle
import cv2
import graphviz as graphviz
import pytesseract
import openai
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
# st.markdown(
#     f'<h1 style="color:#000000;font-size:24px;">{"Witness the magic by simply uploading an image below and let our model do the talking."}</h1>',
#     unsafe_allow_html=True,
# )
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
            
def get_remedies(symptoms):
    """
    Generate remedies and medication suggestions from OpenAI API based on symptoms.

    Args:
    symptoms (list): List of symptoms.

    Returns:
    None
    """
    openai.api_key = st.secrets["OPENAI_API_KEY"]  # Assuming you've stored your OpenAI API key as a Streamlit secret
    prompt = f"Given the symptoms {', '.join(symptoms)}, provide remedies and medication suggestions."
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.5,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"]
    )
    remedies = response.choices[0].text.strip()
    # Perform any necessary actions with the generated remedies
    print("Remedies and medication suggestions:", remedies)


with open("pages/serialized", "rb") as f:
    model = pickle.load(f)


if file is None:
    pass
else:
    drugs = ocr(file)
    dictionary = {}
    for i in drugs:
        dictionary[i] = model.predict([i])
    graph = graphviz.Digraph(format="dot")
    graph.graph_attr["rankdir"] = "LR"
    graph.graph_attr["bgcolor"] = "#00000000"

    for k in dictionary:
        graph.edge("Alex", k)
        for i in dictionary[k]:
            graph.edge(k, i)

    st.graphviz_chart(graph)

    st.markdown(
        f'<h1 style="color:#000000;font-size:18px;">{"Mobile number, to receive a summary:"}</h1>',
        unsafe_allow_html=True,
    )

    txt = st.text_input("")

    def get_remedies_from_symptoms_dict(symptoms_dict):
    """
    Get remedies and medication suggestions from OpenAI API based on symptoms provided in a dictionary.
    Args:
    symptoms_dict (dict): Dictionary where values are lists of symptoms.
    Returns:
    dict: Dictionary mapping symptoms to remedies and medication suggestions.
    """
    # Extract all symptoms from the dictionary values and convert them into a single list
    all_symptoms = [symptom for symptoms_list in symptoms_dict.values() for symptom in symptoms_list]
    # Call the original get_remedies function with the combined list of symptoms
    remedies = get_remedies(all_symptoms)
    # Return the remedies
    return remedies

    remedies = get_remedies_from_symptoms_dict(symptoms_dict)

    get_remedies(remedies)

    if st.button("Send Summary"):
        # check that txt contains a valid phone number
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
