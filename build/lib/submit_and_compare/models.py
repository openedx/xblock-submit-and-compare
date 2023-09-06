"""
Handle data access logic for the XBlock
"""
import textwrap

from xblock.fields import Float
from xblock.fields import Integer
from xblock.fields import List
from xblock.fields import Scope
from xblock.fields import String


class SubmitAndCompareModelMixin:
    """
    Handle data access logic for the XBlock
    """

    has_score = True
    display_name = String(
        display_name='Display Name',
        default='Submit and Compare',
        scope=Scope.settings,
        help=(
            'This name appears in the horizontal'
            ' navigation at the top of the page'
        ),
    )
    student_answer = String(
        default='',
        scope=Scope.user_state,
        help='This is the student\'s answer to the question',
    )
    max_attempts = Integer(
        default=0,
        scope=Scope.settings,
    )
    count_attempts = Integer(
        default=0,
        scope=Scope.user_state,
    )
    your_answer_label = String(
        default='Your Answer:',
        scope=Scope.settings,
        help='Label for the text area containing the student\'s answer',
    )
    our_answer_label = String(
        default='Our Answer:',
        scope=Scope.settings,
        help='Label for the \'expert\' answer',
    )
    submit_button_label = String(
        default='Submit and Compare',
        scope=Scope.settings,
        help='Label for the submit button',
    )
    hints = List(
        default=[],
        scope=Scope.content,
        help='Hints for the question',
    )
    question_string = String(
        help='Default question content ',
        scope=Scope.content,
        multiline_editor=True,
        default=textwrap.dedent("""
            <submit_and_compare schema_version='1'>
                <body>
                    <p>
                        Before you begin the simulation,
                        think for a minute about your hypothesis.
                        What do you expect the outcome of the simulation
                        will be?  What data do you need to gather in order
                        to prove or disprove your hypothesis?
                    </p>
                </body>
                <explanation>
                    <p>
                        We would expect the simulation to show that
                        there is no difference between the two scenarios.
                        Relevant data to gather would include time and
                        temperature.
                    </p>
                </explanation>
                <demandhint>
                    <hint>
                        A hypothesis is a proposed explanation for a
                        phenomenon. In this case, the hypothesis is what
                        we think the simulation will show.
                    </hint>
                    <hint>
                        Once you've decided on your hypothesis, which data
                        would help you determine if that hypothesis is
                        correct or incorrect?
                    </hint>
                </demandhint>
            </submit_and_compare>
        """))
    score = Float(
        default=0.0,
        scope=Scope.user_state,
    )
    weight = Integer(
        display_name='Weight',
        help='This assigns an integer value representing '
             'the weight of this problem',
        default=0,
        scope=Scope.settings,
    )

    def max_score(self):
        """
        Returns the configured number of possible points for this component.
        Arguments:
            None
        Returns:
            float: The number of possible points for this component
        """
        return self.weight
