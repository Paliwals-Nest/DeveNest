import json


class slack_configure:

    def __init__(self):
        try:
            with open("slack_config.json") as config:
                data = json.loads(config.read())
                self.token = data.get('slack_token')
                self.secret = data.get('slack_signing_secret')
        except FileNotFoundError as e:
            print("Can't read slack token and slack secret {}".format(e))

    def return_slack_config(self):
        return self.token, self.secret


if __name__ == '__main__':
    slack_configure()
