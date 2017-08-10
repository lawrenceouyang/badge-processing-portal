from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages

from django.http import Http404, JsonResponse
from tbadge_portal.forms import DateSearchForm, BadgeQueryForm, PersonSearchForm, CreateRequestForm, CreateLimitedIssuanceForm, CreateStandardIssuanceForm
from tbadge_portal.views.error import validate_api_call
from tbadge_portal.views.login import admin_login_required, login_required
from tbadge_portal.helpers import hashid
from datetime import datetime, timedelta
import tbadge_portal.forms as forms
import requests
import json
import logging
import unicodedata

logger = logging.getLogger(__name__)


@login_required
def badge_view(request, badge_id):

    if request.method == 'GET':
        # RETURN A BADGE #
        if request.GET.get("action") == "return":
            response = requests.put("{}/badge/temp_badge/{}/status/{}".format(settings.TBADGE_WS_URL, badge_id, "1"),
                                    data={"operator_fullname": "{} {}".format(request.session["first_name"].title(),
                                                                              request.session["last_name"].title())})
            validate_api_call(response, [304])
            if request.GET.get("type") == "inline":
                j = {'status': response.status_code}
                return JsonResponse(j, safe=False)
            elif response.status_code == 304:
                messages.error(request, "The badge could not be found or has already been returned. Please try again.",
                               extra_tags="danger")
                logger.error("status_code={} message=User '{}' attempted to return badge '{}' that either does not "
                             "exist or has already been returned.".format(304, request.session["username"], badge_id))
                return redirect(reverse('login'))
            messages.success(request, "Successfully returned badge.")
            return redirect(reverse('login'))
        else:
            response = requests.get("{}/badge/temp_badge/{}/latest".format(settings.TBADGE_WS_URL, badge_id))
            validate_api_call(response, [404])
            if response.status_code == 404:
                messages.error(request, "The badge could not be found. Please try again.", extra_tags="danger")
                logger.error("status_code={} message=User '{}' attempted to access badge '{}' that does not exist."
                             .format(404, request.session["username"], badge_id))
                return redirect(reverse('login'))
            response_data = json.loads(response.text)

            # IF RETURNED, SHOW HISTORY INSTEAD #
            if response_data["data"]["badge_status"]["status_id"] == 2:
                return redirect(reverse('badge_history', kwargs={"badge_id": badge_id}))

            return render(request, "tbadge_portal/badge/badge_view.html",
                          {"badge_data": json.dumps(response_data["data"]), "badge_id": badge_id})
    raise Http404

@login_required
def badge_view_only(request, badge_id):

    if request.method == 'GET':
        response = requests.get("{}/badge/temp_badge/{}/latest".format(settings.TBADGE_WS_URL, badge_id))
        validate_api_call(response, [404])
        if response.status_code == 404:
            messages.error(request, "The badge could not be found. Please try again.", extra_tags="danger")
            logger.error("status_code={} message=User '{}' attempted to access badge '{}' that does not exist."
                         .format(404, request.session["username"], badge_id))
            return redirect(reverse('login'))
        response_data = json.loads(response.text)

        # IF RETURNED, SHOW HISTORY INSTEAD #
        if response_data["data"]["badge_status"]["status_id"] == 2:
            return redirect(reverse('badge_history', kwargs={"badge_id": badge_id}))

        return render(request, "tbadge_portal/badge/badge_view.html",
                      {"badge_data": json.dumps(response_data["data"]), "badge_id": badge_id, "readonly": True})
    raise Http404


@login_required
def badge_history(request, badge_id):
    if request.method == 'GET':
        response = requests.get("{}/badge/temp_badge/{}".format(settings.TBADGE_WS_URL, badge_id))
        validate_api_call(response, [404])
        if response.status_code == 404:
            messages.error(request, "The badge could not be found. Please try again.", extra_tags="danger")
            logger.error("status_code={} message=User '{}' attempted to access badge '{}' that does not exist."
                         .format(404, request.session["username"], badge_id))
            return redirect(reverse('login'))
        response_data = json.loads(response.text)
        return render(request, "tbadge_portal/badge/badge_history.html",
                      {"badge_data": json.dumps(response_data), "badge_id": badge_id})
    raise Http404


@login_required
def badge_lookup(request):
    if request.method == 'GET':

        # Allow users and admins to access look-up page by id
        if request.GET.get("type") == "id":
            return render(request, "tbadge_portal/badge/badge_lookup.html")

        # Allow only admins to access look-up by date
        if request.GET.get("type") == "date" and request.session["role"] == 'Admin':
            return render(request, "tbadge_portal/badge/badge_date_lookup.html")
        else:
            messages.error(request, "You do not have authorization to access that page.", extra_tags="danger")
            logger.warning(
                "status_code={} message=Unauthorized user '{}' tried to access '{}', an admin-only page.".format(
                    403, request.session['username'], request.path))
            return redirect(reverse('login'))

    raise Http404


@admin_login_required
def badge_results(request):
    if request.method == 'POST':
        if request.GET.get("type") == "id":
            return redirect(reverse("badge_view", kwargs={"badge_id": request.POST.get("badge_id")}))
        if request.GET.get("type") == "date":
            form = forms.DateSearchForm(request.POST)
            if form.is_valid():
                from_date = request.POST.get("from_date")
                to_date = request.POST.get("to_date")
                not_returned_response = requests.get("{}/badge/temp_badge/status/time?from={}&to={}&badge_status={}".
                                                     format(settings.TBADGE_WS_URL, from_date, to_date, "not_returned"))
                validate_api_call(not_returned_response, [404])
                not_returned_data = {"data": []}

                overdue_response = requests.get("{}/badge/temp_badge/status/time?from={}&to={}&badge_status={}".
                                                format(settings.TBADGE_WS_URL, from_date, to_date, "overdue"))
                validate_api_call(overdue_response, [404])
                overdue_data = {"data": []}

                if not_returned_response.status_code != 404:
                    not_returned_data = json.loads(not_returned_response.text)

                if overdue_response.status_code != 404:
                    overdue_data = json.loads(overdue_response.text)

                returned_response = requests.get("{}/badge/temp_badge/status/time?to={}&from={}&badge_status={}".
                                                 format(settings.TBADGE_WS_URL, request.POST.get("to_date"),
                                                        request.POST.get("from_date"), "returned"))
                validate_api_call(returned_response, [404])
                returned_data = {"data": []}
                if returned_response.status_code != 404:
                    returned_data = json.loads(returned_response.text)
                    sorted_returned_data = sorted(
                        returned_data["data"], key=lambda k: datetime.strptime(k["issued_on"], '%m/%d/%Y %I:%M %p'),
                        reverse=True)
                    returned_data["data"] = sorted_returned_data

                return render(request, "tbadge_portal/badge/badge_results.html",
                              {
                                  "type": "all",
                                  "from": request.POST.get("from_date"),
                                  "to": request.POST.get("to_date"),
                                  "not_returned": json.dumps(not_returned_data),
                                  "returned": json.dumps(returned_data),
                                  "overdue": json.dumps(overdue_data)
                              })
            else:
                messages.warning(request, "The date data provided in the form could not be validated. "
                                          "Please try again.", extra_tags="danger")
                logger.warning("status_code={} message=User '{}' attempted to submit invalid date range for search."
                               .format(400, request.session["username"]))
                return render(request, "tbadge_portal/badge/badge_date_lookup.html")
    else:
        if request.GET.get("type") == "id":
            return redirect(reverse('badge_lookup') + "?type=id")
        return redirect(reverse('badge_lookup') + "?type=date")


@login_required
def badge_return(request):
    if request.method == 'GET':
        return render(request, "tbadge_portal/badge/badge_return.html")
    else:
        form = forms.BadgeQueryForm(request.POST)
        if form.is_valid:
            response = requests.get("{}/badge/temp_badge/{}".format(settings.TBADGE_WS_URL,
                                                                    request.POST.get("badge_query")))
            # Badge Not Found #
            validate_api_call(response, [404])
            if response.status_code == 404:
                messages.error(request, "The badge could not be found. Please try again.", extra_tags="danger")
                logger.error("status_code={} message=User '{}' attempted to access badge '{}' that does not exist."
                             .format(404, request.session["username"], request.POST.get("badge_query")))
                if request.GET.get("next"):
                    return redirect(request.GET.get("next"))
                return render(request, "tbadge_portal/badge/badge_return.html")

            if request.POST.get("type") == "readonly":
                return redirect(reverse("badge_view_only", kwargs={"badge_id": request.POST.get("badge_query")}))

            return redirect(reverse("badge_view", kwargs={"badge_id": request.POST.get("badge_query")}))
        else:
            messages.warning(request, "The badge could not be validated. Please try again.", extra_tags="danger")
            logger.warning("status_code={} message=User '{}' attempted to submit invalid badge '{}'."
                           .format(400, request.session["username"], request.POST.get("badge_query")))
            return render(request, "tbadge_portal/badge/badge_return.html", "")


@login_required
def badge_issue(request):

    # GET #
    if request.method == 'GET':

        # Validate Temporary Badge Status #
        if request.GET.get("action") == "validate_temporary":
            csn = request.GET['csn']

            # First, check if the badge tapped is actually an escort badge via escort badge status
            response = requests.get("{}/badge/escort_badge/csn/{}".format(settings.TBADGE_WS_URL, csn))
            validate_api_call(response, [404])

            # 200 implies the badge tapped was found in the table
            if response.status_code == 200:
                j = json.loads(response.text)

                # If it has a non-zero UPID, it is NOT a temporary badge so return error code 5
                if 'upid' in j['data']:
                    temp_upid = j['data']['upid']
                    unicodedata.normalize('NFKD', temp_upid).encode('ascii', 'ignore')
                    if temp_upid != '0':
                        j = {'status': response.status_code, 'status_id': 5}
                        return JsonResponse(j, safe=False)

            # Otherwise no UPID or a 404 (badge not found) means it's a valid temp badge
            # So continue to check whether the badge can be issued by TABS
            response = requests.get("{}/badge/temp_badge/{}/current_status".format(settings.TBADGE_WS_URL, csn))
            validate_api_call(response, [404])
            # 404 implies badge has never been issued - so it is valid
            if response.status_code == 200:
                j = json.loads(response.text)
                j['status'] = 200
                j['status_id'] = j['data']['status_id']
                return JsonResponse(j, safe=False)
            else:
                j = {'status': response.status_code, 'status_id': 4}
                return JsonResponse(j, safe=False)

        # Validate Escort Badge Status #
        elif request.GET.get("action") == "validate_escort":
            csn = request.GET['csn']
            response = requests.get("{}/badge/escort_badge/csn/{}".format(settings.TBADGE_WS_URL, csn))
            validate_api_call(response, [404])
            # 404 implies escort badge not found - valid call but invalid status
            if response.status_code == 200:
                j = json.loads(response.text)
                j['status'] = 200
                return JsonResponse(j, safe=False)
            else:
                j = {'status': response.status_code}
                return JsonResponse(j, safe=False)

        # Start Issue Badge with type 'Limited' #
        elif request.GET.get("type") == "ld":
            return render(request, "tbadge_portal/badge/badge_issue.html", {"type": 'ld'})

        # Start Issue Badge with type 'Standard' #
        elif request.GET.get("type") == "standard":
            return render(request, "tbadge_portal/badge/badge_issue.html", {"type:": 'std'})

    # POST #
    elif request.method == 'POST':

        # Create a request (step 1 to step 2) #
        if request.POST.get("action") == "create_request":

            # Create a validation form for the request to ensure formatting
            form = forms.CreateRequestForm(request.POST)
            if form.is_valid():

                # First make the request/create applicant and store it's return body #
                data = json.loads(json.dumps(request.POST))
                response = requests.post("{}/applicant/badge/request".format(settings.TBADGE_WS_URL), data=data)
                validate_api_call(response, [])
                j = json.loads(response.text)
                j['status'] = response.status_code

                # Then check if the applicant already has a badge issued and store the result
                # 404 implies applicant has no issuances and therefore is cleared
                app_id = j['data']['applicant_id']
                response = requests.get("{}/applicant/{}/badge/current_status".format(settings.TBADGE_WS_URL, app_id))
                validate_api_call(response, [404])
                if response.status_code == 200:
                    k = json.loads(response.text)
                    j['status_id'] = k['data']['status_id']
                else:
                    j['status_id'] = 4
                return JsonResponse(j, safe=False)
            else:
                logger.warning("status_code={} message=User '{}' Form data for CREATE REQUEST could not be validated."
                               .format(400, request.session["username"]))
                j = {'status': 400}
                return JsonResponse(j, safe=False)

        # Complete an issuance (step 3 to step 4) #
        elif request.POST.get("action") == "complete_issue":

            # Create the corresponding validation form to ensure correct formatting
            if request.POST.get("badge_type") == "Limited":
                form = forms.CreateLimitedIssuanceForm(request.POST)
            elif request.POST.get("badge_type") == "Standard":
                form = forms.CreateStandardIssuanceForm(request.POST)
            else:
                logger.warning("status_code={} message=User '{}' Tried to issue badge without a badge type."
                               .format(400, request.session["username"]))
                j = {'status': 400}
                return JsonResponse(j, safe=False)

            # Make the API call only if the form is in the correct format
            if form.is_valid():
                data = json.loads(json.dumps(request.POST))
                temp_csn = request.POST['csn']
                app_id = request.POST['applicant_id']
                req_id = request.POST['request_id']
                response = requests.post("{}/badge/temp_badge/{}/applicant/{}/request/{}"
                                         .format(settings.TBADGE_WS_URL, temp_csn, app_id, req_id), data=data)
                validate_api_call(response, [])
                j = {'status': response.status_code}
                return JsonResponse(j, safe=False)

            # Otherwise force a 400 error on the client side
            else:
                logger.warning("status_code={} message=User '{}' Form data for CREATE ISSUANCE could not be validated."
                               .format(400, request.session["username"]))
                j = {'status': 400}
                return JsonResponse(j, safe=False)

    # Default: Return Issue page with no type specified - Defaults to Standard Badge #
    return render(request, "tbadge_portal/badge/badge_issue.html")


@admin_login_required
def badge_list(request):
    if request.method == 'GET':
        if request.GET.get("type") == "recent":
            # from_date = datetime_to_utc(datetime.today()) - timedelta(days=1)
            # to_date = datetime_to_utc(datetime.today())
            from_date = datetime.today() - timedelta(days=1)
            to_date = datetime.today()

            response = requests.get("{}/badge/temp_badge/status/time?from={}&to={}&badge_status={}".format
                                    (settings.TBADGE_WS_URL, from_date.strftime("%Y-%m-%d %H:%M:%S"),
                                     to_date.strftime("%Y-%m-%d %H:%M:%S"), "not_returned"))
            validate_api_call(response, [404])
            if response.status_code == 404:
                response_data = {"data": []}
            else:
                response_data = json.loads(response.text)
                data = sorted(response_data["data"], key=lambda k: datetime.strptime(k["issued_on"],
                                                                                     '%m/%d/%Y %I:%M %p'), reverse=True)
                response_data["data"] = data
            if request.GET.get("f") == "json":
                return JsonResponse(response_data, safe=False)
            return render(request, "tbadge_portal/badge/badge_list.html", {"type": "recent",
                                                                           "issued_data": json.dumps(response_data)})
        if request.GET.get("type") == "overdue":
            response = requests.get("{}/badge/temp_badge/status/time?badge_status={}".format
                                    (settings.TBADGE_WS_URL, "overdue"))
            validate_api_call(response, [404])
            if response.status_code == 404:
                response_data = {"data": []}
            else:
                response_data = json.loads(response.text)
            return render(request, "tbadge_portal/badge/badge_list.html", {"type": "overdue",
                                                                           "overdue": json.dumps(response_data)})
    raise Http404


@admin_login_required
def badge_escort_results(request):
    if request.method == 'POST':
        if request.GET.get("type") == "name":
            form = forms.PersonSearchForm(request.POST)
            if form.is_valid():
                response = requests.get("{}/applicant/escort/search?first_name={}&last_name={}&middle_name={}".format(
                    settings.TBADGE_WS_URL, request.POST.get("first_name"), request.POST.get("last_name"),
                    request.POST.get("middle_name")))
                validate_api_call(response, [404])
                if response.status_code == 404:
                    messages.error(request,
                                   "Your query produced no results. Please make sure the name is spelled correctly, "
                                   "and try again.", extra_tags="danger")
                    return render(request, "tbadge_portal/applicant/applicant_lookup.html", "")
                response_data = json.loads(response.text)
                if len(response_data["data"]) == 1:
                    return redirect(reverse('badge_escort_view',
                                            kwargs={"escort_upid": hashid(json.loads(response.text)["data"][0]["upid"],
                                                                          "encode")}))
                else:
                    return render(request, "tbadge_portal/badge/badge_escort_list.html", {"escorts": response.text})
            else:
                messages.warning(request, "Your query could not be validated. Please try again.", extra_tags="danger")
                logger.warning("status_code={} message=User '{}' attempted to submit invalid escort name '{} {} {}'."
                               .format(400, request.session["username"], request.POST.get("first_name"),
                                       request.POST.get("middle_name"), request.POST.get("last_name")))
                return redirect(reverse("applicant_lookup"))

        if request.GET.get("type") == "csn":
            form = forms.BadgeQueryForm(request.POST)
            if form.is_valid():
                response = requests.get("{}/badge/escort_badge/csn/{}?issued_badges=true"
                                        .format(settings.TBADGE_WS_URL, request.POST.get("badge_query")))
                validate_api_call(response, [404])
                if response.status_code == 404:
                    messages.error(request, "The escort could not be found. Please make sure you have the right ID, "
                                            "and try again.", extra_tags="danger")
                    return redirect(reverse('badge_lookup') + "?type=id")

                response_data = json.loads(response.text)
                issued_badges = sorted(response_data["data"]["issuedBadges"],
                                       key=lambda k: datetime.strptime(k["issued_on"], '%m/%d/%Y %I:%M %p'),
                                       reverse=True)
                response_data["data"]["issuedBadges"] = issued_badges
                return render(request, "tbadge_portal/badge/badge_escort_view.html",
                              {"escort_data": json.dumps(response_data), "csn_view": True})

            else:
                messages.warning(request, "The escort csn could not be validated. Please try again.",
                                 extra_tags="danger")
                logger.warning("status_code={} message=User '{}' attempted to submit invalid escort csn '{}'."
                               .format(400, request.session["username"], request.POST.get("badge_query")))
                return redirect(reverse('badge_lookup') + "?type=id")

        if request.GET.get("type") == "upid":
            form = forms.BadgeQueryForm(request.POST)
            if form.is_valid():
                response = requests.get(
                    "{}/badge/escort_badge/upid/{}".format(settings.TBADGE_WS_URL, request.POST.get("badge_query")))
                validate_api_call(response, [404])
                if response.status_code == 404:
                    messages.error(request,
                                   "The escort could not be found. Please make sure you have the right ID, "
                                   "and try again.", extra_tags="danger")
                    return redirect(reverse('badge_lookup') + "?type=id")
                return redirect(reverse('badge_escort_view',
                                        kwargs={"escort_upid": hashid(json.loads(response.text)["data"]["upid"],
                                                                      "encode")}))
            else:
                messages.warning(request, "The escort upid could not be validated. "
                                          "Please try again.", extra_tags="danger")
                logger.warning("status_code={} message=User '{}' attempted to submit invalid escort upid '{}'."
                               .format(400, request.session["username"], request.POST.get("badge_query")))
                return redirect(reverse('badge_lookup') + "?type=id")
    else:
        return redirect(reverse('applicant_lookup'))


@admin_login_required
def badge_escort_view(request, escort_upid):
    if request.method == 'GET':
        decoded_id = hashid(escort_upid, "decode")
        if decoded_id is None:
            messages.error(request,
                           "The escort could not be found. Please make sure you have the right ID, and try again.",
                           extra_tags="danger")
            logger.warning("status_code={} message=User '{}' attempted to retrieve escort with invalid hashid '{}'."
                           .format(400, request.session["username"], escort_upid))
            return redirect(reverse('badge_lookup') + "?type=id")
        response = requests.get(
            "{}/badge/escort_badge/upid/{}".format(settings.TBADGE_WS_URL, decoded_id))
        validate_api_call(response, [404])
        if response.status_code == 404:
            messages.error(request,
                           "The escort could not be found. Please make sure you have the right ID, and try again.",
                           extra_tags="danger")
            return redirect(reverse('badge_lookup') + "?type=id")
        response_data = json.loads(response.text)
        issued_badges = sorted(response_data["data"]["issuedBadges"],
                               key=lambda k: datetime.strptime(k["issued_on"], '%m/%d/%Y %I:%M %p'), reverse=True)
        response_data["data"]["issuedBadges"] = issued_badges
        return render(request, "tbadge_portal/badge/badge_escort_view.html", {"escort_data": json.dumps(response_data)})
    raise Http404


@login_required
def badge_csn_escort_view(request, escort_csn):
    if request.method == 'GET':
        response = requests.get("{}/badge/escort_badge/csn/{}?issued_badges=true".format(settings.TBADGE_WS_URL,
                                                                                         escort_csn))
        validate_api_call(response, [404])
        if response.status_code == 404:
            messages.error(request, "The escort could not be found. Please make sure you have the right ID, "
                                    "and try again.", extra_tags="danger")
            return redirect(reverse('badge_lookup') + "?type=id")
        response_data = json.loads(response.text)
        issued_badges = sorted(response_data["data"]["issuedBadges"],
                               key=lambda k: datetime.strptime(k["issued_on"], '%m/%d/%Y %I:%M %p'), reverse=True)
        response_data["data"]["issuedBadges"] = issued_badges
        return render(request, "tbadge_portal/badge/badge_escort_view.html", {"escort_data": json.dumps(response_data),
                                                                              "csn_view": True})
    raise Http404


@login_required
def badge_escort_csn_to_upid(request):
    if request.method == 'GET':
        if request.GET.get("csn"):
            response = requests.get("{}/badge/escort_badge/csn/{}".format(settings.TBADGE_WS_URL,
                                                                          request.GET.get("csn")))
            validate_api_call(response, [404])
            if response.status_code == 404:
                messages.error(request, "The escort could not be found. Please make sure you have the right ID, "
                                        "and try again.", extra_tags="danger")
                return redirect(reverse('badge_lookup') + "?type=id")

            response_data = json.loads(response.text)["data"]
            if "upid" not in response_data:
                messages.error(request, "The escort could not be found. Please make sure you have the right ID, "
                                        "and try again.", extra_tags="danger")
                return redirect(reverse('badge_lookup') + "?type=id")

            return redirect(reverse('badge_escort_view',
                                    kwargs={"escort_upid": hashid(response_data["upid"], "encode")}))
        raise Http404
    raise Http404
