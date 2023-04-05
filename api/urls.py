from django.urls import include, path

from .views import MemberCount, MemberAdvancedCount

urlpatterns = [
    path("members/count/", MemberCount.as_view()),
    path("members/count/advanced/", MemberAdvancedCount.as_view()),
]
