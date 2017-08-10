from django.conf.urls import url
from tbadge_portal.views import login, admin, applicant, badge

urlpatterns = [

    # Login/Out Pages
    url(r'^$', login.login, name='login'),
    url(r'^logout/$', login.logout, name='logout'),

    # Applicant Pages
    url(r'^applicant/lookup/$', applicant.applicant_lookup, name='applicant_lookup'),
    url(r'^applicant/lookup/results/$', applicant.applicant_results, name='applicant_results'),
    url(r'^applicant/(?P<applicant_id>[\w\-]+)/$', applicant.applicant_view, name='applicant_view'),

    # Escort Pages
    url(r'^escort/results/$', badge.badge_escort_results, name='badge_escort_results'),
    url(r'^escort/convert/$', badge.badge_escort_csn_to_upid, name='badge_escort_csn_to_upid'),
    url(r'^escort/(?P<escort_upid>[\w\-]+)/$', badge.badge_escort_view, name='badge_escort_view'),
    url(r'^escort/csn/(?P<escort_csn>[\w\-]+)/$', badge.badge_csn_escort_view, name='badge_csn_escort_view'),

    # Badge Pages
    url(r'^badge/lookup/$', badge.badge_lookup, name='badge_lookup'),
    url(r'^badge/lookup/results/$', badge.badge_results, name='badge_results'),
    url(r'^badge/issue/$', badge.badge_issue, name='badge_issue'),
    url(r'^badge/return/$', badge.badge_return, name='badge_return'),
    url(r'^badge/list/$', badge.badge_list, name='badge_list'),
    url(r'^badge/(?P<badge_id>[\w\-]+)/$', badge.badge_view, name='badge_view'),
    url(r'^badge/(?P<badge_id>[\w\-]+)/view/$', badge.badge_view_only, name='badge_view_only'),
    url(r'^badge/(?P<badge_id>[\w\-]+)/history$', badge.badge_history, name='badge_history'),

    # Statistics Page
    url(r'^admin/statistics/$', admin.admin_statistics, name='admin_statistics')

]

# Error views
handler404 = 'tbadge_portal.views.error.tbadge_page_not_found'
handler500 = 'tbadge_portal.views.error.tbadge_server_error'
handler403 = 'tbadge_portal.views.error.tbadge_permission_denied'
handler400 = 'tbadge_portal.views.error.tbadge_bad_request'
