import os
import json
import datetime

class NewsletterManager():
    def __init__(self):
        self.filename = "newsletter_db.json"
        self.path = os.path.join("configs", self.filename)
        with open(self.path) as file:
            self.configs = json.load(file , object_hook=self.date_hook)

    def get(self):
        return self.configs

    def date_hook(self, json_dict):
        for (key, value) in json_dict.items():
            if key in ['start', 'end']:
                json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d").date()

            if key in ['time_start', 'time_end']:
                json_dict[key] = datetime.datetime.strptime(value, "%H:%M:%S").time()

        return json_dict

