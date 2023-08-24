import collections
import json
import random
import string
import time

Institution = collections.namedtuple("Institution", ["name", "guid"])
SharedSecret = collections.namedtuple("SharedSecret", ["name", "guid"])


class Config:
    def __init__(self, file_path="utility/config.json"):
        self.read_configuration(file_path)
        self.randomize_configuration()
        self.header = {
            "Host": self.url_endpoint,
            "Content-Type": self.content_type,
            "Authorization": self.authorization,
        }

    def randomize_configuration(self):
        self.external_meeting_id = "random-" + get_random_numeric_string(7)
        self.internal_meeting_id = (
            get_random_alpha_numeric_string(40) + "-" + str(round(time.time() * 1000))
        )
        self.record_id = self.internal_meeting_id
        self.internal_user_id = (
            get_random_alpha_string(1) + "_" + get_random_alpha_numeric_string(12)
        )

        index = random.choice([i for i in range(len(self.institutions))])
        self.institution = Institution(
            self.institutions[index]["name"], self.institutions[index]["guid"]
        )
        self.shared_secret = SharedSecret(
            self.shared_secrets[index]["name"], self.shared_secrets[index]["guid"]
        )

    def read_configuration(self, file_path):
        try:
            with open(file_path) as file:
                data = json.load(file)
                for key, value in data.items():
                    self.__setattr__(key, value)
        except RuntimeError:
            pass


def get_random_alpha_string(stringLength):
    letters = string.ascii_lowercase
    return "".join((random.choice(letters) for i in range(stringLength)))


def get_random_numeric_string(stringLength):
    digits = string.digits
    return "".join((random.choice(digits) for i in range(stringLength)))


def get_random_alpha_numeric_string(stringLength):
    lettersAndDigits = string.ascii_lowercase + string.digits
    return "".join((random.choice(lettersAndDigits) for i in range(stringLength)))
