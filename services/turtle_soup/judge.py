import json

from groq import Groq

from config import GROQ_API_KEY
from models import TurtleSoupJudge, TurtleSoupStory

# 初始化Groq客戶端
client = Groq(api_key=GROQ_API_KEY)


def judge_turtle_soup(
    current_soup: TurtleSoupStory, correct_guesses: list
) -> TurtleSoupJudge:
    """判斷玩家是否已經解開謎題"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    # 海龜湯解謎完成判定系統

                    你是一個專門負責評估海龜湯解謎完成度的 AI 判定系統。你的任務是根據**湯面**（謎題的公開資訊）、
                    **湯底**（隱藏的真相），以及**玩家的猜測歷史紀錄**，判斷玩家是否已成功破解謎題核心，並給出最終評價：`pass`（通關）或 `fail`（未完成）。

                    ## 判定規則

                    ### 1. 核心情節對比  
                    - **識別湯底中的關鍵要素**，找出構成謎題核心的主要事件與細節(主要真相)。  
                    - **比對玩家已猜出的內容**，判斷其是否涵蓋了湯底的關鍵情節，並確保推理過程合理，判斷其是否涵蓋謎題的核心，而非僅接近答案。  
                    - **關鍵資訊須正確識別**，但對於細節誤差或不影響整體理解的次要資訊，可適度放寬標準。 

                    ### 2. 邏輯鏈評估  
                    - 玩家是否能**完整地串聯事件發生、發展與結局**。  
                    - 玩家是否理解事件的**主要時間線與因果關係**，確保推理過程清晰且邏輯自洽，能夠解釋發生的關鍵原因。  
                    - 玩家是否掌握**關鍵角色的動機**，並能合理解釋他們的行為與決策、主要行為背後的意圖。  
                    - 玩家是否識別**影響結局的關鍵轉折點**，即是否理解哪些因素導致事件結果，避免關鍵誤解或錯誤推理。  
                    
                    ## 參考信息
                    請根據下列信息來進行評估並生成結果：

                    - 湯面：
                    {current_soup.brief_story}
                    ---
                    - 湯底：
                    {current_soup.full_story}
                    ---
                    - **玩家的猜測歷史紀錄(玩家已猜出的內容)**：
                    {correct_guesses}
                    ---
                    ## 判定標準  

                    - **`pass`（通關）**：玩家的推理已覆蓋謎題核心，並能構建完整的事件邏輯。  
                    - **`fail`（未完成）**：玩家的推理仍存在缺漏，尚未完全揭示謎題的核心情節，或邏輯鏈不完整。
                    - 你的判定應該基於**客觀分析**，確保每一次評估都能幫助玩家了解其解謎進度。
                    - 你的判定應該聚焦於**關鍵真相**，適度忽略不影響核心理解的細節，確保玩家能在合理範圍內完成解謎。

                    ## 輸出格式
                    請根據玩家的理解情況，返回以下結果：

                    ```json
                    {{
                        "judge": "pass 或 fail"
                    }}
                    ```
                    
                    """,
                },
            ],
            model="deepseek-r1-distill-llama-70b",
            temperature=0.2,
            stream=False,
            response_format={"type": "json_object"},
        )
        response_content = chat_completion.choices[0].message.content
        json_data = json.loads(response_content)
        return TurtleSoupJudge(**json_data)
    except Exception as e:
        print(f"評估海龜湯時發生錯誤: {e}")
        raise
