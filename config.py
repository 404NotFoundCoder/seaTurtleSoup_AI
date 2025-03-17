import os

from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# Groq API配置
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
