from django.db import InternalError
from django.shortcuts import render

import logging

logger = logging.getLogger(__name__)


def tbadge_page_not_found(request):
    return render(request, "tbadge_portal/error/error.html", {"error_message": "404 Page Not Found"})


def tbadge_server_error(request):
    return render(request, "tbadge_portal/error/error.html", {"error_message": "500 Internal Server Error"})


def tbadge_permission_denied(request):
    return render(request, "tbadge_portal/error/error.html", {"error_message": "403 Forbidden"})


def tbadge_request(request):
    return render(request, "tbadge_portal/error/error.html", {"error_message": "400 Bad Request"})


def validate_api_call(response, exceptions):
    if (response.status_code < 200 or response.status_code > 299) and response.status_code not in exceptions:
        logger.exception("status_code={} message= WS URI '{}' returned a status code '{}' which was not in the "
                         "exceptions list.".format(response.status_code, response.request.url, response.status_code))
        raise InternalError("TBadge Webservice Status Code Error. Status Code {}".format(response.status_code))
