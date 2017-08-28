import os
import json
import datetime
import itertools

class NewsletterManager():
    def __init__(self, newsletter_file = "configs/newsletter_db.json"):
        self.path = newsletter_file
        # self.path = os.path.join("configs", self.filename)
        with open(self.path) as file:
            self.configs = json.load(file , object_hook=self.date_hook)

        with open(os.path.join("configs", "newsletter.json")) as file:
            self.newsletterCfg = json.load(file , object_hook=self.date_hook)

    def get(self):
        return self.configs

    def date_hook(self, json_dict):
        for (key, value) in json_dict.items():
            if key in ['start', 'end']:
                json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d").date()

            if key in ['time_start', 'time_end']:
                json_dict[key] = datetime.datetime.strptime(value, "%H:%M:%S").time()

        return json_dict

    def unpack(self):
        list = []
        for trip in self.newsletterCfg:
            trip_dict = {}
            start = trip['departure']
            end = trip['arrival']
            for dest in itertools.product(start, end):
                dest_name = "-".join(dest)
                trip_dict[dest_name] = trip['config']
            list.append(trip_dict)
        return list
