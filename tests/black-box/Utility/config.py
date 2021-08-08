import string
import random

class Config:
    def __init__(self, file_path="Utility/config.cfg"):
        self.randomize_configuration()
        self.read_configuration(file_path)
        self.header = {'HOST': self.url_endpoint, 'CONTENT-TYPE': self.content_type, 'AUTHORIZATION': self.authorization}

    def randomize_configuration(self):
        self.internal_meeting_id = get_random_alpha_numeric_string(40) + "-" + get_random_alpha_numeric_string(13)
        self.record_id = get_random_alpha_numeric_string(40) + "-" + get_random_alpha_numeric_string(13)
        self.external_meeting_id = "random-" + get_random_numeric_string(7)
        self.internal_user_id = get_random_alpha_string(1) + "_" + get_random_alpha_numeric_string(12)
        
    def read_configuration(self, file_path):
        try:
            with open(file_path) as file:
                for line in file:
                    attributes = line.split('=')
                    self.__setattr__(attributes[0], attributes[1].replace('"', '').replace('\n', ''))
        except:
            pass


def get_random_alpha_string(stringLength):
    letters = string.ascii_lowercase
    return ''.join((random.choice(letters) for i in range(stringLength)))

def get_random_numeric_string(stringLength):
    digits = string.digits
    return ''.join((random.choice(digits) for i in range(stringLength)))

def get_random_alpha_numeric_string(stringLength):
    lettersAndDigits = string.ascii_lowercase + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))
