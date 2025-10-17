"""
Custom forms for RecruitApp signup and user management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from better_profanity import profanity
import re


# Initialize profanity filter
profanity.load_censor_words()


class CustomUserCreationForm(UserCreationForm):
    """Legacy custom user creation form - keeping for backwards compatibility."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class CustomSignupForm(SignupForm):
    """
    Custom signup form that extends allauth's SignupForm.

    Features:
    - Username profanity filtering (for kids on platform)
    - Email validation to ensure real email addresses
    - Custom field ordering and styling
    """

    # Override field order
    field_order = ['username', 'email', 'email2', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize field attributes for our styling
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Your email address',
            'autocomplete': 'email',
        })
        self.fields['email2'].widget.attrs.update({
            'placeholder': 'Confirm your email',
            'autocomplete': 'email',
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })

        # Update help text
        self.fields['username'].help_text = "Letters, numbers, and @/./+/-/_ only. Keep it appropriate!"
        self.fields['email'].help_text = "We'll use this to log in and send important updates."

    def clean_username(self):
        """
        Validate username for profanity.
        This protects kids on the platform from inappropriate usernames.
        """
        username = self.cleaned_data.get('username')

        if not username:
            return username

        # Check for profanity
        if profanity.contains_profanity(username):
            raise forms.ValidationError(
                "Please choose a different username. This one contains inappropriate language."
            )

        # Additional custom validation (optional)
        # Ensure username doesn't contain common inappropriate patterns
        inappropriate_patterns = [
            r'\d{4,}',  # Long number sequences (might be phone numbers)
        ]

        for pattern in inappropriate_patterns:
            if re.search(pattern, username):
                raise forms.ValidationError(
                    "Username should not contain long number sequences."
                )

        return username

    def clean_email(self):
        """
        Validate email to ensure it's a real email address.
        Basic validation to catch obvious fake emails.
        """
        email = self.cleaned_data.get('email')

        if not email:
            return email

        # Check for obviously fake domains
        fake_domains = [
            'example.com',
            'test.com',
            'fake.com',
            'localhost',
            'test.test',
            'example.org',
        ]

        domain = email.split('@')[-1].lower() if '@' in email else ''

        if domain in fake_domains:
            raise forms.ValidationError(
                "Please use a real email address."
            )

        # Basic format validation (Django already does this, but we can add more)
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError(
                "Please enter a valid email address."
            )

        return email

    def clean_email2(self):
        """
        Ensure email confirmation matches.
        """
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')

        if email and email2 and email != email2:
            raise forms.ValidationError(
                "Email addresses do not match."
            )

        return email2

    def save(self, request):
        """
        Save the user and prepare for family account creation.
        The actual FamilyAccount will be created in the post-signup view.
        """
        user = super().save(request)

        # Store in session that we need to show role selection
        request.session['needs_role_selection'] = True
        request.session['signup_email'] = user.email

        return user


class RoleSelectionForm(forms.Form):
    """
    Form for selecting user role after signup.
    Used in the post-signup flow to determine if user is athlete or parent.
    """
    role = forms.ChoiceField(
        choices=[
            ('athlete', "I'm the athlete"),
            ('parent', "I'm a parent/guardian"),
        ],
        widget=forms.RadioSelect,
        required=True,
        label="Who are you?",
        help_text="This helps us personalize your experience."
    )

    # Optional: Child's first name if parent
    child_first_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': "Child's first name (optional)",
        }),
        help_text="We'll use this to personalize the experience for your family."
    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        child_first_name = cleaned_data.get('child_first_name')

        # If role is parent, child's name is helpful but not required yet
        # They can invite the child later

        return cleaned_data