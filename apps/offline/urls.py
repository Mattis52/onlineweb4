# -*- encoding: utf-8 -*-

from django.conf.urls import url

# API v1

from apps.api.utils import SharedAPIRootRouter
from apps.offline import views


urlpatterns = [
    url(r'^$', views.main, name='offline')
]


router = SharedAPIRootRouter()
router.register('offline', views.OfflineIssueViewSet)
