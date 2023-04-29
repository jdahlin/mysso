from django.contrib import admin
from django.urls import include, path
from two_factor.urls import urlpatterns as tf_urls

admin.autodiscover()


urlpatterns = [
    path("", include("sso2.core.urls")),
    path("", include("sso2.oauth.urls")),
    path("", include("sso2.portal.urls")),
    path("", include(tf_urls)),
    path("admin/", admin.site.urls),
]
