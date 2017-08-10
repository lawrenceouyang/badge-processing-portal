from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404
from django.conf import settings
from tbadge_portal.forms import PersonSearchForm, NotesForm
from tbadge_portal.views.error import validate_api_call
from tbadge_portal.helpers import hashid
from tbadge_portal.views.login import login_required, admin_login_required
from datetime import datetime
import requests
import json
import logging

logger = logging.getLogger(__name__)


@admin_login_required
def applicant_lookup(request):
    if request.method == 'GET':
        return render(request, "tbadge_portal/applicant/applicant_lookup.html", "")
    else:
        raise Http404


@admin_login_required
def applicant_results(request):
    if request.method == 'GET':
        return redirect(reverse('applicant_lookup'))
    else:
        form = PersonSearchForm(request.POST)
        if form.is_valid():
            response = requests.get("{}/applicant/search?first_name={}&last_name={}&middle_name={}".format
                                    (settings.TBADGE_WS_URL, request.POST.get("first_name"),
                                     request.POST.get("last_name"), request.POST.get("middle_name")))
            validate_api_call(response, [404])
            if response.status_code == 404:
                messages.error(request,
                               "Your query produced no results. Please make sure the name is spelled correctly, "
                               "and try again.", extra_tags="danger")
                return render(request, "tbadge_portal/applicant/applicant_lookup.html", "")
            response_data = json.loads(response.text)
            if len(response_data["data"]) == 1:
                encoded_id = hashid(response_data["data"][0]["applicant_id"], "encode")
                return redirect(reverse('applicant_view', kwargs={"applicant_id": encoded_id}))
            else:
                return render(request, "tbadge_portal/applicant/applicant_list.html", {"applicants": response.text})
        else:
            messages.warning(request, "Your query could not be validated. Please try again.", extra_tags="danger")
            logger.warning(
                "status_code={} message=User '{}' attempted to submit invalid applicant name '{} {} {}'.".
                    format(400, request.session["username"], request.POST.get("first_name"),
                           request.POST.get("middle_name"), request.POST.get("last_name")))
            return redirect(reverse("applicant_lookup"))


@login_required
def applicant_view(request, applicant_id):
    decoded_id = hashid(applicant_id, "decode")
    if decoded_id is None:
        logger.warning("status_code={} message=User '{}' attempted to retrieve applicant with invalid hashid '{}'."
                       .format(400, request.session["username"], applicant_id))
        messages.error(request, "The applicant you're looking for does not exist. Please try again.",
                       extra_tags="danger")
        return redirect(reverse('login'))
    if request.method == 'GET':
        applicant_response = requests.get("{}/applicant/{}".format(settings.TBADGE_WS_URL, decoded_id))
        validate_api_call(applicant_response, [404])
        if applicant_response.status_code == 404 or len(json.loads(applicant_response.text)["data"]) == 0:
            messages.error(request, "The applicant you're looking for does not exist. Please try again.",
                           extra_tags="danger")
            return redirect(reverse('login'))
        applicant_data = json.loads(applicant_response.text)["data"][0]
        if "middle_name" in applicant_data:
            applicant_name = "{} {} {}".format(applicant_data["first_name"], applicant_data["middle_name"],
                                               applicant_data["last_name"])
        else:
            applicant_name = "{} {}".format(applicant_data["first_name"], applicant_data["last_name"])

        # ISSUANCE HISTORY #
        if request.GET.get("history") == "issuance":
            response = requests.get("{}/applicant/{}/badge".format(settings.TBADGE_WS_URL, decoded_id))
            validate_api_call(response, [404])
            response_data = {"data": []}
            if response.status_code != 404:
                response_data = json.loads(response.text)
                data = sorted(response_data["data"], key=lambda k: datetime.strptime(k["issued_on"], '%m/%d/%Y %I:%M %p'),
                          reverse=True)
                response_data["data"] = data
            return render(request, "tbadge_portal/applicant/applicant_issuances.html",
                          {"issuance": json.dumps(response_data), "applicant": applicant_name,
                           "applicant_id": applicant_id})

        # REQUEST HISTORY #
        elif request.GET.get("history") == "requests":
            response = requests.get("{}/applicant/{}/badge/request".format(settings.TBADGE_WS_URL, decoded_id))
            validate_api_call(response, [404])
            if response.status_code == 404:
                messages.error(request, "The applicant you're looking for does not exist. Please try again.",
                               extra_tags="danger")
                return redirect(reverse('login'))
            response_data = json.loads(response.text)
            data = sorted(response_data["data"], key=lambda k: datetime.strptime(k["timestamp"], '%m/%d/%Y %I:%M %p'),
                          reverse=True)
            response_data["data"] = data
            return render(request, "tbadge_portal/applicant/applicant_requests.html",
                          {"requests": json.dumps(response_data), "applicant": applicant_name,
                           "applicant_id": applicant_id})

        else:
            # APPLICANT PROFILE #
            return render(request, "tbadge_portal/applicant/applicant_view.html",
                          {"applicant": applicant_response.text})
    else:
        # Post Notes
        form = NotesForm(request.POST)
        if form.is_valid():
            response = requests.put("{}/applicant/{}".format(settings.TBADGE_WS_URL, decoded_id),
                                    data={"notes": request.POST.get("notes"),
                                          "operator_username": "{} {}".format
                                          (request.session["first_name"], request.session["last_name"])})
            validate_api_call(response, [])
            messages.success(request, "Applicant notes successfully updated!")
            return redirect(reverse('applicant_view', kwargs={"applicant_id": applicant_id}))
        else:
            logger.warning(
                "status_code={} message=Notes post failed django form validation".format(400))
            messages.error(request, "Your notes submission could not be validated.", extra_tags="danger")
            return redirect(reverse('applicant_view', kwargs={"applicant_id": applicant_id}))
