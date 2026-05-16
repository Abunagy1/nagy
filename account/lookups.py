from ajax_select import register, LookupChannel
from django.contrib.auth import get_user_model

User = get_user_model()

@register('postman_users')
class PostmanUsersLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        return self.model.objects.filter(
            username__icontains=q, is_active=True
        ).order_by('username')

    def format_item_display(self, item):
        return f"{item.username} ({item.get_full_name()})"