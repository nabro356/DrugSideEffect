import pickle
import cv2
import graphviz as graphviz
import pytesseract
import openai
import requests
import json
import random
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


        print(f"Given the symptoms, We are provide remedies and medication suggestions.")
        combined_remedies = [
            "Stay hydrated by drinking plenty of water throughout the day to support overall health and well-being.",
            "Eat a balanced diet rich in fruits, vegetables, whole grains, lean proteins, and healthy fats to provide essential nutrients and promote optimal functioning of the body.",
            "Get regular exercise to improve cardiovascular health, strengthen muscles, boost mood, and reduce the risk of chronic diseases.",
            "Practice stress-reducing activities such as deep breathing, meditation, yoga, or tai chi to promote relaxation and improve mental health.",
            "Ensure adequate sleep by maintaining a consistent sleep schedule, creating a relaxing bedtime routine, and optimizing sleep environment.",
            "Limit intake of processed foods, sugary snacks, and beverages high in added sugars to prevent weight gain and support metabolic health.",
            "Avoid smoking and limit alcohol consumption to reduce the risk of developing chronic diseases and improve overall health.",
            "Practice good hygiene habits, such as washing hands regularly, covering coughs and sneezes, and avoiding close contact with sick individuals, to prevent the spread of infections.",
            "Protect skin from sun damage by wearing sunscreen, protective clothing, and seeking shade, especially during peak sun hours.",
            "Maintain regular dental hygiene by brushing teeth twice a day, flossing daily, and scheduling regular dental check-ups to prevent tooth decay and gum disease.",
            "Stay mentally active by engaging in activities that challenge the brain, such as puzzles, reading, learning new skills, or socializing with others.",
            "Seek regular medical check-ups and screenings to monitor health status, detect any potential issues early, and receive appropriate medical care and treatment.",
            "Practice safe driving habits, wear seatbelts, and avoid distractions while driving to reduce the risk of accidents and injuries.",
            "Stay connected with friends, family, and community to foster social support, reduce feelings of loneliness, and promote emotional well-being.",
            "Practice proper lifting techniques, use ergonomic equipment, and take breaks to avoid musculoskeletal injuries and strain.",
            "Create a supportive work environment by setting realistic goals, prioritizing tasks, and seeking help when needed to manage stress and prevent burnout.",
            "Practice mindfulness and gratitude by focusing on the present moment, acknowledging blessings, and expressing appreciation for life's experiences.",
            "Engage in activities that bring joy and fulfillment, such as hobbies, creative pursuits, or spending time in nature, to nourish the soul and enhance overall well-being.",
            "Prioritize self-care by setting boundaries, saying no when necessary, and taking time for oneself to recharge and replenish energy levels.",
            "Seek professional help and support from mental health professionals, counselors, or support groups if experiencing emotional or psychological challenges.",
            "Practice environmental stewardship by reducing waste, conserving resources, and supporting sustainability initiatives to protect the planet and future generations.",
            "Take regular breaks during prolonged periods of sitting or screen time to prevent fatigue, stiffness, and postural issues.",
            "Practice proper hand hygiene by washing hands with soap and water for at least 20 seconds, especially before eating or touching the face.",
            "Limit exposure to environmental pollutants and toxins by choosing natural and organic products, avoiding smoking or secondhand smoke, and using air purifiers if necessary.",
            "Engage in relaxation techniques such as progressive muscle relaxation, guided imagery, or biofeedback to reduce muscle tension, promote relaxation, and alleviate stress.",
            "Use over-the-counter or prescription medications as directed by a healthcare professional to manage symptoms of acute conditions or chronic diseases.",
            "Incorporate mindfulness-based practices such as mindfulness meditation, body scan, or mindful eating to cultivate awareness, reduce stress, and enhance well-being.",
            "Participate in regular health screenings and preventive healthcare measures, including vaccinations, cancer screenings, and cholesterol checks, to maintain optimal health.",
            "Practice proper posture and ergonomics in daily activities such as sitting, standing, and lifting to prevent musculoskeletal strain and promote spinal health.",
            "Engage in regular cardiovascular exercise such as walking, jogging, swimming, or cycling to strengthen the heart, improve circulation, and enhance cardiovascular health.",
            "Incorporate relaxation techniques such as deep breathing exercises, progressive muscle relaxation, or visualization to reduce anxiety, tension, and promote restful sleep.",
            "Use natural remedies such as herbal teas, essential oils, or aromatherapy to alleviate common ailments such as headaches, nausea, or indigestion.",
            "Seek social support from friends, family, or support groups to cope with life's challenges, share experiences, and foster a sense of belonging and connection.",
            "Practice time management strategies such as prioritizing tasks, setting goals, and breaking projects into smaller, manageable steps to reduce stress and increase productivity.",
            "Engage in regular stretching exercises to improve flexibility, prevent muscle stiffness, and reduce the risk of injury during physical activities.",
            "Use relaxation techniques such as progressive muscle relaxation, guided imagery, or meditation to reduce stress, promote relaxation, and improve overall well-being.",
            "Seek professional help from healthcare providers, therapists, or counselors if experiencing persistent or severe symptoms of mental health conditions such as depression or anxiety.",
            "Maintain a healthy work-life balance by setting boundaries, scheduling regular breaks, and prioritizing self-care activities to prevent burnout and maintain overall well-being.",
            "Incorporate mindfulness-based practices such as mindful breathing, body scan, or mindful walking into daily routines to cultivate present-moment awareness and reduce stress.",
            "Stay informed about current health guidelines, recommendations, and best practices to protect yourself and others from infectious diseases and public health threats.",
            "Practice gratitude by keeping a gratitude journal, expressing appreciation for small blessings, and focusing on positive aspects of life to promote emotional well-being.",
            "Engage in regular physical activity such as walking, jogging, cycling, or dancing to improve mood, reduce stress, and enhance overall quality of life.",
            "Practice relaxation techniques such as deep breathing, progressive muscle relaxation, or visualization to reduce stress, promote relaxation, and improve sleep quality.",
            "Seek emotional support from friends, family, or mental health professionals if experiencing feelings of loneliness, sadness, or anxiety.",
            "Engage in activities that promote social connection and community involvement, such as volunteering, joining clubs, or participating in group activities, to foster a sense of belonging and purpose."
        ]

        selected_remedies = random.sample(combined_remedies, 4)

        # Print the selected remedies
        print("Randomly Selected Remedies:")
        for index, remedy in enumerate(selected_remedies, start=1):
            print(f"{index}. {remedy}")

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
