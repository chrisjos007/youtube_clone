from django.contrib import admin
from .models import User, Subscription, View, Comment, VideoLike, Video
from django_admin_listfilter_dropdown.filters import DropdownFilter

# Register your models here.


# User Model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "firstname", "lastname")
    list_filter = [
        ("email", DropdownFilter),
    ]
    search_fields = (
        "email__startswith",
        "username__startswith"
    )


# Video Model
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "uname",)
    list_filter = [
        ("title", DropdownFilter),
        ("User__username", DropdownFilter)
    ]
    search_fields = (
        "title__startswith",
        "User__username__startswith"
    )

    def uname(self, obj):
        u = obj.User.username
        return u


# VideoLike Model
@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ("title", 'username')
    list_filter = [
        ("video__title", DropdownFilter),
        ("user__username", DropdownFilter)
    ]
    search_fields = (
        "video__title__startswith",
    )

    def title(self, obj):
        t = obj.video.title
        return t

    def username(self, obj):
        u = obj.user.username
        return u


# Subscription Model
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber_name', 'subscribeto_name')
    list_filter = [
        ("subscribeTo__username", DropdownFilter)
    ]
    search_fields = (
        "subscribeTo__username__startswith",
    )

    def subscriber_name(self, obj):
        u = User.objects.get(pk=obj.subscriber)
        return u.username

    def subscribeto_name(self, obj):
        u = obj.subscribeTo.username
        return u


# Comment Model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("title", "username")
    list_filter = [
        ("video__title", DropdownFilter),
        ("user__username", DropdownFilter)
    ]
    search_fields = (
        "video__title__startswith",
        "user__username__startswith"
    )

    def title(self, obj):
        t = obj.video.title
        return t

    def username(self, obj):
        u = obj.user.username
        return u


# View Model
@admin.register(View)
class ViewAdmin(admin.ModelAdmin):
    list_display = ("title", "username")
    list_filter = [
        ("video__title", DropdownFilter),
        ("user__username", DropdownFilter)
    ]
    search_fields = (
        "video__title__startswith",
        "user__username__startswith"
    )

    def title(self, obj):
        t = obj.video.title
        return t

    def username(self, obj):
        u = obj.user.username
        return u
