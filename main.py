import os
import streamlit as st
from dotenv import load_dotenv
import requests
from docx import Document
from pypdf import PdfReader

# =========！！！这里必须紧跟import之后，第一个st_xxx语句！！！=========
st.set_page_config(page_title="AI简历助手|DeepSeek版")

# 加载密钥
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

# ----------------------工具函数：读取docx/pdf文本----------------------
def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def read_pdf(file):
    reader = PdfReader(file)
    pages = [page.extract_text() for page in reader.pages]
    return "\n".join(pages)

# ----------------------调用DeepSeek接口----------------------
def call_deepseek(prompt:str):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model":"deepseek-chat",
        "temperature":0.3,
        "messages":[{"role":"user","content":prompt}]
    }
    resp = requests.post(API_URL, json=payload, headers=headers)
    return resp.json()["choices"][0]["message"]["content"]

# ----------------------页面UI（全部挪到函数的下面）----------------------
st.title("AI简历助手|DeepSeek版")
st.caption("上传简历，支持PDF / DOCX")

upload_file = st.file_uploader("上传简历文件",type=["pdf","docx"])
jd_text = st.text_area("粘贴岗位JD（选填，用于匹配打分&简历润色）","")

if upload_file is not None:
    suffix = upload_file.name.split(".")[-1].lower()
    if suffix == "docx":
        resume_content = read_docx(upload_file)
    elif suffix == "pdf":
        resume_content = read_pdf(upload_file)
    else:
        resume_content=""
    st.subheader("📄简历原始文本预览")
    st.text_area("",resume_content,height=250)

    if st.button("🚀开始解析&优化简历"):
        with st.spinner("大模型处理中，请等待..."):
            prompt = f"""
你是专业求职简历优化助手。
【简历原文】
{resume_content}
【岗位JD】
{jd_text if jd_text else "无提供JD"}

输出三部分：
1.结构化简历摘要（教育、实习、项目、技能）
2.JD匹配评估：匹配分数0‑100，优势、短板
3.优化建议：基于STAR法则改写项目经历，禁止编造不存在经历。
"""
            result = call_deepseek(prompt)
            st.subheader("✅AI处理结果")
            st.markdown(result)