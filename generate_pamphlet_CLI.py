import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SOURCE_TEXT = {
    # Header Section
    "__HEADER_NEED_INTERPRETER__": "I need an interpreter",
    "__HEADER_PREFERRED_LANGUAGE__": "My preferred language is",
    "__HEADER_DONT_UNDERSTAND__": "I don't understand medical information in English",
    
    # Patient Rights
    "__SECTION_PATIENT_RIGHTS__": "Patient Rights",
    "__RIGHTS_INTRO__": "You have the right to:",
    "__RIGHTS_INTERPRETATION__": "Free medical interpretation at any time during your visit",
    "__RIGHTS_REPEAT_INFO__": "Ask staff to repeat or explain information until you understand",
    "__RIGHTS_DISCHARGE__": "Receive discharge instructions in your preferred language",
    "__RIGHTS_COST_ESTIMATE__": "Request a cost estimate before treatment",
    
    # Left Column - Phrases & Info
    "__SECTION_COMMON_PHRASES__": "Common Phrases",
    "__PHRASE_DONT_UNDERSTAND__": "I don't understand.",
    "__PHRASE_IN_PAIN__": "I am in pain.",
    "__PHRASE_BATHROOM__": "Where is the bathroom?",
    "__PHRASE_SPEAK_SLOWLY__": "Please speak slowly.",
    "__PHRASE_HAVE_INTERPRETER__": "I have someone who can interpret for me.",
    
    "__SECTION_PERSONAL_INFO__": "Personal Information",
    "__FIELD_DATE_OF_BIRTH__": "Date of Birth",
    "__FIELD_BLOOD_TYPE__": "Blood Type",
    "__FIELD_PRIMARY_DOCTOR__": "Primary Doctor",
    "__FIELD_EMERGENCY_CONTACT__": "Emergency Contact Phone",
    "__EMERGENCY_CALL_911__": "If emergency, please call 911",
    
    "__SECTION_INSURANCE__": "Insurance Information",
    "__FIELD_INSURANCE_PROVIDER__": "Insurance Provider",
    "__FIELD_ID_NUMBER__": "ID Number",
    "__FIELD_GROUP_PLAN__": "Group / Plan",
    
    "__SECTION_CONDITIONS__": "Current Medical Conditions",
    "__CONDITION_DIABETES__": "Diabetes",
    "__CONDITION_HEART_DISEASE__": "Heart Disease",
    "__CONDITION_HIGH_BLOOD_PRESSURE__": "High Blood Pressure",
    "__CONDITION_ASTHMA__": "Asthma",
    "__CONDITION_STROKE__": "Stroke",
    "__CONDITION_CANCER__": "Cancer",
    "__CONDITION_KIDNEY_DISEASE__": "Kidney Disease",
    "__CONDITION_OTHER__": "Other",
    
    # Right Column - Medical
    "__SECTION_PAIN_SCALE__": "Pain Scale",
    "__PAIN_LEAST__": "Least",
    "__PAIN_MOST__": "Most",
    
    "__BODY_DIAGRAM_INSTRUCTION__": "Circle the part that hurts",
    
    "__SECTION_MEDICATIONS__": "Medications I Take",
    "__TABLE_MEDICATION__": "Medication",
    "__TABLE_DOSE__": "Dose",
    "__TABLE_HOW_OFTEN__": "How Often",
    
    "__SECTION_MOBILITY__": "Mobility & Accessibility",
    "__MOBILITY_WHEELCHAIR__": "Wheelchair",
    "__MOBILITY_WALKER__": "Walker",
    "__MOBILITY_HEARING_AID__": "Hearing Aid",
    "__MOBILITY_GLASSES__": "Glasses",
    
    # Bottom Section - Symptoms
    "__SECTION_SYMPTOMS__": "Symptom Assistance",
    "__SUBSECTION_PAIN_DESCRIPTION__": "Pain Description",
    "__PAIN_SHARP__": "Sharp",
    "__PAIN_DULL__": "Dull",
    "__PAIN_BURNING__": "Burning",
    "__PAIN_PRESSURE__": "Pressure",
    "__PAIN_THROBBING__": "Throbbing",
    "__PAIN_NUMBNESS__": "Numbness",
    
    "__SUBSECTION_COMMON_SYMPTOMS__": "Common Symptoms",
    "__SYMPTOM_NAUSEA__": "Nausea",
    "__SYMPTOM_VOMITING__": "Vomiting",
    "__SYMPTOM_DIZZINESS__": "Dizziness",
    "__SYMPTOM_FEVER__": "Fever",
    "__SYMPTOM_DIFFICULTY_BREATHING__": "Difficulty breathing",
    "__SYMPTOM_CHEST_PAIN__": "Chest pain",
    
    "__SUBSECTION_ALLERGIES__": "Common Allergies",
    "__ALLERGY_PEANUT__": "Peanut",
    "__ALLERGY_MEDICINE__": "Medicine",
    "__ALLERGY_SEAFOOD__": "Seafood",
    "__ALLERGY_DAIRY__": "Dairy",
    "__ALLERGY_OTHER__": "Other",
    
    "__FOOTER_SHOW_CARD__": "Show this card to staff if you need help."
}

def load_image_as_base64(path):
    try:
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            if path.lower().endswith(".png"):
                return f"data:image/png;base64,{encoded_string}"
            else:
                return f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Image '{path}' not found. Diagram will be blank.")
        return ""

def get_translation(client, target_language):
    print(f"Generating card in {target_language}...")
    
    prompt = f"""
    You are a precise medical translator. 
    Translate the following English dictionary values into {target_language}.
    
    Return ONLY a raw JSON object. Do not use Markdown formatting.
    
    Special Instructions:
    1. Key '__LANG_EN__': Return '{target_language}' in English (Uppercase).
    2. Key '__LANG_NATIVE__': Return '{target_language}' in its native script.
    3. IMPORTANT: Return ONLY the translated text. DO NOT add curly braces inside the value or brackets [].
    
    Source Dictionary to Translate:
    {json.dumps(SOURCE_TEXT)}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment.")
        return
    
    client = OpenAI(api_key=api_key)
    template_filename = "templates/pamphlet_template.html"
    try:
        with open(template_filename, "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Error: '{template_filename}' not found. Please ensure it is in the same folder.")
        return

    organ_image_data = load_image_as_base64("img/organ_diagram.jpg")

    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    while True:
        target_lang = input("Enter a language to generate (or 'q' to quit): ").strip()
        
        if target_lang.lower() == 'q':
            break
            
        translated_data = get_translation(client, target_lang)
        
        if translated_data:
            card_code = template
            
            if organ_image_data:
                img_tag = f'<img src="{organ_image_data}" alt="Body Diagram" style="max-width:100%; height:100%; object-fit:contain;">'
            else:
                img_tag = ""
            
            card_code = card_code.replace("[Body Diagram Image Here]", img_tag)

            print("cleaning LLM response...")
            for key, value in translated_data.items():
                clean_value = str(value).replace("{", "").replace("}", "").replace("｛", "").replace("｝", "")
                card_code = card_code.replace(key, clean_value)
                
            safe_name = target_lang.lower().replace(' ', '_')
            filename = os.path.join(output_folder, f"pamphlet_{safe_name}.html")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(card_code)
                
            print(f"Created: {filename}")

if __name__ == "__main__":
    main()