# settings.py

SESSION_CONFIGS = [
    dict(
        name='legitimacy',
        display_name='Legitimacy, Transparency & Compliance',
        app_sequence=['legitimacy_exp'],
        num_demo_participants=5,
        # Treatment variables — change these per session in the admin
        election_condition=True,    # True = Election, False = Random
        transparent_condition=True, # True = Transparent, False = Vague
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01,
    participation_fee=5.00,
)

PARTICIPANT_FIELDS = []

SESSION_FIELDS = [
    'election_condition',
    'transparent_condition',
]

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = []

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'your_password_here'

DEMO_PAGE_INTRO_HTML = ""

SECRET_KEY = '{{ secret_key }}'  # oTree auto-fills this

INSTALLED_APPS = ['otree']