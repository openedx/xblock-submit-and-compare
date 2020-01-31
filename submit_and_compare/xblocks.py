"""
This is the core logic for the XBlock
"""
from __future__ import absolute_import
from xblock.core import XBlock

from .mixins.dates import EnforceDueDates
from .mixins.events import EventableMixin
from .mixins.scenario import XBlockWorkbenchMixin
from .models import SubmitAndCompareModelMixin
from .views import SubmitAndCompareViewMixin


@XBlock.needs('i18n')
class SubmitAndCompareXBlock(
        EnforceDueDates,
        EventableMixin,
        SubmitAndCompareModelMixin,
        SubmitAndCompareViewMixin,
        XBlockWorkbenchMixin,
        XBlock,
):
    """
    A Submit-And-Compare XBlock
    """
