class ZfoUtils:
    @staticmethod
    def md5(str: str):
        import hashlib
        m = hashlib.md5()
        m.update(str.encode("utf8"))
        return m.hexdigest()