from xblock.core import XBlock


class EventableMixin:

    @XBlock.json_handler
    def publish_event(self, data, *args, **kwargs):
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
        result = {
            'result': 'success',
        }
        return result

    def _get_unique_id(self):
        try:
            unique_id = self.location.name
        except AttributeError:
            # workaround for xblock workbench
            unique_id = 'workbench-workaround-id'
        return unique_id

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
