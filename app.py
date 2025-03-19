from flask import Flask, jsonify, request

from models import TurtleSoupStory
from services.player.ai_player import generate_ai_player
from services.player.player_config import AI_PLAYERS
from services.turtle_soup import (
    evaluate_turtle_soup,
    generate_turtle_soup,
    judge_turtle_soup,
)

app = Flask(__name__)


@app.route("/api/soup", methods=["POST"])
def create_turtle_soup():
    """生成新的海龜湯謎題"""

    try:
        soup = generate_turtle_soup()

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

    try:
        data = request.get_json()

        # 檢查請求是否包含所有必要的參數
        required_keys = [
            "soup",
            "correct_guesses",
            "not_correct_guesses",
            "not_important_guesses",
            "guess",
        ]
        if not data or not all(key in data for key in required_keys):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"請提供所有必要的參數: {required_keys}",
                    }
                ),
                400,
            )

        # 從請求中提取數據
        soup = TurtleSoupStory(**data["soup"])  # 轉換成 TurtleSoupStory 物件
        correct_guesses = data["correct_guesses"]
        not_correct_guesses = data["not_correct_guesses"]
        not_important_guesses = data["not_important_guesses"]
        guess = data["guess"]

        # **1. 評估猜測**
        try:
            evaluation_result = evaluate_turtle_soup(soup, guess)
        except Exception as e:
            return (
                jsonify({"status": "error", "message": f"評估海龜湯時發生錯誤: {e}"}),
                500,
            )

        # 更新猜測歷史
        if evaluation_result.evaluation == "是":
            correct_guesses.append(guess)
        elif evaluation_result.evaluation == "不是":
            not_correct_guesses.append(guess)
        else:  # 不重要
            not_important_guesses.append(guess)

        # **2. 判斷是否解開謎題**
        try:
            judge_result = judge_turtle_soup(soup, correct_guesses)
        except Exception as e:
            return (
                jsonify({"status": "error", "message": f"評估海龜湯時發生錯誤: {e}"}),
                500,
            )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "evaluation": evaluation_result.evaluation,
                    "judge": judge_result.judge == "pass",
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

    try:
        data = request.get_json()

        # 檢查請求是否包含所有必要的參數
        required_keys = [
            "soup",
            "player_type",
            "correct_guesses",
            "not_correct_guesses",
            "not_important_guesses",
        ]
        if not data or not all(key in data for key in required_keys):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"請提供所有必要的參數: {required_keys}",
                    }
                ),
                400,
            )

        # 從請求中提取數據
        soup = TurtleSoupStory(**data["soup"])  # 轉換成 TurtleSoupStory 物件
        player_type = data["player_type"]
        correct_guesses = data["correct_guesses"]
        not_correct_guesses = data["not_correct_guesses"]
        not_important_guesses = data["not_important_guesses"]

        # 確保 player_type 在允許的 AI 玩家類型內
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

        # 生成AI玩家的猜測
        try:
            guess_result = generate_ai_player(
                soup,
                player_type,
                correct_guesses,
                not_correct_guesses,
                not_important_guesses,
            )
        except Exception as e:
            return (
                jsonify(
                    {"status": "error", "message": f"生成AI玩家猜測時發生錯誤: {e}"}
                ),
                500,
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
