from django.contrib import admin

# Register your models here.

from .models import User, Posts, Likes, Follows

class LikesAdmin(admin.ModelAdmin):
    filter_horizontal = ("posts",)

class FollowsAdmin(admin.ModelAdmin):
    filter_horizontal = ("follows",)

admin.site.register(User)
admin.site.register(Posts)
admin.site.register(Likes, LikesAdmin)
admin.site.register(Follows, FollowsAdmin)