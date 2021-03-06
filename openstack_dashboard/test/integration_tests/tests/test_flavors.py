#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstack_dashboard.test.integration_tests import helpers
from openstack_dashboard.test.integration_tests.regions import messages


class TestFlavors(helpers.AdminTestCase):
    FLAVOR_NAME = helpers.gen_random_resource_name("flavor")

    def flavor_create(self, name=None, selected_projects=None):
        name = name or self.FLAVOR_NAME
        flavors_page = self.home_pg.go_to_system_flavorspage()
        flavors_page.create_flavor(name=name, vcpus=1, ram=1024, root_disk=20,
                                   ephemeral_disk=0, swap_disk=0,
                                   selected_projects=selected_projects)
        self.assertTrue(
            flavors_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(flavors_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(flavors_page.is_flavor_present(name))
        return flavors_page

    def flavor_delete(self, name=None):
        name = name or self.FLAVOR_NAME
        flavors_page = self.home_pg.go_to_system_flavorspage()
        flavors_page.delete_flavor(name)
        self.assertTrue(
            flavors_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(flavors_page.find_message_and_dismiss(messages.ERROR))
        self.assertFalse(flavors_page.is_flavor_present(name))

    def test_flavor_create(self):
        """tests the flavor creation and deletion functionalities:
        * creates a new flavor
        * verifies the flavor appears in the flavors table
        * deletes the newly created flavor
        * verifies the flavor does not appear in the table after deletion
        """
        self.flavor_create()
        self.flavor_delete()

    def test_flavor_update_metadata(self):
        """Test update flavor metadata
        * logs in as admin user
        * creates a new flavor
        * verifies the flavor appears in the flavors table
        * verifies that Metadata column of the table contains 'No'
        * invokes action 'Update Metadata' for the new flavor
        * adds custom filed 'metadata'
        * adds value 'flavor' for the custom filed 'metadata'
        * verifies that Metadata column of the table is updated to Yes
        * deletes the newly created flavor
        * verifies the flavor does not appear in the table after deletion
        """
        new_metadata = {'metadata1': helpers.gen_random_resource_name("value"),
                        'metadata2': helpers.gen_random_resource_name("value")}
        flavors_page = self.flavor_create()
        self.assertTrue(
            flavors_page.get_metadata_column_value(self.FLAVOR_NAME) == 'No')
        flavors_page.add_custom_metadata(self.FLAVOR_NAME, new_metadata)
        self.assertTrue(
            flavors_page.get_metadata_column_value(self.FLAVOR_NAME) == 'Yes')
        results = flavors_page.check_flavor_metadata(self.FLAVOR_NAME,
                                                     new_metadata)
        self.flavor_delete()
        self.assertSequenceTrue(results)  # custom matcher

    def test_edit_flavor(self):
        new_flavor_name = 'new-' + self.FLAVOR_NAME
        flavors_page = self.flavor_create()

        flavors_page.edit_flavor(name=self.FLAVOR_NAME,
                                 new_name=new_flavor_name)
        self.assertTrue(
            flavors_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(flavors_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(flavors_page.is_flavor_present(new_flavor_name))

        self.flavor_delete(new_flavor_name)

    def test_modify_flavor_access(self):
        self.flavor_create(selected_projects=['admin'])
        assert self.FLAVOR_NAME in self._available_flavors()

        self.home_pg.log_out()

        self.home_pg = self.login_pg.login(self.DEMO_NAME, self.DEMO_PASSWORD)
        self.home_pg.change_project(self.DEMO_PROJECT)
        assert self.FLAVOR_NAME not in self._available_flavors()

        self.home_pg.log_out()

        self.home_pg = self.login_pg.login(self.ADMIN_NAME,
                                           self.ADMIN_PASSWORD)
        self.home_pg.change_project(self.ADMIN_PROJECT)

        self.flavor_delete()

    def _available_flavors(self):
        instances_page = self.home_pg.go_to_compute_instancespage()
        launch_instance_form = \
            instances_page.instances_table.launch_instance_ng()
        launch_instance_form.switch_to(2)
        available_flavor_names = \
            launch_instance_form.flavors.available_items.keys()
        launch_instance_form.cancel()
        return available_flavor_names

    def test_delete_flavors(self):
        names = [self.FLAVOR_NAME + str(i) for i in range(3)]
        for name in names:
            flavors_page = self.flavor_create(name)

        name = names.pop()
        flavors_page.delete_flavors(name)
        self.assertTrue(
            flavors_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(flavors_page.find_message_and_dismiss(messages.ERROR))
        self.assertFalse(flavors_page.is_flavor_present(name))

        flavors_page.delete_flavors(*names)
        self.assertTrue(
            flavors_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(flavors_page.find_message_and_dismiss(messages.ERROR))
        self.assertSequenceFalse(
            [flavors_page.is_flavor_present(name) for name in names])
