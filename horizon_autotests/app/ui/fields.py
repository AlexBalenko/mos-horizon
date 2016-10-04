"""
Custom form fields.

@author: gdyuldin@mirantis.com
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from pom import ui
from selenium.webdriver.common.by import By


class TextField(ui.TextField):
    """Custom text field."""

    @property
    @ui.wait_for_presence
    def help_message(self):
        """Get help message of field."""
        return self.webelement.find_element(
            By.XPATH, 'ancestor::*//*[contains(@class, "help-block")]'
        ).get_attribute('innerHTML')