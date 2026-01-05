import json
import os

class UserManager:
    def __init__(self, db_file="user_preferences.json"):
        self.db_file = db_file
        self.preferences = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.db_file):
            return {}
        try:
            with open(self.db_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_data(self):
        try:
            with open(self.db_file, "w") as f:
                json.dump(self.preferences, f, indent=4)
        except IOError as e:
            print(f"Error saving user preferences: {e}")

    def set_user_state(self, user_id, state):
        """Saves a user's preferred state."""
        self.preferences[str(user_id)] = state
        self._save_data()

    def get_user_state(self, user_id):
        """Returns the user's preferred state, or None if not set."""
        return self.preferences.get(str(user_id))
