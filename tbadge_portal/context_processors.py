from django.conf import settings


# noinspection PyUnusedLocal
def version_number(request):
    return {'VERSION': settings.VERSION}


# noinspection PyUnusedLocal
def webservice_url(request):
    return {'TBADGE_WS_URL': settings.TBADGE_WS_URL}


# noinspection PyUnusedLocal
def under_construction(request):
    return {'UNDER_CONSTRUCTION': settings.UNDER_CONSTRUCTION}
