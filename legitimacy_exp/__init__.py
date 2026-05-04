from otree.api import *
import random
from collections import Counter

# ── Experiment parameters ──────────────────────────────────────────
N_PLAYERS      = 5
TAX_RATE       = 0.40
ALPHA          = 2.0
N_ROUNDS       = 1
EFFORT_TIMEOUT = 60

OPTION_LABELS = {
    1: 'Equal Distribution',
    2: 'Favoring Self',
    3: 'Effort Based',
}

TRANSPARENT_MESSAGES = [
    'Everyone should receive an equal share',
    'I keep some more for me but still share fairly',
    'Higher effort deserves more',
]

VAGUE_MESSAGE = 'This is my offer.'


# ── Constants ──────────────────────────────────────────────────────
class C(BaseConstants):
    NAME_IN_URL       = 'legitimacy_exp'
    PLAYERS_PER_GROUP = N_PLAYERS
    NUM_ROUNDS        = N_ROUNDS


# ── Subsession ─────────────────────────────────────────────────────
class Subsession(BaseSubsession):
    pass


# ── Group ──────────────────────────────────────────────────────────
class Group(BaseGroup):
    common_revenue    = models.FloatField(initial=0)
    total_pot         = models.FloatField(initial=0)
    allocator_id      = models.IntegerField()
    allocation_option = models.IntegerField(
        choices=[1, 2, 3],
        blank=True,             # ← fixed
    )
    message_sent      = models.StringField(blank=True)  # ← fixed
    accept_votes      = models.IntegerField(initial=0)
    reject_votes      = models.IntegerField(initial=0)
    proposal_accepted = models.BooleanField()


# ── Player ─────────────────────────────────────────────────────────
class Player(BasePlayer):
    # Effort task
    numA             = models.IntegerField()
    numB             = models.IntegerField()
    countCorrect     = models.IntegerField(initial=0)
    countIncorrect   = models.IntegerField(initial=0)

    # Derived from effort task
    income           = models.IntegerField(initial=0)
    tax_paid         = models.FloatField(initial=0)
    after_tax_income = models.FloatField(initial=0)

    # Role flags
    is_allocator     = models.BooleanField(initial=False)
    is_candidate     = models.BooleanField(initial=False)

    # Election fields
    nomination       = models.IntegerField(blank=True)
    election_vote    = models.IntegerField(blank=True)

    # Responder vote
    accept_vote      = models.BooleanField(
        choices=[[True,  'I Accept the allocation'],
                 [False, 'I Reject the allocation']],
        label='Your vote',
        widget=widgets.RadioSelect,
        blank=True,
    )

    # Payoffs
    allocation_received = models.FloatField(initial=0)
    round_payoff        = models.FloatField(initial=0)

    # Allocation decision
    allocation_choice   = models.IntegerField(blank=True)
    selected_message    = models.StringField(blank=True)

    # Comprehension check answers
    comp_tax_rate = models.IntegerField(
        blank=True,
        choices=[
            [1, '20%'],
            [2, '40%'],
            [3, '60%'],
            [4, '80%'],
        ],
        label='',
        widget=widgets.RadioSelect,
    )

    comp_votes_needed = models.IntegerField(
        blank=True,
        choices=[
            [1, '2 out of 4'],
            [2, '3 out of 4'],
            [3, '4 out of 4'],
            [4, '1 out of 4'],
        ],
        label='',
        widget=widgets.RadioSelect,
    )

    comp_rejection = models.IntegerField(
        blank=True,
        choices=[
            [1, 'Nothing — you lose your tax payment'],
            [2, 'The full project fund divided equally'],
            [3, 'An equal share of the tax revenue (R/5)'],
            [4, 'Your after-tax income only'],
        ],
        label='',
        widget=widgets.RadioSelect,
    )

    comp_who_decides = models.IntegerField(
        blank=True,
        choices=[
            [1, 'One randomly selected group member (the Allocator)'],
            [2, 'All group members by majority vote'],
            [3, 'The experimenter'],
            [4, 'The participant with the highest income'],
        ],
        label='',
        widget=widgets.RadioSelect,
    )

    # Comprehension check attempts tracking
    comp_attempts = models.IntegerField(initial=0)  # all submissions
    comp_failed_attempts = models.IntegerField(initial=0)  # only failed ones
    comp_q1_wrong = models.IntegerField(initial=0)
    comp_q2_wrong = models.IntegerField(initial=0)
    comp_q3_wrong = models.IntegerField(initial=0)
    comp_q4_wrong = models.IntegerField(initial=0)

    # Demographic survey
    age = models.IntegerField(
        label='What is your age?',
        min=18,
        max=100,
    )

    gender = models.StringField(
        label='What is your gender?',
        choices=[
            'Male',
            'Female',
            'Non-binary',
            'Prefer not to say',
            'Other',
        ],
        widget=widgets.RadioSelect,
    )

    race = models.StringField(
        label='What is your race/ethnicity?',
        choices=[
            'White/Caucasian',
            'Black/African American',
            'Hispanic/Latino',
            'Asian/Pacific Islander',
            'Native American/Alaska Native',
            'Multiracial',
            'Prefer not to say',
            'Other',
        ],
        widget=widgets.RadioSelect,
    )

    nationality = models.StringField(
        label='What is your nationality?',
    )

    year_in_school = models.StringField(
        label='What is your year in school?',
        choices=[
            'Freshman',
            'Sophomore',
            'Junior',
            'Senior',
            'Graduate student',
            'Other',
        ],
        widget=widgets.RadioSelect,
    )

    major = models.StringField(
        label='What is your major/field of study?',
    )

    political_orientation = models.IntegerField(
        label='How would you describe your political orientation?',
        choices=[
            [1, 'Very liberal'],
            [2, 'Liberal'],
            [3, 'Moderate'],
            [4, 'Conservative'],
            [5, 'Very conservative'],
        ],
        widget=widgets.RadioSelect,
    )

    institutional_trust = models.IntegerField(
        label='How much do you trust institutions in general? (1 = not at all, 5 = very much)',
        choices=[
            [1, '1 — Not at all'],
            [2, '2'],
            [3, '3 — Neutral'],
            [4, '4'],
            [5, '5 — Very much'],
        ],
        widget=widgets.RadioSelect,
    )

    elected_better = models.IntegerField(
        label='Do you think elected officials make better decisions than appointed ones?',
        choices=[
            [1, 'Strongly disagree'],
            [2, 'Disagree'],
            [3, 'Neutral'],
            [4, 'Agree'],
            [5, 'Strongly agree'],
        ],
        widget=widgets.RadioSelect,
    )

    transparency_importance = models.IntegerField(
        label='How important is it that decision-makers explain their reasoning?',
        choices=[
            [1, 'Not important at all'],
            [2, 'Slightly important'],
            [3, 'Moderately important'],
            [4, 'Very important'],
            [5, 'Extremely important'],
        ],
        widget=widgets.RadioSelect,
    )

# ── Subsession function ────────────────────────────────────────────
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()
        for player in subsession.get_players():
            player.numA = round(random.random() * 10)
            player.numB = round(random.random() * 10)
    else:
        subsession.group_like_round(1)
        for player in subsession.get_players():
            prev = player.in_round(1)
            if prev.income:
                player.income           = prev.income
                player.tax_paid         = prev.tax_paid
                player.after_tax_income = prev.after_tax_income


# ── Player-level function ──────────────────────────────────────────
def compute_tax(player: Player):
    player.income           = player.countCorrect
    player.tax_paid         = round(TAX_RATE * player.income, 2)
    player.after_tax_income = round((1 - TAX_RATE) * player.income, 2)


# ── Group functions ────────────────────────────────────────────────
def compute_revenue(group: Group):
    total_income         = sum(p.income for p in group.get_players())
    group.common_revenue = TAX_RATE * total_income
    group.total_pot      = ALPHA * group.common_revenue


def assign_random_allocator(group: Group):
    allocator              = random.choice(group.get_players())
    allocator.is_allocator = True
    group.allocator_id     = allocator.id_in_group


def tally_nominations(group: Group):
    players  = group.get_players()
    counts   = Counter(p.nomination for p in players)
    ranked   = sorted(
        players,
        key=lambda p: (-counts.get(p.id_in_group, 0), random.random())
    )
    for p in ranked[:2]:
        p.is_candidate = True


def tally_election(group: Group):
    candidates  = [p for p in group.get_players() if p.is_candidate]
    vote_counts = {c.id_in_group: 0 for c in candidates}
    for p in group.get_players():
        if p.election_vote in vote_counts:
            vote_counts[p.election_vote] += 1
    max_votes  = max(vote_counts.values())
    winners    = [pid for pid, v in vote_counts.items() if v == max_votes]
    elected_id = random.choice(winners)
    for p in group.get_players():
        p.is_allocator = (p.id_in_group == elected_id)
    group.allocator_id = elected_id


def compute_allocation(group: Group):
    players      = group.get_players()
    T            = group.total_pot
    n            = N_PLAYERS
    option       = group.allocation_option
    total_income = sum(p.income for p in players)
    for p in players:
        if option == 1:
            p.allocation_received = T / n
        elif option == 2:
            p.allocation_received = (T / 2) if p.is_allocator \
                                    else T / (2 * (n - 1))
        elif option == 3:
            share = (p.income / total_income) if total_income > 0 else (1 / n)
            p.allocation_received = T * share


def tally_votes(group: Group):
    responders          = [p for p in group.get_players() if not p.is_allocator]
    group.accept_votes  = sum(1 for p in responders if p.accept_vote)
    group.reject_votes  = len(responders) - group.accept_votes
    group.proposal_accepted = group.accept_votes >= 3


def compute_payoffs(group: Group):
    default_refund = group.common_revenue / N_PLAYERS
    for p in group.get_players():
        x_i            = p.allocation_received if group.proposal_accepted \
                         else default_refund
        p.round_payoff = p.after_tax_income + x_i
        p.payoff       = p.round_payoff


# ── Pages ──────────────────────────────────────────────────────────
class Intro(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            num_rounds = N_ROUNDS,
            round_word = 'round' if N_ROUNDS == 1 else 'rounds',
        )

class GroupAssignment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            group_id = player.group.id_in_subsession
        )

class ComprehensionCheck(Page):
    form_model  = 'player'
    form_fields = [
        'comp_tax_rate',
        'comp_votes_needed',
        'comp_rejection',
        'comp_who_decides',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        player.comp_attempts += 1  # always increments

        if values.get('comp_tax_rate') != 2:
            errors['comp_tax_rate'] = 'Incorrect. Please try again.'
            player.comp_q1_wrong += 1

        if values.get('comp_votes_needed') != 2:
            errors['comp_votes_needed'] = 'Incorrect. Please try again.'
            player.comp_q2_wrong += 1

        if values.get('comp_rejection') != 3:
            errors['comp_rejection'] = 'Incorrect. Please try again.'
            player.comp_q3_wrong += 1

        if values.get('comp_who_decides') != 1:
            errors['comp_who_decides'] = 'Incorrect. Please try again.'
            player.comp_q4_wrong += 1

        if errors:
            player.comp_failed_attempts += 1  # only increments on failure

        return errors if errors else None

class EffortTaskInstructions(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(effort_timeout=EFFORT_TIMEOUT)

class EffortTask(Page):

    timeout_seconds = EFFORT_TIMEOUT

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def live_method(player: Player, data):
        try:
            answer = int(data)
        except (ValueError, TypeError):
            answer = -1

        if player.numA + player.numB == answer:
            player.countCorrect += 1
        else:
            player.countIncorrect += 1

        player.numA = round(random.random() * 10)
        player.numB = round(random.random() * 10)

        return {
            player.id_in_group: {
                'num_a':           player.numA,
                'num_b':           player.numB,
                'count_correct':   player.countCorrect,
                'count_incorrect': player.countIncorrect,
            }
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        compute_tax(player)


class EffortTaskWaitPage(WaitPage):

    title_text = 'Waiting for other participants'
    body_text  = 'Please wait while the other participants finish the effort task.'

    template_name = 'legitimacy_exp/EffortTaskWaitPage.html'

    @staticmethod
    def after_all_players_arrive(group: Group):
        compute_revenue(group)
        assign_random_allocator(group)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            count_correct   = player.countCorrect,
            count_incorrect = player.countIncorrect,
            income          = player.countCorrect,
            tax_paid        = round(TAX_RATE * player.countCorrect, 2),
            after_tax       = round((1 - TAX_RATE) * player.countCorrect, 2),
        )

class IncomeTaxation(Page):

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        T = group.total_pot
        n = N_PLAYERS
        total_income = sum(p.income for p in group.get_players())
        default_refund = round(group.common_revenue / n, 2)

        # Minimum share — Option 2 gives non-allocators T/2(n-1)
        # but we don't know if they'll be allocator so show both extremes
        min_share = round(T / (2 * (n - 1)), 2)  # worst case as responder

        # Maximum share — Option 1 gives everyone T/n equally
        max_share = round(T / n, 2)

        return dict(
            default_refund=default_refund,
            common_revenue=round(group.common_revenue, 2),
            total_pot=round(T, 2),
            min_share=min_share,
            max_share=max_share,
        )

class AllocatorReveal(Page):

    @staticmethod
    def vars_for_template(player: Player):
        group     = player.group
        allocator = group.get_player_by_id(group.allocator_id)
        all_players = [
            dict(
                id_in_group = p.id_in_group,
                income      = p.income,
            )
            for p in group.get_players()
        ]
        return dict(
            allocator_id     = group.allocator_id,
            allocator_income = allocator.income,
            all_players      = all_players,
        )


class AllocatorDecisionWaitPage(WaitPage):
    """Holds responders while the allocator decides."""

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_allocator

    title_text = 'Waiting for the decision-maker'
    body_text  = 'Please wait while the decision-maker makes their allocation choice.'


class AllocationDecision(Page):
    form_model  = 'player'
    form_fields = ['allocation_choice', 'selected_message']

    @staticmethod
    def is_displayed(player: Player):
        return player.is_allocator

    @staticmethod
    def vars_for_template(player: Player):
        group        = player.group
        T            = group.total_pot
        n            = N_PLAYERS
        total_income = sum(p.income for p in group.get_players())

        opt1_each   = round(T / n, 2)
        opt2_self   = round(T / 2, 2)
        opt2_others = round(T / (2 * (n - 1)), 2)

        opt3_amounts = [
            dict(
                id_in_group = p.id_in_group,
                amount      = round(T * (p.income / total_income), 2)
                              if total_income > 0
                              else round(T / n, 2),
                is_self     = p.id_in_group == player.id_in_group,
            )
            for p in group.get_players()
        ]

        return dict(
            opt1_each    = opt1_each,
            opt2_self    = opt2_self,
            opt2_others  = opt2_others,
            opt3_amounts = opt3_amounts,
            total_pot    = round(T, 2),
        )

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('allocation_choice'):
            return 'Please select an allocation option.'
        if not values.get('selected_message'):
            return 'Please select or enter a message.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.group.allocation_option = player.allocation_choice
        player.group.message_sent      = player.selected_message


class AllocationWaitPage(WaitPage):
    """Everyone reunites here; compute each player's allocation."""

    title_text = 'Processing allocation'
    body_text  = 'Please wait while the allocation is being calculated.'

    @staticmethod
    def after_all_players_arrive(group: Group):
        compute_allocation(group)

class VotingPage(Page):
    form_model  = 'player'
    form_fields = ['accept_vote']

    @staticmethod
    def is_displayed(player: Player):
        return not player.is_allocator

    @staticmethod
    def vars_for_template(player: Player):
        group          = player.group
        default_refund = round(group.common_revenue / N_PLAYERS, 2)
        my_allocation  = round(player.allocation_received, 2)

        # ← field_maybe_none guards against None before allocator submits
        option       = group.field_maybe_none('allocation_option')
        message_sent = group.field_maybe_none('message_sent') or ''
        option_label = OPTION_LABELS.get(option, '') if option else ''

        return dict(
            my_allocation  = my_allocation,
            default_refund = default_refund,
            message_sent   = message_sent,
            allocator_id   = group.allocator_id,
            option_label   = option_label,
        )
class VotingWaitPage(WaitPage):

    title_text = 'Waiting for all votes'
    body_text  = 'Please wait while all votes are being collected.'

    @staticmethod
    def after_all_players_arrive(group: Group):
        tally_votes(group)
        compute_payoffs(group)


class RoundResults(Page):

    @staticmethod
    def vars_for_template(player: Player):
        group          = player.group
        default_refund = round(group.common_revenue / N_PLAYERS, 2)
        option         = group.field_maybe_none('allocation_option')
        option_label   = OPTION_LABELS.get(option, '') if option else ''

        return dict(
            accepted       = group.proposal_accepted,
            accept_votes   = group.accept_votes,
            reject_votes   = group.reject_votes,
            option_label   = option_label,
            allocation     = round(player.allocation_received, 2),
            default_refund = default_refund,
            after_tax      = round(player.after_tax_income, 2),
            round_payoff   = round(player.round_payoff, 2),
            is_last_round  = player.round_number == N_ROUNDS,
        )


class FinalPayment(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == N_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        # Sum payoffs across all rounds
        total = sum(
            p.round_payoff
            for p in player.in_all_rounds()
            if p.round_payoff
        )
        # Randomly select one round for payment
        paid_round = player.participant.vars.get('paid_round')
        if not paid_round:
            paid_round = random.randint(1, N_ROUNDS)
            player.participant.vars['paid_round'] = paid_round

        paid_payoff = player.in_round(paid_round).round_payoff

        return dict(
            paid_round  = paid_round,
            paid_payoff = round(paid_payoff, 2),
            total       = round(total, 2),
        )

class DemographicSurvey(Page):
    form_model  = 'player'
    form_fields = [
        'age',
        'gender',
        'race',
        'nationality',
        'year_in_school',
        'major',
        'political_orientation',
        'institutional_trust',
        'elected_better',
        'transparency_importance',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == N_ROUNDS

class ClosingPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == N_ROUNDS

page_sequence = [
    Intro,
    GroupAssignment,
    ComprehensionCheck,
    EffortTaskInstructions,
    EffortTask,
    EffortTaskWaitPage,
    IncomeTaxation,
    AllocatorReveal,
    AllocatorDecisionWaitPage,   # responders wait here
    AllocationDecision,          # allocator decides here
    AllocationWaitPage,          # everyone reunites, compute_allocation runs
    VotingPage,
    VotingWaitPage,      # new
    RoundResults,        # new
    FinalPayment,
    DemographicSurvey,
    ClosingPage,
]