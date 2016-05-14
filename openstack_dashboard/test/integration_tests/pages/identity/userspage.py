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

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables


class UsersTable(tables.TableRegion):
    name = 'users'
    CREATE_USER_FORM_FIELDS = ("name", "email", "password",
                               "confirm_password", "project", "role_id")
    EDIT_USER_FORM_FIELDS = ("name", "email", "project")
    CHANGE_PASSWORD_FORM_FIELDS = ("password", "confirm_password", "name")

    @tables.bind_table_action('create')
    def create_user(self, create_button):
        create_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.CREATE_USER_FORM_FIELDS)

    @tables.bind_row_action('edit', primary=True)
    def edit_user(self, edit_button, row):
        edit_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.EDIT_USER_FORM_FIELDS)

    @tables.bind_row_action('change_password')
    def change_password(self, change_password_button, row):
        change_password_button.click()
        return forms.FormRegion(
            self.driver, self.conf,
            field_mappings=self.CHANGE_PASSWORD_FORM_FIELDS)

    # Row action 'Disable user' / 'Enable user'
    @tables.bind_row_action('toggle')
    def disable_enable_user(self, disable_enable_user_button, row):
        disable_enable_user_button.click()

    @tables.bind_table_action('delete')
    def delete_user(self, delete_button):
        delete_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)


class UsersPage(basepage.BaseNavigationPage):

    USERS_TABLE_NAME_COLUMN = 'name'
    USERS_TABLE_ENABLED_COLUMN = 'enabled'

    def __init__(self, driver, conf):
        super(UsersPage, self).__init__(driver, conf)
        self._page_title = "Users"

    def _get_row_with_user_name(self, name):
        return self.users_table.get_row(self.USERS_TABLE_NAME_COLUMN, name)

    @property
    def users_table(self):
        return UsersTable(self.driver, self.conf)

    def create_user(self, name, password,
                    project, role, email=None):
        create_user_form = self.users_table.create_user()
        create_user_form.name.text = name
        if email is not None:
            create_user_form.email.text = email
        create_user_form.password.text = password
        create_user_form.confirm_password.text = password
        create_user_form.project.text = project
        create_user_form.role_id.text = role
        create_user_form.submit()

    def edit_user(self, name, new_name=None, new_email=None,
                  new_primary_project=None):
        row = self._get_row_with_user_name(name)
        edit_user_form = self.users_table.edit_user(row)
        if new_name:
            edit_user_form.name.text = new_name
        if new_email:
            edit_user_form.email.text = new_email
        if new_primary_project:
            edit_user_form.project.text = new_primary_project
        edit_user_form.submit()

    def get_user_info(self, name):
        user_info = {}

        row = self._get_row_with_user_name(name)
        edit_user_form = self.users_table.edit_user(row)

        user_info['name'] = edit_user_form.name.text
        user_info['email'] = edit_user_form.email.text or None
        user_info['primary_project'] = edit_user_form.project.text

        edit_user_form.cancel()
        return user_info

    def change_password(self, name, new_passwd):
        row = self._get_row_with_user_name(name)
        change_password_form = self.users_table.change_password(row)
        change_password_form.password.text = new_passwd
        change_password_form.confirm_password.text = new_passwd
        change_password_form.submit()

    def delete_user(self, name):
        row = self._get_row_with_user_name(name)
        row.mark()
        confirm_delete_users_form = self.users_table.delete_user()
        confirm_delete_users_form.submit()

    def is_user_present(self, name):
        return bool(self._get_row_with_user_name(name))

    def disable_enable_user(self, name, action):
        row = self._get_row_with_user_name(name)
        self.users_table.disable_enable_user(row)
        if action == 'disable':
            return row.cells[self.USERS_TABLE_ENABLED_COLUMN].text == 'No'
        elif action == 'enable':
            return row.cells[self.USERS_TABLE_ENABLED_COLUMN].text == 'Yes'
