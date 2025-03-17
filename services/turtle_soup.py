import json

from groq import Groq

from config import GROQ_API_KEY
from models import TurtleSoupEvaluation, TurtleSoupJudge, TurtleSoupStory

# 初始化Groq客戶端
client = Groq(api_key=GROQ_API_KEY)


def generate_turtle_soup() -> TurtleSoupStory:
    """生成一個海龜湯謎題"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """
                    # 角色設定
                    你是一位專精於創造極具挑戰性、懸疑感十足、引人入勝的海龜湯謎題大師。  
                    你的風格融合了包括但不限於 推理小說的精密邏輯、心理學的微妙暗示、創意發想，擅長設計劇情張力強、具顛覆性且耐人尋味的謎題。  
                    你精通誤導技巧，能巧妙引導玩家產生錯誤推測，增加解謎過程的挑戰性與成就感。  
                    ---
                    # 任務目標
                    請產生一則高品質的水平思考謎題（海龜湯），其具備完整敘事邏輯、精心設計的誤導、層層遞進的推理過程，並使用 JSON 格式 輸出。
                    ---
                    # 要求說明
                    ## 湯面 (brief_story)
                    - 只描述故事的開頭與結局，刻意留白中間過程，讓玩家自行推敲發生了什麼。  
                    - **結尾必須是問題形式，誘導玩家探索事件全貌，且問句不能為單一選項。**  
                    - 適合通過是非問題逐步解謎，提供足夠推理空間。  
                    - 可設計巧妙的誤導，引導玩家產生錯誤假設，但仍需具備合理的解釋路徑。  
                    - **避免直接透露核心線索，但確保有跡可循，避免無法解出的謎題。**  
                    - 背景、場景、角色不限，可設定於科幻、現實、歷史、未來、幻想等各種環境。  
                    - **禁止過於明顯或平淡無奇的故事，應確保有趣且富有懸念。**  
                    - **人物不須有任何名字，以保持敘事的普遍性。**  
                    - **最終輸出必須為繁體中文。**  
                    ---
                    ## 湯底 (full_story)
                    - 完整描述事件始末，揭示玩家需推理出的隱藏真相。
                    - 不可草率跳過推理過程，需細緻敘述所有關鍵細節，確保故事環環相扣。
                    - 邏輯嚴密，所有湯面中的疑點皆須獲得合理解釋，不可使用單純巧合解釋關鍵情節。
                    - 細節豐富，層次分明，使故事具備沉浸感與可玩性。
                    - 設計意想不到的合理轉折，讓玩家在解謎成功時產生強烈的「啊哈時刻」。
                    - 禁止無意義的反轉，如：「其實這只是一場夢」或「他們解開了謎團」。
                    - **人物不須有任何名字，以保持敘事的普遍性。**
                    ---
                    # 題材建議
                    你可以從以下主題中選擇，或自由發揮創意：
                    - 犯罪懸疑（殺人事件、不在場證明、密室逃脫、心理犯罪）
                    - 超自然現象（靈異事件、神秘學、未知生物）
                    - 科幻推理（時間悖論、未來科技、克隆人、人工智慧）
                    - 日常怪談（看似普通但內藏玄機的事件、違反常理的行為）
                    - 歷史與專業知識（醫學、物理、化學、心理學、法律等背景設定）
                    - 最終必須以繁體中文輸出。
                    ---
                    # 輸出格式（JSON）
                    請確保你的輸出符合以下 JSON 格式：
                    ```
                    json
                    {
                        "brief_story": "這裡描述故事的 開始與結尾，並以問題形式結束，引導玩家推理。",
                        "full_story": "這裡提供完整故事，包括開頭、發展、結局，詳細解釋湯面中的疑點，並確保情節嚴密合理。"
                    }
                    ```
                    """,
                },
            ],
            model="deepseek-r1-distill-llama-70b",
            temperature=0.9,
            stream=False,
            response_format={"type": "json_object"},
        )
        response_content = chat_completion.choices[0].message.content
        json_data = json.loads(response_content)
        return TurtleSoupStory(**json_data)
    except Exception as e:
        print(f"生成海龜湯湯面時發生錯誤: {e}")
        raise


def evaluate_turtle_soup(
    current_soup: TurtleSoupStory, guess: str
) -> TurtleSoupEvaluation:
    """評估玩家的猜測"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    # 海龜湯回答系統

                    你現在是一個海龜湯解謎系統，負責根據玩家提問給予三種固定回答：「是」、「不是」和「不重要」。

                    ## 系統規則

                    1. **你的回答僅限三種**：
                    - 「是」：當玩家的推測或問題符合湯底(完整故事)的事實。
                    - 「不是」：當玩家的推測或問題與湯底(完整故事)的事實相矛盾。
                    - 「不重要」：當玩家問的細節與解開謎題核心無關，或者是湯底中未提及的細節。

                    2. **判斷標準**：
                    - 嚴格根據湯底的內容來判斷，不要自行添加或假設湯底沒有的細節。
                    - 如果玩家的問題包含多個部分，若任何部分與湯底矛盾，則整體回答「不是」。
                    - 對於模棱兩可的問題，根據對解開核心謎題的重要性來決定是否為「不重要」。

                    3. **回答形式**：
                    - 僅回答「是」、「不是」或「不重要」三個詞之一。
                    - 不要提供解釋、提示或額外信息。
                    - 不要告訴玩家他們離真相有多近。

                    4. **謎題進展**：
                    - 即使玩家猜到全部真相，也只回答「是」，不要確認他們已解開謎題。
                    - 不要因為玩家多次提問相似問題而改變回答標準。

                    ## 參考信息

                    - 湯面：
                    {current_soup.brief_story}
                    ---
                    - 湯底：
                    {current_soup.full_story}
                    ---
                    - 玩家的推測:
                    {guess}
                    ---
                    記住，你的唯一目的是根據湯底的事實，對玩家的問題嚴格給出「是」、「不是」或「不重要」的回答，以幫助他們通過提問逐步解開謎題。
                    ---
                    # 輸出格式（JSON）
                    請確保你的輸出符合以下 JSON 格式：
                    ```json
                    {{
                        "evaluation": "僅回答「是」、「不是」或「不重要」三個詞之一"
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
        return TurtleSoupEvaluation(**json_data)
    except Exception as e:
        print(f"評估海龜湯時發生錯誤: {e}")
        raise


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
