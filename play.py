import random

import requests

API_BASE = "https://sea-turtle-soup-ai.vercel.app/api"
AI_PLAYER_TYPES = ["detective_ai", "wild_guess_ai", "funny_ai", "instinct_ai"]


def get_new_soup():
    res = requests.post(f"{API_BASE}/soup")
    if res.status_code != 200 or res.json().get("status") != "success":
        print("無法取得題目，跳過。")
        return None
    return res.json()["data"]


def print_soup_brief(soup_data):
    print("\n湯面：")
    print(soup_data["brief_story"])
    print("\n你可以開始提問，與 AI 玩家輪流猜測，直到解開為止！")


# 啟用 AI 模式設定
use_ai = input("是否啟用 AI 玩家一起玩？(y/n): ").strip().lower() == "y"
selected_ai = None

if use_ai:
    try:
        count = int(input("請輸入要加入幾位 AI 玩家（1~4）：").strip())
        count = max(1, min(count, 4))
        candidates = random.sample(AI_PLAYER_TYPES, count)
        selected_ai = random.choice(candidates)
        print(f"從 {', '.join(candidates)} 中隨機選出  本場對手是：{selected_ai}")
    except:
        selected_ai = random.choice(AI_PLAYER_TYPES)
        print(f"輸入無效，已自動選擇 AI 玩家：{selected_ai}")

# 開始無限挑戰模式
while True:
    correct_guesses = []
    not_correct_guesses = []
    not_important_guesses = []
    turn = 0

    print("\n--- 新的海龜湯題目生成中 ---")
    soup_data = get_new_soup()
    if soup_data is None:
        continue  # 取得題目失敗，跳下一輪

    print_soup_brief(soup_data)

    while True:
        is_ai_turn = use_ai and (turn % 2 == 1)

        if is_ai_turn:
            print(f"\nAI 玩家（{selected_ai}）正在思考...")

            payload = {
                "soup": soup_data,
                "player_type": selected_ai,
                "correct_guesses": correct_guesses,
                "not_correct_guesses": not_correct_guesses,
                "not_important_guesses": not_important_guesses,
            }

            res = requests.post(f"{API_BASE}/ai_player", json=payload)
            if res.status_code != 200 or res.json().get("status") != "success":
                print("AI 錯誤，跳過此題。")
                break

            guess = res.json()["data"]["guess"]
            print(f"AI 猜測：「{guess}」")
        else:
            guess = input("\n請輸入你的猜測（'next' 換下一題，'exit' 離開）：").strip()
            if guess.lower() == "exit":
                print("已離開遊戲。")
                exit(0)
            elif guess.lower() == "next":
                print("正在跳至下一題...")
                break

        # 評估猜測
        payload = {
            "soup": soup_data,
            "guess": guess,
            "correct_guesses": correct_guesses,
            "not_correct_guesses": not_correct_guesses,
            "not_important_guesses": not_important_guesses,
        }

        res = requests.post(f"{API_BASE}/evaluate", json=payload)
        if res.status_code != 200 or res.json().get("status") != "success":
            print("評估錯誤，跳過此題。")
            break

        data = res.json()["data"]
        print(f"評估結果：{data['evaluation']}")
        print(f"是的：{data['correct_guesses']}")
        print(f"不是：{data['not_correct_guesses']}")
        print(f"不重要：{data['not_important_guesses']}")

        if data["judge"]:
            print("\n恭喜成功解開海龜湯！")
            print("湯底：")
            print(data["full_story"])
            break

        correct_guesses = data["correct_guesses"]
        not_correct_guesses = data["not_correct_guesses"]
        not_important_guesses = data["not_important_guesses"]
        turn += 1
