from flask import Flask, jsonify, request

from config import AI_PLAYERS
from services.ai_player import generate_ai_player
from services.turtle_soup import (
    evaluate_turtle_soup,
    generate_turtle_soup,
    judge_turtle_soup,
)

app = Flask(__name__)

# 全局變量存儲當前謎題和猜測歷史
soup = None
correct_guesses = []
not_correct_guesses = []
not_important_guesses = []


@app.route("/api/soup", methods=["POST"])
def create_turtle_soup():
    """生成新的海龜湯謎題"""
    global soup, correct_guesses, not_correct_guesses, not_important_guesses

    try:
        soup = generate_turtle_soup()
        # 重置猜測歷史
        correct_guesses = []
        not_correct_guesses = []
        not_important_guesses = []
        print(soup)
        return jsonify(
            {
                "status": "success",
                "data": {
                    "brief_story": soup.brief_story,
                    "full_story": soup.full_story,
                },
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/evaluate", methods=["POST"])
def evaluate_and_judge():
    """評估玩家的猜測並判斷是否解開謎題"""
    global soup, correct_guesses, not_correct_guesses, not_important_guesses

    if not soup:
        return jsonify({"status": "error", "message": "請先生成海龜湯謎題"}), 400

    try:
        data = request.get_json()
        if not data or "guess" not in data:
            return jsonify({"status": "error", "message": "請提供猜測內容"}), 400

        guess = data["guess"]

        # 評估猜測
        evaluation_result = evaluate_turtle_soup(soup, guess)

        # 更新猜測歷史
        if evaluation_result.evaluation == "是":
            correct_guesses.append(guess)
        elif evaluation_result.evaluation == "不是":
            not_correct_guesses.append(guess)
        else:  # 不重要
            not_important_guesses.append(guess)

        # 判斷是否解開謎題
        judge_result = judge_turtle_soup(soup, correct_guesses)

        return jsonify(
            {
                "status": "success",
                "data": {
                    "evaluation": evaluation_result.evaluation,
                    "judge": judge_result.judge,
                    "correct_guesses": correct_guesses,
                    "not_correct_guesses": not_correct_guesses,
                    "not_important_guesses": not_important_guesses,
                    "full_story": (
                        soup.full_story if judge_result.judge == "pass" else None
                    ),
                },
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/ai_player", methods=["POST"])
def create_ai_player_guess():
    """創建AI玩家並生成猜測"""
    global soup, correct_guesses, not_correct_guesses, not_important_guesses

    if not soup:
        return jsonify({"status": "error", "message": "請先生成海龜湯謎題"}), 400

    try:
        data = request.get_json()

        # 檢查請求是否包含有效的資料和 'player_type'
        if not data or "player_type" not in data:
            return jsonify({"status": "error", "message": "請提供AI玩家類型"}), 400

        player_type = data["player_type"]

        # 檢查AI玩家類型是否有效
        if player_type not in AI_PLAYERS:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"無效的AI玩家類型，可用類型: {list(AI_PLAYERS.keys())}",
                    }
                ),
                400,
            )

        # 生成AI玩家猜測
        guess_result = generate_ai_player(
            soup,
            player_type,
            correct_guesses,
            not_correct_guesses,
            not_important_guesses,
        )

        return jsonify(
            {
                "status": "success",
                "data": {"player_type": player_type, "guess": guess_result.guess},
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
