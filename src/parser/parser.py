from sys import argv


class Parser:
    def parse_argument(self):
        if not argv[1].endswith(".json"):
            print("error the config file is not json format")