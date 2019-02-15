"""
Submit and Compare XBlock main Python class
"""

from StringIO import StringIO

import textwrap
import logging
import pkg_resources

from lxml import etree

from django.template import Context, Template
from django.utils.translation import ungettext

from xblock.core import XBlock
from xblock.fields import Scope, String, List, Float, Integer
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader

from .mixins import EnforceDueDates

LOG = logging.getLogger(__name__)

loader = ResourceLoader(__name__)


# Public
def get_body(xmlstring):
    # pylint: disable=no-member
    """
    Helper method
    """
    tree = etree.parse(StringIO(xmlstring))
    body = tree.xpath('/submit_and_compare/body')
    body_string = etree.tostring(body[0], method='text', encoding='unicode')
    return body_string


# Private
def _load_resource(resource_path):
    """
    Gets the content of a resource
    """
    resource_content = pkg_resources.resource_string(
        __name__,
        resource_path,
    )
    return unicode(resource_content)


def _render_template(template_path, context):
    """
    Evaluate a template by resource path, applying the provided context
    """
    template_str = _load_resource(template_path)
    return Template(template_str).render(Context(context))


def _resource_string(path):
    """
    Handy helper for getting resources from our kit.
    """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode('utf8')


def _get_explanation(xmlstring):
    # pylint: disable=no-member
    """
    Helper method
    """
    tree = etree.parse(StringIO(xmlstring))
    explanation = tree.xpath('/submit_and_compare/explanation')
    explanation_string = etree.tostring(explanation[0], method='text', encoding='unicode')
    return explanation_string


def _convert_to_int(value_string):
    try:
        value = int(value_string)
    except ValueError:
        value = 0
    return value


class SubmitAndCompareXBlock(EnforceDueDates, XBlock):
    #  pylint: disable=too-many-ancestors, too-many-instance-attributes
    """
    Enables instructors to create questions with submit and compare responses.
    """

    # Icon of the XBlock. Values : [other (default), video, problem]
    icon_class = 'problem'

    """
    Fields
    """
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

    has_score = True

    def build_fragment(
            self,
            template, 
            context_dict,
    ):
        """
        Creates a fragment for display.
        """
        context = Context(context_dict)
        fragment = Fragment(template.render(context))
        return fragment

    """
    Main functions
    """
    # Decorate the view in order to support multiple devices e.g. mobile
    # See: https://openedx.atlassian.net/wiki/display/MA/Course+Blocks+API
    # section 'View @supports(multi_device) decorator'
    @XBlock.supports('multi_device')
    def student_view(self, context=None):
        # pylint: disable=unused-argument
        """
        The primary view of the XBlock, shown to students
        when viewing courses.
        """
        problem_progress = self._get_problem_progress()
        used_attempts_feedback = self._get_used_attempts_feedback()
        submit_class = self._get_submit_class()
        prompt = get_body(self.question_string)
        explanation = _get_explanation(
            self.question_string
        )
        attributes = ''
        context.update(
            {
                'display_name': self.display_name,
                'problem_progress': problem_progress,
                'used_attempts_feedback': used_attempts_feedback,
                'submit_class': submit_class,
                'prompt': prompt,
                'student_answer': self.student_answer,
                'explanation': explanation,
                'your_answer_label': self.your_answer_label,
                'our_answer_label': self.our_answer_label,
                'submit_button_label': self.submit_button_label,
                'attributes': attributes,
                'is_past_due': self.is_past_due(),
            }
        )
        fragment = Fragment()
        fragment.content = loader.render_template(
            'templates/submit_and_compare_view.html',
            context
        )
        fragment.add_css(
            _resource_string(
                'static/css/submit_and_compare.css'
            ),
        )
        fragment.add_javascript(
            _resource_string(
                'static/js/submit_and_compare_view.js'
            ),
        )
        fragment.initialize_js('SubmitAndCompareXBlockInitView')
        return fragment


    def studio_view(self, context=None):
        """
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        """
        context = {
            'display_name': self.display_name,
            'weight': self.weight,
            'max_attempts': self.max_attempts,
            'xml_data': self.question_string,
            'your_answer_label': self.your_answer_label,
            'our_answer_label': self.our_answer_label,
            'submit_button_label': self.submit_button_label,
        }
        html = _render_template(
            'templates/submit_and_compare_edit.html',
            context,
        )

        frag = Fragment(html)
        resource_content = _load_resource(
            'static/js/submit_and_compare_edit.js'
        )
        frag.add_javascript(resource_content)
        frag.initialize_js('SubmitAndCompareXBlockInitEdit')
        return frag

    def max_score(self):
        """
        Returns the configured number of possible points for this component.
        Arguments:
            None
        Returns:
            float: The number of possible points for this component
        """
        return self.weight

    @XBlock.json_handler
    def student_submit(self, submissions, suffix=''):
        # pylint: disable=unused-argument
        """
        Save student answer
        """
        # when max_attempts == 0, the user can make unlimited attempts
        success = False
        if self.max_attempts > 0 and self.count_attempts >= self.max_attempts:
            LOG.error(
                'User has already exceeded the maximum '
                'number of allowed attempts',
            )
        elif self.is_past_due():
            LOG.debug(
                'This problem is past due',
            )
        else:
            self.student_answer = submissions['answer']

            if submissions['action'] == 'submit':
                self.count_attempts += 1

            if self.student_answer:
                self.score = 1.0
            else:
                self.score = 0.0

            self._publish_grade()
            self._publish_problem_check()
            success = True

        result = {
            'success': success,
            'problem_progress': self._get_problem_progress(),
            'submit_class': self._get_submit_class(),
            'used_attempts_feedback': self._get_used_attempts_feedback(),
        }
        return result

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        # pylint: disable=unused-argument
        """
        Save studio edits
        """
        self.display_name = submissions['display_name']
        self.weight = _convert_to_int(submissions['weight'])
        max_attempts = _convert_to_int(submissions['max_attempts'])
        if max_attempts >= 0:
            self.max_attempts = max_attempts
        self.your_answer_label = submissions['your_answer_label']
        self.our_answer_label = submissions['our_answer_label']
        self.submit_button_label = submissions['submit_button_label']
        xml_content = submissions['data']
        # pylint: disable=no-member
        try:
            etree.parse(StringIO(xml_content))
            self.question_string = xml_content
        except etree.XMLSyntaxError as error:
            return {
                'result': 'error',
                'message': error.message,
            }

        return {
            'result': 'success',
        }

    @XBlock.json_handler
    def send_hints(self, submissions, suffix=''):
        # pylint: disable=unused-argument
        # pylint: disable=no-member
        """
        Build hints once for user
        This is called once on page load and
        js loop through hints on button click
        """
        tree = etree.parse(StringIO(self.question_string))
        raw_hints = tree.xpath('/submit_and_compare/demandhint/hint')
        decorated_hints = list()
        total_hints = len(raw_hints)
        for i, raw_hint in enumerate(raw_hints, 1):
            hint = u'Hint ({number} of {total}): {hint}'.format(
                number=i,
                total=total_hints,
                hint=etree.tostring(raw_hint, encoding='unicode'),
            )
            decorated_hints.append(hint)
        hints = decorated_hints
        return {
            'result': 'success',
            'hints': hints,
        }

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):
        # pylint: disable=unused-argument
        """
        Publish events
        """
        try:
            event_type = data.pop('event_type')
        except KeyError:
            return {
                'result': 'error',
                'message': 'Missing event_type in JSON data',
            }

        data['user_id'] = self.scope_ids.user_id
        data['component_id'] = self._get_unique_id()
        self.runtime.publish(self, event_type, data)

        return {'result': 'success'}

    def _get_unique_id(self):
        try:
            unique_id = self.location.name
        except AttributeError:
            # workaround for xblock workbench
            unique_id = 'workbench-workaround-id'
        return unique_id

    def _get_used_attempts_feedback(self):
        """
        Returns the text with feedback to the user about the number of attempts
        they have used if applicable
        """
        result = ''
        if self.max_attempts > 0:
            result = ungettext(
                'You have used {count_attempts} of {max_attempts} submission',
                'You have used {count_attempts} of {max_attempts} submissions',
                self.max_attempts,
            ).format(
                count_attempts=self.count_attempts,
                max_attempts=self.max_attempts,
            )
        return result

    def _can_submit(self):
        if self.is_past_due():
            return False
        if self.max_attempts == 0:
            return True
        if self.count_attempts < self.max_attempts:
            return True
        return False

    def _get_submit_class(self):
        """
        Returns the css class for the submit button
        """
        result = ''
        if not self._can_submit():
            result = 'nodisplay'
        return result

    def _get_problem_progress(self):
        """
        Returns a statement of progress for the XBlock, which depends
        on the user's current score
        """
        if self.weight == 0:
            result = ''
        elif self.score == 0.0:
            result = "({})".format(
                ungettext(
                    '{weight} point possible',
                    '{weight} points possible',
                    self.weight,
                ).format(
                    weight=self.weight,
                )
            )
        else:
            scaled_score = self.score * self.weight
            score_string = '{0:g}'.format(scaled_score)
            result = "({})".format(
                ungettext(
                    score_string + '/' + "{weight} point",
                    score_string + '/' + "{weight} points",
                    self.weight,
                ).format(
                    weight=self.weight,
                )
            )
        return result

    def _publish_grade(self):
        self.runtime.publish(
            self,
            'grade',
            {
                'value': self.score,
                'max_value': 1.0,
            }
        )

    def _publish_problem_check(self):
        self.runtime.publish(
            self,
            'problem_check',
            {
                'grade': self.score,
                'max_grade': 1.0,
            }
        )
