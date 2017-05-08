from django.conf.urls import url

from conflicto.api.v1.controllers.post_view import PostView
from conflicto.api.v1.controllers.reaction_view import ReactionView
from conflicto.api.v1.controllers.user_view import UserView

urlpatterns = [
    url(r'^user/authenticate$', UserView.as_view()),
    url(r'^post$', PostView.as_view()),
    url(r'^reaction$', ReactionView.as_view())
]
