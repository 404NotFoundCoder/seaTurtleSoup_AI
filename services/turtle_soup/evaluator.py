import json

from groq import Groq

from config import GROQ_API_KEY
from models import TurtleSoupEvaluation, TurtleSoupStory

# 初始化Groq客戶端
client = Groq(api_key=GROQ_API_KEY)


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
