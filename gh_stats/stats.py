from collections import Counter


class Statblock:
    def __init__(self) -> None:
        self.username = ""
        self.count = 0

        self.month_count = 0
        self.month = ""  # String so it can hold leading zeros
        self.month_name = ""

        self.projects: Counter[str] = Counter()

        self.new_repo_count = 0

    def get_most_common_repo(self) -> tuple[str, int]:
        (ret,) = self.projects.most_common(1)
        return ret
