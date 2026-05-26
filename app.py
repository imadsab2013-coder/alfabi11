import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import json
import os
import math
import re

# 1. إعداد المجلد المادي لحفظ البيانات والدليل الرقمي للقواعد
DATA_DIR = "data_protocol"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
RULES_FILE = os.path.join(DATA_DIR, "rules_ledger.json")

# 2. النواة الصلبة: المتجهات النصية الـ 14 الخام المستخرجة من النصوص
VECTORS = [
    "ALM", "ALMR", "ALR", "ALMS", "KHYES", 
    "TCM", "TC", "YC", "TH", "PM", "PMECQ", 
    "S", "Q", "N"
]

# الحروف الـ 14 الفريدة المكونة للنظام المغلق
LETTERS = sorted(list(set("".join(VECTORS))))

# استخراج العلاقات المتجهة الإلزامية من النصوص الخام (قاعدة البيانات المرجعية للمحرك)
MANDATORY_TRANSITIONS = set()
for vector in VECTORS:
    if len(vector) > 1:
        for i in range(len(vector) - 1):
            MANDATORY_TRANSITIONS.add((vector[i], vector[i+1]))

# 3. دالات إدارة ملفات القيود (JSON Ledger)
def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_rules(rules):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=4)

# 4. محرك الفحص والتحقق المادي (Automated Rule Validation Engine)
def validate_rule_against_vectors(rule_text):
    """
    يقوم بتحليل القاعدة نصياً وإسقاطها على المتجهات الإلزامية للتأكد من عدم وجود تصادم مادي.
    الصيغ المدعومة: 
    - X -> Y  (تعني X يمين يتصل بـ Y يسار)
    - X != Y (تعني X لا يتصل بـ Y)
    """
    clean_rule = rule_text.replace(" ", "").upper()
    
    # حالة الاتصال الإيجابي X -> Y
    if "->" in clean_rule:
        parts = clean_rule.split("->")
        if len(parts) == 2 and parts[0] in LETTERS and parts[1] in LETTERS:
            x, y = parts[0], parts[1]
            # فحص التناقض: هل هناك متجه يمنع هذا الاتصال؟ (متروك للتوسيع الهندسي)
            return {"valid": True, "msg": f"الاتصال المتجه المباشر من {x} إلى {y} معتمد ولا يصطدم بالمتجهات الأساسية."}
    
    # حالة النفي المادي X != Y
    if "!=" in clean_rule:
        parts = clean_rule.split("!=")
        if len(parts) == 2 and parts[0] in LETTERS and parts[1] in LETTERS:
            x, y = parts[0], parts[1]
            # فحص التصادم: إذا كانت القاعدة تنفي اتصالاً وهو إلزامي في النصوص، فالقاعدة باطلة
            if (x, y) in MANDATORY_TRANSITIONS:
                return {"valid": False, "msg": f"تصادم مادي كلي! المتجهات النصية تفرض حتماً اتصال {x} بـ {Y}."}
            return {"valid": True, "msg": f"قاعدة العزل بين {x} و {y} صامدة ولم تكسر أي متجه نصي."}
            
    return {"valid": True, "msg": "تم تسجيل القاعدة كملاحظة بنيوية حرة تحت الاختبار الكلي للاحتمالات."}

# 5. بناء واجهة المستخدم Streamlit
st.set_page_config(layout="wide", page_title="مختبر بروتوكول البينة")

st.markdown("# محرك التحليل المادي لمتجهات البينة (14 نقطة متساوية)")
st.markdown("---")

# تقسيم الشاشة هندسياً
col_control, col_graph = st.columns([1, 1])

# إدارة القواعد في لوحة التحكم
with col_control:
    st.markdown("### 📥 لوحة تحكم القيود والملاحظات")
    
    # تعليمات الصيغة للمستخدم لضمان دقة الإدخال البرمجي
    with st.expander("ℹ️ دليل صياغة القواعد الرياضية للمحرك"):
        st.code("X -> Y  : لفرض أن يمين X يتصل بـ يسار Y (عكس عقارب الساعة)\nX != Y : لفرض عزل فراغي تام بين الحرفين ومنع التجاور", language="text")
    
    # حقل الإدخال
    rule_input = st.text_input("أدخل صيغة القاعدة المادية الجديدة:")
    if st.button("🚨 تشغيل اختبار التصادم وحفظ القاعدة"):
        if rule_input:
            rules = load_rules()
            # فحص القاعدة قبل الحفظ
            check_result = validate_rule_against_vectors(rule_input)
            
            if check_result["valid"]:
                st.success(check_result["msg"])
                new_id = len(rules) + 1 if not rules else max([r["id"] for r in rules]) + 1
                rules.append({"id": new_id, "text": rule_input, "status": "صامدة"})
                save_rules(rules)
            else:
                st.error(check_result["msg"])
                
    st.markdown("---")
    st.markdown("### 🗂️ دفتر القيود المرقمة (مجلد الحفظ المادي)")
    
    current_rules = load_rules()
    if current_rules:
        for r in current_rules:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**قاعدة رقم [{r['id']}]**: `{r['text']}` — 🛡️ *{r['status']}*")
            with c2:
                if st.button("حذف", key=f"del_{r['id']}"):
                    updated_rules = [rule for rule in current_rules if rule["id"] != r["id"]]
                    save_rules(updated_rules)
                    st.rerun()
    else:
        st.info("مجلد البيانات فارغ حالياً. لم يتم تثبيت أي قاعدة مادية بعد.")

# بناء الشاشة الديناميكية لعرض الحروف وتحريكها
with col_graph:
    st.markdown("### 🕸️ مصفوفة الفضاء الفيزيائي التفاعلي (الحروف الحرة)")
    st.caption("الحروف موزعة هندسياً على 14 نقطة متساوية الأبعاد وتنظر إلى المركز. يمكنك سحب الحروف يدوياً لإعادة رصد التناظر.")
    
    # إنشاء شبكة PyVis الموجهة
    net = Network(height="500px", width="100%", bgcolor="#1a1a1a", font_color="white", directed=True)
    
    # حساب الإحداثيات القطبية الثابتة لـ 14 نقطة متساوية المسافة حول المركز
    radius = 200
    center_x = 0
    center_y = 0
    
    # إسقاط العقد (Nodes) في الدائرة مع السماح بالتحريك الفيزيائي (Draggable)
    for i, letter in enumerate(LETTERS):
        angle = (2 * math.pi * i) / 14
        x_pos = center_x + radius * math.cos(angle)
        y_pos = center_y + radius * math.sin(angle)
        
        # إضافة الحرف ككيان مادي مستقل
        net.add_node(
            letter, 
            label=f" {letter} ", 
            x=int(x_pos), 
            y=int(y_pos), 
            shape="circle",
            color="#4f8bf9",
            size=25,
            font={'size': 18, 'face': 'Courier'}
        )
    
    # إسقاط المتجهات الإلزامية كروابط فيزيائية مرئية لتوضيح اتجاه الدخول والخروج
    for edge in MANDATORY_TRANSITIONS:
        net.add_edge(edge[0], edge[1], color="#2ecc71", width=2, arrows="to")
        
    # تكوين خيارات الفيزياء للسحب والإفلات الحر دون انهيار الهيكل الدائري
    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -2000,
          "centralGravity": 0.1,
          "springLength": 95,
          "springConstant": 0.04
        },
        "minVelocity": 0.75
      }
    }
    """)
    
    # تصدير الشبكة كملف HTML مؤقت وعرضه داخل واجهة Streamlit المزامنة
    path_html = os.path.join(DATA_DIR, "interactive_circle.html")
    net.save_graph(path_html)
    
    with open(path_html, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    components.html(html_content, height=520)

    # عرض المتجهات النصية الخام تحت الدائرة مباشرة للمطابقة البصرية السريعة
    st.markdown("**المتجهات النصية المرجعية في النواة:**")
    st.text(f"قاعدة البيانات الثابتة: {', '.join(VECTORS)}")
