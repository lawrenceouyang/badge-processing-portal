from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.PasswordInput()


class DateSearchForm(forms.Form):
    from_date = forms.DateTimeField(required=True)
    to_date = forms.DateTimeField(required=True)


class PersonSearchForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True)
    middle_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=True)


class BadgeQueryForm(forms.Form):
    badge_query = forms.CharField(max_length=100, required=True)


class NotesForm(forms.Form):
    notes = forms.CharField(max_length=500, required=False)


class CreateRequestForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True)
    middle_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=True)
    dob = forms.DateField(required=True)
    operator_fullname = forms.CharField(max_length=80, required=True)
    badge_type = forms.ChoiceField(choices=[("Limited", "Limited"), ("Standard", "Standard")], required=True)


class CreateLimitedIssuanceForm(forms.Form):
    csn = forms.CharField(max_length=16, required=True)
    applicant_id = forms.CharField(required=True)
    request_id = forms.CharField(required=True)
    badge_type = forms.ChoiceField(choices=[("Limited", "Limited")], required=True)
    escort_badge_csn = forms.CharField(max_length=16, required=True)
    issued_by = forms.CharField(max_length=80, required=True)
    override = forms.BooleanField(required=False)
    escort_upid = forms.CharField(required=True)


class CreateStandardIssuanceForm(forms.Form):
    csn = forms.CharField(max_length=16, required=True)
    applicant_id = forms.CharField(required=True)
    request_id = forms.CharField(required=True)
    badge_type = forms.ChoiceField(choices=[("Standard", "Standard")], required=True)
    issued_by = forms.CharField(max_length=80, required=True)
    override = forms.BooleanField(required=False)
