from django.urls import path
from .views import (user_signup, user_login_auth, me, videos,
                    feed, history, user_details, liked_videos,
                    toggle_subscribe, toggle_like, toggle_dislike,
                    user_update, videos_details, comment_view,
                    search_user, search_video, video_viewed_or_not,
                    ReactAppView)
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    # React view
    path('', ReactAppView.as_view()),
    # authentication views
    path('auth/signup', csrf_exempt(user_signup), name='signup'),
    path('auth/login', csrf_exempt(user_login_auth), name='login'),
    path('auth/me', csrf_exempt(me), name='me'),
    # /users
    path('users', csrf_exempt(user_update), name='user_update'),
    path('users/search', csrf_exempt(search_user), name='search_user'),
    path('users/feed', csrf_exempt(feed), name='feed'),
    path('users/history', csrf_exempt(history), name='history'),
    path('users/likedVideos', csrf_exempt(liked_videos), name='liked_videos'),
    path('users/<str:id>/togglesubscribe',
         csrf_exempt(toggle_subscribe), name='toggle_subscribe'),
    path('users/<str:id>', csrf_exempt(user_details), name='user_details'),
    # /videos
    path('videos', csrf_exempt(videos), name='videos'),
    path('videos/search', csrf_exempt(search_video), name='search_video'),
    path('videos/<str:id>', csrf_exempt(videos_details),
         name='videos_details'),
    path('videos/<str:id>/view', csrf_exempt(video_viewed_or_not),
         name='videos_viewed_or_not'),
    path('videos/<str:video_id>/like',
         csrf_exempt(toggle_like), name='toggle_like'),
    path('videos/<str:video_id>/dislike',
         csrf_exempt(toggle_dislike), name='toggle_dislike'),
    path('videos/<str:id>/comment', csrf_exempt(comment_view),
         name='comment_view'),
]
