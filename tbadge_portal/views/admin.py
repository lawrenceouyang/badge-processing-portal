from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.conf import settings
from tbadge_portal.views.error import validate_api_call
from tbadge_portal.views.login import admin_login_required
import requests
import json
from datetime import datetime
import calendar
import logging

logger = logging.getLogger(__name__)


@admin_login_required
def admin_statistics(request):
    if request.method == 'GET':
        stat_history = {"data": []}
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        if request.GET.get("type") is not None and request.GET.get("value") is not None:
            stats_type = int(request.GET.get("type"))
            value = int(request.GET.get("value"))
            # By MONTH: VALUE/YEAR #
            if stats_type == 1:
                year = int(request.GET.get("year"))
                # CURRENT MONTH: PARTIAL DAYS #
                if value == today.month and year == today.year:
                    for i in range(today.day - 1, -1, -1):
                        cur_day = datetime(today.year, today.month, today.day - i)
                        cur_day_start = cur_day
                        cur_day_end = cur_day.replace(hour=23, minute=59, second=59)
                        cur_day_start = cur_day_start.strftime("%Y-%m-%d %H:%M:%S")
                        cur_day_end = cur_day_end.strftime("%Y-%m-%d %H:%M:%S")
                        cur_day = cur_day.strftime("%m/%d")

                        response = requests.get("{}/badge/temp_badge/status/summary?from={}&to={}".
                                                format(settings.TBADGE_WS_URL, cur_day_start, cur_day_end))
                        validate_api_call(response, [404])
                        if response.status_code == 404:
                            data = {"data": []}
                        else:
                            data = json.loads(response.text)
                        stat_history["data"].append({cur_day: data["data"]}.copy())
                    return JsonResponse(stat_history, safe=False)

                # OTHER MONTH: ALL DAYS #
                else:
                    for i in range(1, calendar.monthrange(year, value)[1] + 1):
                        cur_day = datetime(year, value, i)
                        cur_day_start = cur_day
                        cur_day_end = cur_day.replace(hour=23, minute=59, second=59)
                        cur_day_start = cur_day_start.strftime("%Y-%m-%d %H:%M:%S")
                        cur_day_end = cur_day_end.strftime("%Y-%m-%d %H:%M:%S")
                        cur_day = cur_day.strftime("%m/%d")

                        response = requests.get("{}/badge/temp_badge/status/summary?from={}&to={}".
                                                format(settings.TBADGE_WS_URL, cur_day_start, cur_day_end))
                        validate_api_call(response, [404])
                        if response.status_code == 404:
                            data = {"data": []}
                        else:
                            data = json.loads(response.text)
                        stat_history["data"].append({cur_day: data["data"]}.copy())
                    return JsonResponse(stat_history, safe=False)

            # BY YEAR: VALUE #
            elif stats_type == 2:
                # $CURRENT_YEAR: PARTIAL YEAR #
                if value == today.year:
                    for i in range(1, today.month + 1):
                        cur_day = datetime(today.year, i, 1)
                        cur_day_start = cur_day
                        cur_day_end = cur_day.replace(day=calendar.monthrange(today.year, i)[1],
                                                      hour=23, minute=59, second=59)
                        cur_day_start = cur_day_start.strftime("%Y-%m-%d %H:%M:%S")
                        cur_day_end = cur_day_end.strftime("%Y-%m-%d %H:%M:%S")
                        cur_day = cur_day.strftime("%m/%Y")

                        response = requests.get("{}/badge/temp_badge/status/summary?from={}&to={}".
                                                format(settings.TBADGE_WS_URL, cur_day_start, cur_day_end))
                        validate_api_call(response, [404])
                        if response.status_code == 404:
                            data = {"data": []}
                        else:
                            data = json.loads(response.text)
                        stat_history["data"].append({cur_day: data["data"]}.copy())
                    return JsonResponse(stat_history, safe=False)
                # OTHER YEAR: FULL YEAR #
                else:
                    for i in range(1, 13):
                        cur_day = datetime(value, i, 1)
                        cur_day_start = cur_day
                        cur_day_end = cur_day.replace(day=calendar.monthrange(value, i)[1],
                                                      hour=23, minute=59, second=59)
                        cur_day_start = cur_day_start.strftime("%Y-%m-%d %H:%M:%S")
                        cur_day_end = cur_day_end.strftime("%Y-%m-%d %H:%M:%S")
                        cur_day = cur_day.strftime("%m/%Y")
                        response = requests.get("{}/badge/temp_badge/status/summary?from={}&to={}".
                                                format(settings.TBADGE_WS_URL, cur_day_start, cur_day_end))
                        validate_api_call(response, [404])
                        if response.status_code == 404:
                            data = {"data": []}
                        else:
                            data = json.loads(response.text)
                        stat_history["data"].append({cur_day: data["data"]}.copy())
                    return JsonResponse(stat_history, safe=False)

        # DEFAULT: CURRENT MONTH #
        for i in range(today.day - 1, -1, -1):
            cur_day = datetime(today.year, today.month, today.day - i)
            cur_day_start = cur_day
            cur_day_end = cur_day.replace(hour=23, minute=59, second=59)
            cur_day_start = cur_day_start.strftime("%Y-%m-%d %H:%M:%S")
            cur_day_end = cur_day_end.strftime("%Y-%m-%d %H:%M:%S")
            cur_day = cur_day.strftime("%m/%d")

            response = requests.get("{}/badge/temp_badge/status/summary?from={}&to={}".
                                    format(settings.TBADGE_WS_URL, cur_day_start, cur_day_end))
            validate_api_call(response, [404])
            if response.status_code == 404:
                data = {"data": []}
            else:
                data = json.loads(response.text)
            stat_history["data"].append({cur_day: data["data"]}.copy())
        return render(request, "tbadge_portal/admin/statistics.html", {"stats": json.dumps(stat_history)})
    else:
        raise Http404
