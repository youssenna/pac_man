import json


def is_valid_name(name: object) -> bool:
    if not isinstance(name, str):
        return False
    if not 1 <= len(name) <= 10:
        return False
    if not name.strip():
        return False
    for c in name:
        if not (c.isalnum() or c == " "):
            return False
    return True


def load_highscores(path: str) -> list[tuple[str, int]]:
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error loading highscores: {e}")
        return []

    if not isinstance(data, list):
        print("Error loading highscores: JSON data must be a list")
        return []

    highscores: list[tuple[str, int]] = []

    for entry in data:
        if not isinstance(entry, dict):
            continue

        name = entry.get("name")
        score = entry.get("score")

        if not isinstance(name, str) or not is_valid_name(name):
            continue

        if not isinstance(score, int) or isinstance(score, bool) or score < 0:
            continue

        highscores.append((name, score))

    highscores.sort(key=lambda item: item[1], reverse=True)

    return highscores[:10]


def save_highscores(path: str, scores: list[tuple[str, int]]) -> bool:
    data: list[dict[str, object]] = []

    for name, score in scores:
        data.append({
            "name": name,
            "score": score
        })

    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except OSError as e:
        print(f"Error saving highscores: {e}")
        return False

    return True


def is_highscore(scores: list[tuple[str, int]], score: int) -> bool:
    if len(scores) < 10:
        return True
    if score > scores[-1][1]:
        return True

    return False


def add_highscore(path: str, name: str, score: int) -> bool:
    if not is_valid_name(name):
        return False

    if not isinstance(score, int) or isinstance(score, bool) or score < 0:
        return False

    highscores = load_highscores(path)

    highscores.append((name, score))
    highscores.sort(key=lambda item: item[1], reverse=True)
    highscores = highscores[:10]

    return save_highscores(path, highscores)
