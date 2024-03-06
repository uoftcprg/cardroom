from django.dispatch import Signal

post_state_construction = Signal()
pre_state_destruction = Signal()
