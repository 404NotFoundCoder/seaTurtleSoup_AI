import json

from groq import Groq

from config import GROQ_API_KEY
from models import TurtleSoupGuess, TurtleSoupStory
from services.player.player_config import AI_PLAYERS

# 初始化Groq客戶端
client = Groq(api_key=GROQ_API_KEY)


def generate_ai_player(
    soup: TurtleSoupStory,
    player_type: str,
    correct_guesses: list,
    not_correct_guesses: list,
    not_important_guesses: list,
) -> TurtleSoupGuess:
    """根據AI玩家類型生成猜測"""
    try:
        # 查找指定類型的AI玩家，找不到則返回預設 detective AI
        ai_player = AI_PLAYERS.get(player_type, AI_PLAYERS["detective_ai"])

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    # 海龜湯解謎AI玩家
                    你是一名海龜湯解謎AI玩家。
                    你將根據湯面提供的資訊，逐步拆解並推測出真相。

                    ## 角色特徵
                    {ai_player['features']}

                    ## 任務目標
                    {ai_player['goal']}
                    - 在**資訊不足時，猜測應簡短且針對性強(短、精簡、明確)的單一問句**；如:凶手是死者的同事嗎？死者因书房内的某种机关而死亡吗？
                    - 當資訊充足時，才可提出更完整的推論。  
                    - 根據「是/不是/不重要」的回應，調整推理方向，逐步縮小範圍。  
                    - **每次猜測應明確聚焦於單一重點，避免同時提出多個假設或不必要的細節。**  
                    - **不使用「或者」，確保每個猜測獨立、清晰、具體。**  
                    - 依據湯面描述與已知資訊，做出邏輯嚴謹的合理推測，以推動解謎進程。  

                    ## 參考信息:
                    請根據下列信息來猜測：
                    - 湯面：
                    {soup.brief_story}

                    ---
                    ## 歷史猜測列表  
                    ### 「是」的資訊  
                    {correct_guesses}

                    ### 「不是」的資訊  
                    {not_correct_guesses}

                    ### 「不重要」的資訊  
                    {not_important_guesses}

                    ---
                    ## 輸出格式
                    根據湯面的描述和歷史推測列表，請提供以下結果：

                    ```json
                    {{
                        "guess": "根據湯面的描述，提出一個疑問或猜測"
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
        return TurtleSoupGuess(**json_data)
    except Exception as e:
        print(f"生成AI玩家猜測時發生錯誤: {e}")
        raise
