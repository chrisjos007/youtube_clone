from .authentication import SafeJWTAuthentication
from rest_framework.decorators import authentication_classes
from .utils import (
    generate_access_token,
    get_username)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import (
    User,
    Comment,
    Subscription,
    View,
    Video,
    VideoLike)
from .serializers import (
    UserSerializer,
    ChannelSerializer,
    VideoSerializer,
    VideoHistorySerializer,
    UserdetailSerializer,
    UserUpdateSerializer,
    UserSubscriptionSerializer,
    VideoInfoSerializer,
    MyCommentSerializer,
    VideoUploadSerializer,
    UserSearchSerializers,
    VideoSearchSerializer)
from collections import defaultdict
from django.db.models import F, Count, Q
from django.db.models import (
    Case,
    When,
    Value,
    Exists,
    CharField)
from django.contrib.auth.hashers import (
    make_password,
    check_password)
from django.views.generic import View as ReactView
from django.http import HttpResponse
from django.conf import settings
import os


class ReactAppView(ReactView):
    '''
    To serve the react app
    '''

    def get(self, request):
        try:
            with open(os.path.join(
                settings.REACT_APP, 'build', 'index.html'
            )) as file:
                return HttpResponse(file.read())

        except FileNotFoundError:
            return HttpResponse(
                """
                index.html not found ! build your React app !!
                """,
                status=501,
            )


# we have not included signup with JWT authintication
# signup verifies the userdata creates the user and generates the JWT
# API for auth/signup
@api_view(['POST'])
def user_signup(request):
    ''' To create user account '''

    # Extracting User details from body
    firstname = request.data['firstname']
    lastname = request.data['lastname']
    username = request.data['username']
    email = request.data['email']
    password = request.data['password']
    password = make_password(password)
    # Checking If same Credentials are already present
    user_with_same_user_name = User.objects.filter(username=username)\
        .first()
    user_with_same_email = User.objects.filter(email=email).first()

    # If same username exists
    if user_with_same_user_name:
        # Returning response
        return Response({
            'success': 'false',
            'message': 'The user name is already taken'}, status=400)

    # If same email exists
    if user_with_same_email:
        # Returning response
        return Response({
            'success': 'false',
            'message': 'The email is already taken'}, status=400
        )
    # Creating user
    user = User(
        firstname=firstname,
        lastname=lastname,
        username=username,
        email=email,
        password=password)
    user.save()

    # Creating Token
    token = generate_access_token(user)

    # Returning response
    return Response({'success': 'true', 'data': token}, status=200)


# we have not included login with JWT authintication
# login verifies the email & pass and generates JWT
# API for auth/login
@api_view(['POST'])
def user_login_auth(request):
    '''
    Login the user from verified credentials
    '''

    # Extracting email and password from request body
    email = request.data['email']
    password = request.data['password']

    # Getting current user from DB
    user = User.objects.filter(email=email).first()

    # if user is not registered
    if not(user):
        return Response({
            'status': 'false',
            'message': 'The email is not yet registered'},
            status=400)

    # if password is incorrect
    if (not(check_password(password, user.password))):
        return Response({
            'status': 'false',
            'message': 'The password does not match'},
            status=400)

    # login(user)
    token = generate_access_token(user)

    # Returning response
    return Response({
        'success': 'true',
        'data': token},
        status=200)


# API for auth/me
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def me(request):
    # Extracting username from token
    username = get_username(request)

    # Getting logged in User from DB
    user = User.objects.values(
        'id', 'firstname', 'lastname', 'username', 'email', 'avatar', 'cover'
    ).filter(username=username).first()

    # Extracting channels subscribed by the logged in user
    channels = User.objects.values('id', 'username', 'avatar').\
        filter(id__in=(Subscription.objects.values_list(
            'subscribeTo', flat=True
        ).filter(subscriber=user['id'])
        ))

    # serializing queries for user and channel
    user_serialized = UserSerializer(user)
    channel_serialized = ChannelSerializer(channels, many=True)

    # creates a default dictionary to store serialized data
    out = defaultdict(dict)
    out['success'] = "true"
    out["data"] = user_serialized.data
    out["data"]["channels"] = channel_serialized.data

    # returning the serialized response
    return Response(out)


# API for /users
@api_view(['PUT', 'GET'])
@authentication_classes([SafeJWTAuthentication])
def user_update(request):
    '''
    API to update user details from given data
    '''
    # Extracting username from token
    username = get_username(request)

    # extracting current user
    current_user = User.objects.filter(username=username).first()

    # for editing profile
    if request.method == 'PUT':

        # Getting user info from request
        channelDescription = request.data['channelDescription']
        firstname = request.data['firstname']
        lastname = request.data['lastname']

        # getting avatar and cover of user
        current_avatar = current_user.avatar
        current_cover = current_user.cover

        # getting the avatar and cover from request of default
        avatar = request.data.get('avatar', current_avatar)
        cover = request.data.get('cover', current_cover)

        # updating user data
        current_user.channelDescription = channelDescription
        current_user.firstname = firstname
        current_user.lastname = lastname
        current_user.avatar = avatar
        current_user.cover = cover
        current_user.save()

        # Serializing User
        current_user = UserUpdateSerializer(current_user).data

        # Returning response
        return Response({"success": "true", "data": current_user})

    # for getting other users
    elif request.method == 'GET':

        # Getting all users except current user
        users = User.objects.exclude(username=username).\
            annotate(subscribersCount=Count('user_subscriptions')).\
            annotate(videosCount=Count('user_videos')).all()

        users = users.annotate(
            currentuser=Value(current_user.id, CharField())
        ).order_by('-createdAt')

        # Serializing User
        data = UserSubscriptionSerializer(users, many=True).data

        # Returning response
        return Response({"success": "true", "data": data})


# API for users/search
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def search_user(request):

    # Extracting username from token
    username = get_username(request)

    # extracting current user
    current_user = User.objects.filter(username=username).first()

    # Getting search word of user from url
    searchterm = request.GET['searchterm']

    # getting matched results for user from DB
    search_result = User.objects.filter(
        Q(
            username__icontains=searchterm
        ) | Q(
            firstname__icontains=searchterm
        ) | Q(
            lastname__icontains=searchterm
        )
    )

    search_result = search_result.annotate(videosCount=Count('user_videos')).\
        annotate(subscribersCount=Count('user_subscriptions')).\
        annotate(
            isMe=Case(
                When(username=username,
                     then=Value('true')
                     ),
                default=Value('false'),
                output_field=CharField())).\
        annotate(currentuser=Value(current_user.id, CharField())).\
        order_by('-createdAt')

    # Serializing Data
    data = UserSearchSerializers(search_result, many=True).data

    # Returning response
    return Response({"success": 'true', "data": data})


# API for users/feed'
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def feed(request):

    # Extracting username from token
    username = get_username(request)

    # Extracting the current User
    current_user = User.objects.filter(username=username).first()

    # Extracting the Users whom Current User Subrscribed
    user_ids = Subscription.objects.values('subscribeTo').\
        filter(subscriber=current_user.id)

    # Getting Videos for subscribed Users
    videos = Video.objects.filter(User_id__in=user_ids).\
        annotate(views=Count('video_views')).\
        annotate(userId=F('User_id')).order_by('-createdAt')

    # Serializing Videos data
    subscribed_video_feeds = VideoSerializer(videos, many=True).data

    # Returning response
    return Response({"success": "true", "data": subscribed_video_feeds})


# Api for users/history
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def history(request):

    # Extracting username from token
    username = get_username(request)

    # Getting Current User
    current_user = User.objects.filter(username=username).first()

    # Getting videos watched by Current User
    videos = Video.objects.filter(
        video_views__in=(View.objects.filter(user=current_user))).\
        annotate(views=Count('video_views')).order_by('-createdAt')

    # Serializing Watched Videos
    videos_history = VideoHistorySerializer(videos, many=True).data

    # Returning response
    return Response({"success": "true", "data": videos_history})


# API for users/likedVideos
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def liked_videos(request):

    # Extracting username from token
    username = get_username(request)

    # extracting current user
    current_user = User.objects.filter(username=username).first()

    # extracting liked videos by current user
    likedvideo_object = Video.objects.filter(
        likes__in=(VideoLike.objects.filter(user=current_user, like__gte=1))).\
        annotate(views=Count('video_views')).order_by('-createdAt')

    # serializing liked videos
    likedvideo_serialized = VideoHistorySerializer(
        likedvideo_object, many=True).data

    # returning the response
    return Response({"success": "true", "data": likedvideo_serialized})


# API for users/<str:id>/togglesubscribe
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def toggle_subscribe(request, id):

    # Extracting username from token
    username = get_username(request)

    # extracting current user
    current_user = User.objects.filter(username=username).first()

    # extracting the user from URL
    other_user = User.objects.filter(id=id).first()

    # extracting current users all susbscriptions
    subscriptions_of_current = Subscription.objects.filter(
        subscriber=current_user.id
    )

    # Checking if other user is already susbscribed
    flag = True
    for user in subscriptions_of_current:
        if user.subscribeTo.id == other_user.id:
            flag = False
            # if other user is subscribed delete the user
            user.delete()

    if flag:
        # if other user is not subscribed then subscribe him
        subscribing = Subscription(
            subscriber=current_user.id, subscribeTo=other_user
        )
        subscribing.save()

    # Returning response
    return Response({"success": "true", "data": {}})


# API for users/<str:id>
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def user_details(request, id):

    # Extracting username from token
    username = get_username(request)

    # Getting current User
    current_user = User.objects.filter(username=username).first()

    # Getting User by Id
    user = User.objects.filter(id=id).\
        annotate(
            isMe=Case(
                When(username=username, then=Value('true')),
                default=Value('false'),
                output_field=CharField())).\
        annotate(subscribersCount=Count('user_subscriptions'))

    user = user.annotate(
        isSubscribed=Exists(
            Subscription.objects.filter(
                subscriber=current_user.id).filter(
                    subscribeTo=user[0]))).first()

    # Serializing user data
    data = UserdetailSerializer(user).data

    # Returning response
    return Response({"success": "true", "data": data})


# API for /videos
@api_view(['GET', 'POST'])
@authentication_classes([SafeJWTAuthentication])
def videos(request):

    # Extracting username from token
    username = get_username(request)

    # extracting current user
    current_user = User.objects.filter(username=username).first()

    if request.method == 'GET':
        # Getting All Videos
        videos = Video.objects.annotate(
            views=Count('video_views')).\
            annotate(userId=F('User_id')).\
            order_by('-createdAt')

        # Serializing Videos Data
        video_on_home = VideoSerializer(videos, many=True).data

        # Returning Response
        return Response({"success": "true", "data": video_on_home})

    elif request.method == 'POST':
        # Extracting data for Video instance in DB
        description = request.data.get('description')
        thumbnail = request.data.get('thumbnail')
        url = request.data.get('url')
        title = request.data.get('title')

        # Creating Video Instance
        video_uploaded = Video(
            title=title,
            description=description,
            url=url,
            thumbnail=thumbnail,
            User=current_user
        )
        video_uploaded.save()

        # Getting Video posted with some additional fields
        video = Video.objects.filter(id=video_uploaded.id).\
            annotate(userId=Value(current_user.id, CharField())).first()

        # Serializing Video object
        video_serialized = VideoUploadSerializer(video).data

        # Returning Response
        return Response({"success": "true", "data": video_serialized})


# API for videos/search
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def search_video(request):

    # Getting search word of user from url
    searchterm = request.GET['searchterm']

    # getting matched results for user from DB
    search_result = Video.objects.filter(Q(title__icontains=searchterm))

    search_result = search_result.annotate(userId=F('User_id')).\
        order_by('-createdAt')

    # Serializing data
    data = VideoSearchSerializer(search_result, many=True).data

    # Returning response
    return Response({"success": 'true', "data": data})


# API for videos/<str:id>
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def videos_details(request, id):

    # Extracting username from token
    username = get_username(request)

    # Getting current user
    current_user = User.objects.filter(username=username).first()

    # getting video by id from url
    video = Video.objects.filter(id=id).\
        annotate(
            isVideoMine=Case(When(User_id=current_user.id, then=Value('true')),
                             default=Value('false'),
                             output_field=CharField())).\
        annotate(views=Count('video_views')).annotate(userId=F('User_id'))

    video = video.\
        annotate(
            isSubscribed=Exists(
                Subscription.objects.filter(
                    subscriber=current_user.id
                ).filter(subscribeTo=video[0].User))).\
        annotate(
            isViewed=Exists(
                View.objects.filter(
                    user=current_user
                ).filter(video=video[0]))).\
        annotate(
            isLiked=Exists(
                VideoLike.objects.filter(
                    video=video[0]
                ).filter(user=current_user).filter(like=1))).\
        annotate(
            isDisliked=Exists(
                VideoLike.objects.filter(
                    video=video[0]
                ).filter(user=current_user).filter(like=-1)))

    video_viewed = View(video=video[0], user=current_user)
    video_viewed.save()

    # Serializing Data
    out = (VideoInfoSerializer(video.first()).data)

    # Returning response
    return Response({"success": 'true', "data": out})


# API for videos/<str:id>/view
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def video_viewed_or_not(request, id):
    return Response({"success": 'true', "data": {}})


# API for videos/<str:video_id>/like
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def toggle_like(request, video_id):

    # Extracting username from token
    username = get_username(request)

    # extracting current user
    current_user = User.objects.filter(username=username).first()

    # extracting video
    video = Video.objects.filter(id=video_id).first()

    is_disliked = VideoLike.objects.filter(
        video_id=video_id, user=current_user).filter(like=-1).first()
    if is_disliked:
        is_disliked.delete()

    # extracting the video like for video_id
    is_liked = VideoLike.objects.filter(
        video_id=video_id, user=current_user).filter(like=1).first()

    # if not liked like else delete like
    if not is_liked:
        like_video = VideoLike(
            like=1,
            video=video,
            user=current_user
        )
        like_video.save()
    else:
        is_liked.delete()

    # Returning response
    return Response({"success": "true", "data": {}})


# API for videos/<str:video_id>/dislike
@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
def toggle_dislike(request, video_id):

    # Extracting username from token
    username = get_username(request)

    # extracting current user
    current_user = User.objects.filter(username=username).first()

    # extracting video
    video = Video.objects.filter(id=video_id).first()

    is_liked = VideoLike.objects.filter(
        video_id=video_id, user=current_user).filter(like=1).first()
    if is_liked:
        is_liked.delete()

    # extracting the video like for video_id
    is_disliked = VideoLike.objects.filter(
        video_id=video_id, user=current_user).filter(like=-1).first()

    # if not liked like else delete like
    if not is_disliked:
        like_video = VideoLike(
            like=-1,
            video=video,
            user=current_user
        )
        like_video.save()
    else:
        is_disliked.delete()

    # Returning response
    return Response({"success": "true", "data": {}})


# API for videos/<str:id>/comment
@api_view(['POST'])
@authentication_classes([SafeJWTAuthentication])
def comment_view(request, id):

    # Extracting username from token
    username = get_username(request)

    # extracting current user
    current_user = User.objects.filter(username=username).first()

    # Getting comment text
    text = request.data.get('text')

    # getting the current video
    current_video = Video.objects.filter(id=id).\
        annotate(userId=F('User_id')).first()

    # Adding comment on video
    comment_by_user = Comment(
        text=text,
        video=current_video,
        user=current_user
    )
    comment_by_user.save()

    # Getting comment with some additional fields
    comment = Comment.objects.filter(id=comment_by_user.id).\
        annotate(userId=Value(current_user.id, CharField())).\
        annotate(videoId=Value(current_video.id, CharField())).first()

    # Serializing Comment data
    data = MyCommentSerializer(comment).data

    # Returning response
    return Response({"success": 'true', "data": data})
