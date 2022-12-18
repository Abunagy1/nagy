from django.apps import AppConfig
from django.conf import settings
#from django.contrib.auth.models import User
from django.db.models.signals import post_save
#from django.utils.translation import ugettext_lazy as _ # for < 3.2 version
from django.utils.translation import gettext_lazy as _
class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
    verbose_name = _('account')
    verbose_name_plural = _('accounts')
    # we use the next signal ready fn if we have custom abstract user only or other app not related to the 
    # auth user that already registered in relation to profile in the same app account
    def ready(self):
        from . import signals
        import account.signals
        #post_save.connect(signals.create_profile, sender=User, weak=False, dispatch_uid='Profile')
        #post_save.connect(signals.create_user_profile, sender=User, weak=False, dispatch_uid='Profile') 
        # post_save is built-in signal connected to create_profile reciver fn)
        # dispatch_uid: a unique identifier as the dispatch_uid argument to identify your receiver function
        # post save is an internal signal & create_user_profile is the callback function that has been called 
        # sender is the user class model, weak = false to not make the callback as garbage collected and uid for no duplication
