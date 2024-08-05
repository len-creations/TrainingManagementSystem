from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
import time

class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.password)
        )

    def check_token(self, user, token):
        # Check if the token is expired (default 1 hour expiration)
        expiration_time = 3600  # 1 hour in seconds
        token_is_valid = super().check_token(user, token)
        if not token_is_valid:
            return False

        # Check for expiration based on last login timestamp
        current_time = time.time()
        last_login_time = user.last_login.timestamp() if user.last_login else current_time
        return (current_time - last_login_time) < expiration_time

token_generator = CustomPasswordResetTokenGenerator()
