import os

# --- SMART FONT CALCULATOR ---
def calculate_font_size(text, max_chars=14, default_size=40):
    """
    Shrinks font size if the Language Name is too long.
    """
    length = len(text)
    if length <= max_chars:
        return str(default_size)
    extra_chars = length - max_chars
    new_size = default_size - (extra_chars * 1.5) 
    if new_size < 20: new_size = 20
    return str(int(new_size))

# --- LANGUAGE DATABASE ---
database = [
    {
        "filename": "card_chinese.svg",
        "data": {
            "{{LANG_EN}}": "CHINESE",
            "{{LANG_NATIVE}}": "中文",
            "{{HEADER_SUB}}": "我需要一名翻译",
            "{{LBL_NAME}}": "姓名",
            "{{LBL_PHONE}}": "电话",
            "{{NEEDS_SUB}}": "当前需求",
            "{{PAIN_SUB}}": "疼痛等级",
            "{{CIRCLE_SUB}}": "请圈出疼痛部位",
            "{{HISTORY_SUB}}": "病史资料",
            "{{ALLERGY_SUB}}": "过敏",
            "{{MEDS_SUB}}": "药物",
            "{{MED_NAME}}": "药名",
            "{{MED_DOSE}}": "量",
            "{{FINANCIAL_SUB}}": "财务权利与保险",
            "{{LBL_INSURANCE}}": "保险公司",
            "{{LBL_ID}}": "会员号",
            "{{LBL_STAFF}}": "请出示给员工",
            "{{ADVOCACY_TEXT}}": "我有权了解费用。请写下预估价。",
            "{{LBL_COST}}": "预估费"
        }
    },
    {
        "filename": "card_vietnamese.svg",
        "data": {
            "{{LANG_EN}}": "VIETNAMESE",
            "{{LANG_NATIVE}}": "Tiếng Việt",
            "{{HEADER_SUB}}": "Tôi cần một thông dịch viên",
            "{{LBL_NAME}}": "Tên",
            "{{LBL_PHONE}}": "Số điện thoại",
            "{{NEEDS_SUB}}": "Nhu cầu cấp bách",
            "{{PAIN_SUB}}": "Thang đo đau",
            "{{CIRCLE_SUB}}": "Khoanh tròn nơi đau",
            "{{HISTORY_SUB}}": "Tiền sử bệnh",
            "{{ALLERGY_SUB}}": "Dị ứng",
            "{{MEDS_SUB}}": "Thuốc",
            "{{MED_NAME}}": "Tên thuốc",
            "{{MED_DOSE}}": "Liều lượng",
            "{{FINANCIAL_SUB}}": "Quyền tài chính",
            "{{LBL_INSURANCE}}": "Bảo hiểm",
            "{{LBL_ID}}": "Mã số",
            "{{LBL_STAFF}}": "Đưa cho nhân viên",
            "{{ADVOCACY_TEXT}}": "Tôi có quyền biết chi phí. Vui lòng ghi lại ước tính.",
            "{{LBL_COST}}": "Chi phí ước tính"
        }
    }
]

# --- GENERATION LOOP ---
try:
    with open("template.svg", "r", encoding="utf-8") as f:
        template = f.read()
except FileNotFoundError:
    print("Error: template.svg not found.")
    exit()

for entry in database:
    card_code = template
    data = entry["data"]
    
    # 1. Calculate dynamic font size for the Language Title
    lang_size = calculate_font_size(data["{{LANG_EN}}"], max_chars=12, default_size=40)
    card_code = card_code.replace("{{SIZE_LANG}}", lang_size)
    
    # 2. Replace all other placeholders
    for key, value in data.items():
        card_code = card_code.replace(key, value)
        
    # 3. Save
    with open(entry["filename"], "w", encoding="utf-8") as f:
        f.write(card_code)
    print(f"Generated {entry['filename']}")
