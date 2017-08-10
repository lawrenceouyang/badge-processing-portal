from django.contrib.auth import logout as django_logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from tbadge_portal.forms import LoginForm
from tbadge_portal.views.error import validate_api_call
import requests
import json
import logging

logger = logging.getLogger(__name__)


def login_required(function):
    def wrapper(request, *args, **kw):
        try:
            if not request.session.session_key or 'role' not in request.session or settings.UNDER_CONSTRUCTION:
                return redirect(reverse('login') + '?next=' + request.get_full_path())
            else:
                return function(request, *args, **kw)
        except KeyError:
            django_logout(request)
            return redirect(reverse('login'))
    return wrapper


def admin_login_required(function):
    def wrapper(request, *args, **kw):
        try:
            if not request.session.session_key or 'role' not in request.session or settings.UNDER_CONSTRUCTION:
                return redirect(reverse('login') + '?next=' + request.get_full_path())
            elif request.session["role"] == 'User':
                messages.error(request, "You do not have authorization to access that page.", extra_tags="danger")
                logger.warning("status_code={} message=Unauthorized user '{}' tried to access '{}', an admin-only page."
                               .format(403, request.session['username'], request.path))
                return redirect(reverse('login'))
            else:
                return function(request, *args, **kw)
        except KeyError:
            django_logout(request)
            return redirect(reverse('login'))
    return wrapper


def logout(request):
    request.session.clear()
    django_logout(request)
    return redirect(reverse('login'))


def login(request):
    try:
        # Redirect to Home if session is already valid
        if request.session.session_key and 'role' in request.session and not settings.UNDER_CONSTRUCTION:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            return render(request, "tbadge_portal/main/home.html", "")

        # Login POST
        elif request.method == 'POST' and not settings.UNDER_CONSTRUCTION:
            form = LoginForm(request.POST)

            # Ensure login form parameters are valid
            if form.is_valid():
                username = request.POST.get('username')
                password = request.POST.get('password')

                # First attempt to log in using SFO AD
                response = requests.post("{}/ad/auth".format(settings.AD_WS_URL),
                                         data={"username": username, "password": password, "attributes": True})
                validate_api_call(response, [])
                response_data = json.loads(response.text)["response"]

                # If SFO AD returns a valid set of credentials
                if response_data["validPassword"] is True:

                    # Assign role corresponding to database role
                    if '#REDACTED' in response_data["role"]:
                        request.session["role"] = 'Admin'
                    elif '#REDACTED' in response_data["role"]:
                        request.session["role"] = 'Admin'
                    elif '#REDACTED' in response_data["role"]:
                        request.session["role"] = 'Admin'
                    elif '#REDACTED' in response_data["role"]:
                        request.session["role"] = 'User'
                    elif '#REDACTED' in response_data["role"]:
                        request.session["role"] = 'User'
                    elif '#REDACTED' in response_data["role"] and settings.ALLOW_TEST_USER:
                        request.session["role"] = 'User'

                    # No role or incorrect role implies unauthorized access
                    else:
                        logger.warning("status_code={} message=Unauthorized user {} attempted to login."
                                       .format(403, username))
                        messages.error(request, "You do not have authorization to access this system.",
                                       extra_tags="danger")
                        return redirect(reverse('login'))

                    # Fill session metadata
                    request.session["logged_in"] = True
                    request.session["first_name"] = response_data["firstName"].title()
                    request.session["last_name"] = response_data["lastName"].title()
                    request.session["username"] = username
                    request.session["id"] = response_data["id"]

                    # Redirect to next page/home page
                    logger.info("Redirection to page '{}'.".format(request.GET.get('next')))
                    if request.GET.get('next'):
                        return redirect(request.GET.get('next'))
                    return render(request, "tbadge_portal/main/home.html", "")

                # Otherwise try SFPD AD
                else:
                    response = requests.post("{}/ad-sfpd/auth".format(settings.AD_WS_URL),
                                             data={"username": username, "password": password,
                                                   "attributes": True})
                    validate_api_call(response, [])
                    response_data = json.loads(response.text)["response"]

                    # If they have a valid SFPD AD, grant them 'User Access'
                    if response_data["validPassword"] is True:

                        # Check for specific role?

                        request.session["role"] = 'User'
                        request.session["logged_in"] = True
                        request.session["first_name"] = response_data["firstName"].title()
                        request.session["last_name"] = response_data["lastName"].title()
                        request.session["username"] = username
                        request.session["id"] = response_data["id"]

                        # Redirect to next page/home page
                        logger.info("Redirection to page '{}'.".format(request.GET.get('next')))
                        if request.GET.get('next'):
                            return redirect(request.GET.get('next'))
                        return render(request, "tbadge_portal/main/home.html", "")

                    # Otherwise user failed both AD checks - alert them of incorrect username/password.
                    else:
                        messages.error(request, 'Wrong username or password.', extra_tags="danger")
                    logger.warning("status_code={} message=Invalid credentials for user '{}' after trying sfo and "
                                   "sfpd ad".format(401, username))
                    return render(request, "tbadge_portal/account/login.html", "")

        # Default - Redirect to Login
        else:
            request.session.clear()
            return render(request, "tbadge_portal/account/login.html", "")
    except KeyError:
        request.session.clear()
        django_logout(request)
        messages.error(request, "Unable to validate credentials. Please contact an administrator.", extra_tags="danger")
        return redirect(reverse('login'))
