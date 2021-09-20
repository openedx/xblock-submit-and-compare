"""
Handle view logic for the XBlock
"""
import logging

from django.utils.translation import ungettext
from django.utils.translation import ugettext as _
from lxml import etree
from six import StringIO
from xblock.core import XBlock
from xblockutils.resources import ResourceLoader

from .mixins.fragment import XBlockFragmentBuilderMixin


LOG = logging.getLogger(__name__)


def _convert_to_int(value_string):
    """
    Convert a string to integer

    Default to 0
    """
    try:
        value = int(value_string)
    except ValueError:
        value = 0
    return value


def get_body(xmlstring):
    """
    Helper method
    """
    # pylint: disable=no-member
    tree = etree.parse(StringIO(xmlstring))
    body = tree.xpath('/submit_and_compare/body')
    body_string = etree.tostring(body[0], method='text', encoding='unicode')
    return body_string


def _get_explanation(xmlstring):
    # pylint: disable=no-member
    """
    Helper method
    """
    tree = etree.parse(StringIO(xmlstring))
    explanation = tree.xpath('/submit_and_compare/explanation')
    explanation_string = etree.tostring(
        explanation[0],
        method='text',
        encoding='unicode',
    )
    return explanation_string


class SubmitAndCompareViewMixin(
        XBlockFragmentBuilderMixin,
):
    """
    Handle view logic for Image Modal XBlock instances
    """

    loader = ResourceLoader(__name__)
    static_js_init = 'SubmitAndCompareXBlockInitView'
    icon_class = 'problem'
    editable_fields = [
        'display_name',
        'weight',
        'max_attempts',
        'your_answer_label',
        'our_answer_label',
        'submit_button_label',
        'question_string',
    ]
    show_in_read_only_mode = True

    def provide_context(self, context=None):
        """
        Build a context dictionary to render the student view
        """
        context = context or {}
        context = dict(context)
        problem_progress = self._get_problem_progress()
        used_attempts_feedback = self._get_used_attempts_feedback()
        submit_class = self._get_submit_class()
        prompt = get_body(self.question_string)
        explanation = _get_explanation(
            self.question_string
        )
        attributes = ''
        context.update({
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
        })
        return context

    def studio_view(self, context=None):
        """
        Build the fragment for the edit/studio view

        Implementation is optional.
        """
        context = context or {}
        context.update({
            'display_name': self.display_name,
            'weight': self.weight,
            'max_attempts': self.max_attempts,
            'xml_data': self.question_string,
            'your_answer_label': self.your_answer_label,
            'our_answer_label': self.our_answer_label,
            'submit_button_label': self.submit_button_label,
        })
        template = 'edit.html'
        fragment = self.build_fragment(
            template=template,
            context=context,
            js_init='SubmitAndCompareXBlockInitEdit',
            css=[
                'edit.css',
            ],
            js=[
                'edit.js',
            ],
        )
        return fragment

    @XBlock.json_handler
    def studio_submit(self, data, *args, **kwargs):
        """
        Save studio edits
        """
        # pylint: disable=unused-argument
        self.display_name = data['display_name']
        self.weight = _convert_to_int(data['weight'])
        max_attempts = _convert_to_int(data['max_attempts'])
        if max_attempts >= 0:
            self.max_attempts = max_attempts
        self.your_answer_label = data['your_answer_label']
        self.our_answer_label = data['our_answer_label']
        self.submit_button_label = data['submit_button_label']
        xml_content = data['data']
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
    def student_submit(self, data, *args, **kwargs):
        """
        Save student answer
        """
        # pylint: disable=unused-argument
        # when max_attempts == 0, the user can make unlimited attempts
        success = False
        # pylint: disable=no-member
        if self.max_attempts > 0 and self.count_attempts >= self.max_attempts:
            # pylint: enable=no-member
            LOG.error(
                'User has already exceeded the maximum '
                'number of allowed attempts',
            )
        elif self.is_past_due():
            LOG.debug(
                'This problem is past due',
            )
        else:
            self.student_answer = data['answer']
            if data['action'] == 'submit':
                self.count_attempts += 1  # pylint: disable=no-member
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
    def send_hints(self, data, *args, **kwargs):
        """
        Build hints once for user
        This is called once on page load and
        js loop through hints on button click
        """
        # pylint: disable=unused-argument
        # pylint: disable=no-member
        tree = etree.parse(StringIO(self.question_string))
        raw_hints = tree.xpath('/submit_and_compare/demandhint/hint')
        decorated_hints = []
        total_hints = len(raw_hints)
        for i, raw_hint in enumerate(raw_hints, 1):
            hint = _('Hint ({number} of {total}): {hint}').format(
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

    def _get_used_attempts_feedback(self):
        """
        Returns the text with feedback to the user about the number of attempts
        they have used if applicable
        """
        result = ''
        if self.max_attempts > 0:
            # pylint: disable=no-member
            result = ungettext(
                'You have used {count_attempts} of {max_attempts} submission',
                'You have used {count_attempts} of {max_attempts} submissions',
                self.max_attempts,
            ).format(
                count_attempts=self.count_attempts,
                max_attempts=self.max_attempts,
            )
            # pylint: enable=no-member
        return result

    def _can_submit(self):
        """
        Determine if a user can submit a response
        """
        if self.is_past_due():
            return False
        if self.max_attempts == 0:
            return True
        # pylint: disable=no-member
        if self.count_attempts < self.max_attempts:
            return True
        # pylint: enable=no-member
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
            score_string = f'{scaled_score:g}'
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
