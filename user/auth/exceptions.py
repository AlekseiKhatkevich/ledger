class UserAuthException(Exception):
    pass

class DuplicateUserException(UserAuthException):
    def __init__(self, *args, message):
        super().__init__(*args)
        self.message = message