from django.urls import path

from sso2.portal.routes.home import home

urlpatterns = [
    path("tenant/<str:tenant_id>/home", home, name="home"),
]
