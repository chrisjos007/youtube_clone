from rest_framework import serializers
from .models import (
    User,
    Subscription,
    View,
    Comment,
    VideoLike)


# Serializer for auth/me
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'firstname',
            'lastname',
            'username',
            'email',
            'avatar',
            'cover'
        )


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar'
        )


# Serializer for /videos and /feed and /likedvideos
class UserVideoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    avatar = serializers.CharField(max_length=300)
    username = serializers.CharField(max_length=255)


# serializer for /videos and /feed
class VideoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    thumbnail = serializers.CharField(max_length=300)
    createdAt = serializers.DateTimeField()
    userId = serializers.UUIDField()
    User = UserVideoSerializer()
    views = serializers.IntegerField()


# Serializer for /history for /likedvideos
class VideoHistorySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    thumbnail = serializers.CharField(max_length=300)
    createdAt = serializers.DateTimeField()
    url = serializers.CharField(max_length=300)
    User = UserVideoSerializer()
    views = serializers.IntegerField()


class UserChannelSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=255)
    avatar = serializers.CharField(max_length=255)
    subscribersCount = serializers.SerializerMethodField(
        'subcount',
        source='user_subscriptions')

    def subcount(self, main_object):
        counts = Subscription.objects.filter(subscribeTo=main_object).count()
        return counts


class UserVideoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    thumbnail = serializers.CharField(max_length=300)
    createdAt = serializers.DateTimeField()
    url = serializers.CharField(max_length=300)
    views = serializers.SerializerMethodField('view', source='video_views')

    def view(self, main_object):
        counts = View.objects.filter(video=main_object).count()
        return counts


class UserdetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    channels = serializers.SerializerMethodField(
        'channel',
        source='user_subscriptions'
    )
    avatar = serializers.CharField(max_length=300)
    firstname = serializers.CharField(max_length=300)
    lastname = serializers.CharField(max_length=300)
    cover = serializers.CharField(max_length=300)
    email = serializers.CharField(max_length=300)
    channelDescription = serializers.CharField(max_length=300)

    subscribersCount = serializers.IntegerField()
    isMe = serializers.BooleanField()
    isSubscribed = serializers.BooleanField()
    username = serializers.CharField(max_length=255)
    videos = UserVideoSerializer(many=True, source='user_videos')

    def channel(self, main_object):
        query = User.objects.filter(
            user_subscriptions__in=(
                Subscription.objects.filter(subscriber=main_object.id)
            )).order_by('-createdAt')
        return (UserChannelSerializer(query, many=True).data)


# Serializer for /users updating user profile
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'firstname',
            'lastname',
            'channelDescription',
            'username',
            'email',
            'avatar',
            'cover'
        )


class UserSubscriptionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=255)
    avatar = serializers.CharField(max_length=255)
    subscribersCount = serializers.IntegerField()
    isSubscribed = serializers.SerializerMethodField('subscribed')
    videosCount = serializers.IntegerField()

    def subscribed(self, main_object):
        is_subscribed = Subscription.objects.filter(
            subscriber=main_object.currentuser
        ).filter(subscribeTo=main_object)
        if is_subscribed:
            return True
        else:
            return False


class UserVideoInfoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=255)
    avatar = serializers.CharField(max_length=300)


class CommentVideoInfoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    createdAt = serializers.DateTimeField()
    text = serializers.CharField(max_length=500)
    User = UserVideoInfoSerializer(source='user')


class VideoInfoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    thumbnail = serializers.CharField(max_length=300)
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()
    url = serializers.CharField(max_length=300)
    isVideoMine = serializers.BooleanField()
    isSubscribed = serializers.BooleanField()
    isViewed = serializers.BooleanField()
    isLiked = serializers.BooleanField()
    isDisliked = serializers.BooleanField()
    userId = serializers.UUIDField()
    User = UserVideoInfoSerializer()
    comments = CommentVideoInfoSerializer(many=True)
    views = serializers.SerializerMethodField('view')
    subscribersCount = serializers.SerializerMethodField('subcount')
    commentsCount = serializers.SerializerMethodField('cmtcount')
    likesCount = serializers.SerializerMethodField('likecount')
    dislikesCount = serializers.SerializerMethodField('dislikecount')

    def view(self, main_object):
        counts = View.objects.filter(video=main_object).count()
        return counts

    def subcount(self, main_object):
        count = Subscription.objects.filter(
            subscribeTo=main_object.User).count()
        return count

    def cmtcount(self, main_object):
        count = Comment.objects.filter(video=main_object).count()
        return count

    def likecount(self, main_object):
        count = VideoLike.objects.filter(
            video=main_object).filter(like=1).count()
        return count

    def dislikecount(self, main_object):
        count = VideoLike.objects.filter(
            video=main_object).filter(like=-1).count()
        return count


class MyCommentSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    text = serializers.CharField(max_length=500)
    userId = serializers.UUIDField()
    videoId = serializers.UUIDField()
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()
    User = UserVideoInfoSerializer(source='user')


class VideoUploadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    url = serializers.CharField(max_length=300)
    thumbnail = serializers.CharField(max_length=300)
    userId = serializers.UUIDField()


class UserSearchSerializers(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=255)
    avatar = serializers.CharField(max_length=300)
    channelDescription = serializers.CharField(max_length=300)
    subscribersCount = serializers.IntegerField()
    videosCount = serializers.IntegerField()
    isSubscribed = serializers.SerializerMethodField('subscribed')
    isMe = serializers.BooleanField()

    def subscribed(self, main_object):
        is_subscribed = Subscription.objects.filter(
            subscriber=main_object.currentuser
        ).filter(subscribeTo=main_object)
        if is_subscribed:
            return True
        else:
            return False


class VideoSearchSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)
    url = serializers.CharField(max_length=300)
    thumbnail = serializers.CharField(max_length=300)
    userId = serializers.UUIDField()
    createdAt = serializers.DateTimeField()
    updatedAt = serializers.DateTimeField()
    User = UserVideoInfoSerializer()
