import unittest 
from mock import patch
from pivotal_story import *  ## this line breaks the tests ... :^)
#from ansible.module_utils.basic import *
#from ansible.module_utils.urls import *

class FakeModule:

	def params(self, field):

		if field.startswith("willfail_"):
			return None 
		else:
			return "Some String"

class PivotalStoryTestCase(unittest.TestCase):

	def setUp(self):
		global module 
		module = FakeModule()

	def test_something(self):
		pass

"""

	@patch('ansible.module_utils.basic.module.fail_json')
	def test_validate_inputs_with_valid_inputs(self, mock_fail_json):
		test_inputs = ['name', id]
		validate_inputs(test_inputs)

		assert mock_fail_json.called is False, 'Expect fail_json not to have been called'
"""