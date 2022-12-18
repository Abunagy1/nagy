from django.dispatch import Signal

message_sent = Signal() # it was Signal(providing_args=["message", "thread", "reply"]) but no providing_args in DJ 4
