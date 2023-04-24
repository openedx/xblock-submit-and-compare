"""
Tests for xblock-submit-and-compare
"""
import re
import unittest
from xml.sax.saxutils import escape

from unittest import mock
from django.test.client import Client
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xblock.field_data import DictFieldData

from ..xblocks import SubmitAndCompareXBlock
from ..views import get_body


class SubmitAndCompareXblockTestCase(unittest.TestCase):
    # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    A complete suite of unit tests for the Submit-and-compare XBlock
    """
    @classmethod
    def make_an_xblock(cls, **kw):
        """
        Helper method that creates a Free-text Response XBlock
        """
        course_id = SlashSeparatedCourseKey('foo', 'bar', 'baz')
        runtime = mock.Mock(course_id=course_id)
        scope_ids = mock.Mock()
        field_data = DictFieldData(kw)
        xblock = SubmitAndCompareXBlock(runtime, field_data, scope_ids)
        xblock.xmodule_runtime = runtime
        return xblock

    def setUp(self):
        self.xblock = SubmitAndCompareXblockTestCase.make_an_xblock()
        self.client = Client()

    def test_student_view(self):
        # pylint: disable=protected-access
        """
        Checks the student view for student specific instance variables.
        """
        student_view_html = self.student_view_html()
        self.assertIn(self.xblock.display_name, student_view_html)
        self.assertIn(
            get_body(self.xblock.question_string),
            student_view_html,
        )
        self.assertIn(self.xblock._get_problem_progress(), student_view_html)

    def test_studio_view(self):
        """
        Checks studio view for instance variables specified by the instructor.
        """
        with mock.patch(
            "submit_and_compare.mixins.fragment.XBlockFragmentBuilderMixin.get_i18n_service",
            return_value=None
        ):
            studio_view_html = self.studio_view_html()
        self.assertIn(self.xblock.display_name, studio_view_html)
        xblock_body = get_body(
            self.xblock.question_string
        )
        studio_view_html = re.sub(r'\W+', ' ', studio_view_html.strip())
        xblock_body = re.sub(r'\W+', ' ', xblock_body.strip())
        self.assertIn(
            escape(xblock_body),
            studio_view_html,
        )
        self.assertIn(str(self.xblock.max_attempts), studio_view_html)

    def test_initialization_variables(self):
        """
        Checks that all instance variables are initialized correctly
        """
        self.assertEqual('Submit and Compare', self.xblock.display_name)
        self.assertIn(
            'Before you begin the simulation',
            self.xblock.question_string,
        )
        self.assertEqual(0.0, self.xblock.score)
        self.assertEqual(0, self.xblock.max_attempts)
        self.assertEqual('', self.xblock.student_answer)
        self.assertEqual(0, self.xblock.count_attempts)

    def student_view_html(self):
        """
        Helper method that returns the html of student_view
        """
        return self.xblock.student_view().content

    def studio_view_html(self):
        """
        Helper method that returns the html of studio_view
        """
        return self.xblock.studio_view().content

    def test_problem_progress_weight_zero(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        is blank when the weight of the problem is zero
        """
        self.xblock.score = 1
        self.xblock.weight = 0
        self.assertEqual('', self.xblock._get_problem_progress())

    def test_problem_progress_score_zero_weight_singular(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is singular, and the score is zero
        """
        self.xblock.score = 0
        self.xblock.weight = 1
        self.assertEqual(
            '(1 point possible)',
            self.xblock._get_problem_progress(),
        )

    def test_problem_progress_score_zero_weight_plural(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is plural, and the score is zero
        """
        self.xblock.score = 0
        self.xblock.weight = 3
        self.assertEqual(
            '(3 points possible)',
            self.xblock._get_problem_progress(),
        )

    def test_problem_progress_score_positive_weight_singular(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is singular, and the score is positive
        """
        self.xblock.score = 1
        self.xblock.weight = 1
        self.assertEqual(
            '(1/1 point)',
            self.xblock._get_problem_progress(),
        )

    def test_problem_progress_score_positive_weight_plural(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that the the string returned by get_problem_progress
        when the weight of the problem is plural, and the score is positive
        """
        self.xblock.score = 1
        self.xblock.weight = 3
        self.assertEqual(
            '(3/3 points)',
            self.xblock._get_problem_progress(),
        )

    def test_used_attempts_feedback_blank(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that get_used_attempts_feedback returns no feedback when
        appropriate
        """
        self.xblock.max_attempts = 0
        self.assertEqual('', self.xblock._get_used_attempts_feedback())

    def test_used_attempts_feedback_normal(self):
        # pylint: disable=invalid-name, protected-access
        """
        Tests that get_used_attempts_feedback returns the expected feedback
        """
        self.xblock.max_attempts = 5
        self.xblock.count_attempts = 3
        self.assertEqual(
            'You have used 3 of 5 submissions',
            self.xblock._get_used_attempts_feedback(),
        )

    def test_submit_class_blank(self):
        # pylint: disable=protected-access
        """
        Tests that get_submit_class returns a blank value when appropriate
        """
        self.xblock.max_attempts = 0
        self.assertEqual('', self.xblock._get_submit_class())

    def test_submit_class_nodisplay(self):
        # pylint: disable=protected-access
        """
        Tests that get_submit_class returns the appropriate class
        when the number of attempts has exceeded the maximum number of
        permissable attempts
        """
        self.xblock.max_attempts = 5
        self.xblock.count_attempts = 6
        self.assertEqual('nodisplay', self.xblock._get_submit_class())

    def test_max_score(self):
        """
        Tests max_score function
        Should return the weight
        """
        self.xblock.weight = 4
        self.assertEqual(self.xblock.weight, self.xblock.max_score())
