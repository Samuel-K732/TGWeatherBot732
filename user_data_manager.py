import json


class UserDataManager:
    def __init__(self, filename: str):
        self.filename = filename
        self._data = self._load()

    def _load(self) -> dict:
        with open(self.filename, "r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self._data, file, ensure_ascii=False, indent=2)

    def get(self, user_id: str) -> dict | None:
        return self._data.get(user_id)

    def set(self, user_id: str, location: dict):
        self._data[user_id] = location
        self._save()

    def exist(self, user_id: str) -> bool:
        return user_id in self._data
