import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SOURCE_TEXT = {
    "{{HEADER_SUB}}": "I need an interpreter",
    "{{LBL_NAME}}": "Name",
    "{{LBL_PHONE}}": "Emergency Phone",
    "{{NEEDS_SUB}}": "Immediate Needs",
    "{{PAIN_SUB}}": "Pain Scale",
    "{{CIRCLE_SUB}}": "Circle where it hurts",
    "{{HISTORY_SUB}}": "Medical History",
    "{{ALLERGY_SUB}}": "Allergies",
    "{{MEDS_SUB}}": "Medications",
    "{{MED_NAME}}": "Name",
    "{{MED_DOSE}}": "Dose",
    "{{FINANCIAL_SUB}}": "Financial Rights & Insurance",
    "{{LBL_INSURANCE}}": "Insurance Provider",
    "{{LBL_ID}}": "Member ID",
    "{{LBL_STAFF}}": "Show to Staff",
    "{{ADVOCACY_TEXT}}": "I have the right to know the cost. Please write the estimate below.",
    "{{LBL_COST}}": "Estimated Cost"
}

def calculate_font_size(text, max_chars=14, default_size=40):
    length = len(text)
    if length <= max_chars:
        return str(default_size)
    extra_chars = length - max_chars
    new_size = default_size - (extra_chars * 1.5) 
    if new_size < 20: new_size = 20
    return str(int(new_size))

def get_translation(client, target_language):
    print(f"Generating card in {target_language}...")
    
    prompt = f"""
    You are a precise medical translator. 
    Translate the following English dictionary values into {target_language}.
    
    Return ONLY a raw JSON object. Do not use Markdown formatting.
    
    Special Instructions:
    1. Key '{{LANG_EN}}': Return '{target_language}' in English (Uppercase).
    2. Key '{{LANG_NATIVE}}': Return '{target_language}' in its native script.
    3. IMPORTANT: Return ONLY the translated text. DO NOT add curly braces {{}} or brackets [] around the values.
    
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

    try:
        with open("template.svg", "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print("'template.svg' not found.")
        return

    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    while True:
        print("\n" + "="*40)
        target_lang = input("Enter a language to generate (or 'q' to quit): ").strip()
        
        if target_lang.lower() == 'q':
            break
            
        translated_data = get_translation(client, target_lang)
        
        if translated_data:
            card_code = template
            
            raw_en = translated_data.get("{{LANG_EN}}", target_lang)
            clean_en = str(raw_en).replace("{", "").replace("}", "").replace("｛", "").replace("｝", "")
            translated_data["{{LANG_EN}}"] = clean_en

            if "{{LANG_NATIVE}}" in translated_data:
                raw_native = translated_data["{{LANG_NATIVE}}"]
                clean_native = str(raw_native).replace("{", "").replace("}", "").replace("｛", "").replace("｝", "")
                translated_data["{{LANG_NATIVE}}"] = clean_native

            font_size = calculate_font_size(clean_en)
            card_code = card_code.replace("{{SIZE_LANG}}", font_size)
            
            for key, value in translated_data.items():
                clean_value = str(value).replace("{", "").replace("}", "").replace("｛", "").replace("｝", "")
                
                card_code = card_code.replace("{" + key + "}", clean_value)
                card_code = card_code.replace(key, clean_value)
                
            safe_name = target_lang.lower().replace(' ', '_')
            filename = os.path.join(output_folder, f"card_{safe_name}.svg")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(card_code)
                
            print(f"Created: {filename}")

if __name__ == "__main__":
    main()