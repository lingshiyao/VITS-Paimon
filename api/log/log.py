from api.app_constance import AppConstance


class Log:
    @staticmethod
    def print(*kwargs):
        if AppConstance.DEBUG:
            print(kwargs)
