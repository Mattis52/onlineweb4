# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.events.dashboard import views

urlpatterns = [
    url(r'^$', views.index, name='dashboard_events_index'),
    url(r'^past$', views.past, name='dashboard_events_past'),

    url(r'^create/$', views.create_event, name='dashboard_event_create'),
    url(r'^edit/(?P<event_id>\d+)/$', views.edit_event, name='dashboard_event_edit'),

    # details views
    url(r'^(?P<event_id>\d+)/$', views.event_details, name='dashboard_event_details'),
    # url endpoints for saving forms
    url(r'^(?P<event_id>\d+)/attendance/$', views.event_change_attendance, name='dashboard_event_change_attendance'),
    url(r'^(?P<event_id>\d+)/reservation/$', views.event_change_reservation, name='dashboard_event_change_reservation'),
    # catch-all for other tabs
    url(r'^(?P<event_id>\d+)/(?P<active_tab>\w+)/$', views.event_details, name='dashboard_event_details_active'),


    url(r'^attendee/(?P<attendee_id>\d+)/$', views.attendee_details, name='dashboard_attendee_details'),
]
