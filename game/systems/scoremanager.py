import json
import os
from datetime import datetime

class ScoreManager:
    def __init__(self, scores_file):
        self.scores_file = scores_file

    def save_match(self, p1, p2, scores, winner_index):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "player1": p1,
            "player2": p2,
            "score": scores,
            "winner": f"{p1 if winner_index == 0 else p2}"
        }

        data = []
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []

        data.append(entry)

        with open(self.scores_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
