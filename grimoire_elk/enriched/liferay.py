# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2019 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#

import logging

from grimoirelab_toolkit.datetime import unixtime_to_datetime

from .enrich import Enrich, metadata
from ..elastic_mapping import Mapping as BaseMapping

logger = logging.getLogger(__name__)


class LiferayEnrich(Enrich):

    def get_field_author(self):
        return "emailAddress"

    def get_identities(self, item):
        """ Return the identities from an item """

        user = self.get_sh_identity(item)
        yield user

    def get_sh_identity(self, item, identity_field=None):
        identity = {}

        user = item
        if 'data' in item and type(item) == dict:
            user = item['data']

        if 'firstName' in user:
            identity['name'] = user['firstName'] + ' ' + user['lastName']
        else:
            identity['name'] = user['userName']
        identity['email'] = None
        identity['username'] = None

        if 'emailAddress' in user:
            identity['email'] = user['emailAddress']
        if 'screenName' in user:
            identity['username'] = user['screenName']

        return identity

    @metadata
    def get_rich_item(self, item):

        rich_item = {}
        if item['category'] == 'user':
            rich_item = self.__get_rich_user(item)
        elif item['category'] == 'blog':
            rich_item = self.__get_rich_blog(item)
        elif item['category'] == 'message':
            rich_item = self.__get_rich_message(item)
        else:
            logger.error("rich item not defined for Liferay category %s", item['category'])

        self.add_repository_labels(rich_item)
        self.add_metadata_filter_raw(rich_item)
        return rich_item

    def __get_rich_user(self, item):
        rich_user = {}

        for f in self.RAW_FIELDS_COPY:
            if f in item:
                rich_user[f] = item[f]
            else:
                rich_user[f] = None

        user = item['data']

        rich_user['type'] = 'user'
        rich_user['display_name'] = user['firstName'] + ' ' + user['lastName']
        # rich_user['email'] = user['emailAddress']
        # rich_user['username'] = user['screenName']

        creation_date = unixtime_to_datetime(user['createDate'] / 1000).isoformat()
        rich_user['creation_date'] = creation_date
        rich_user.update(self.get_grimoire_fields(creation_date, "user"))

        if user['lastLoginDate'] is not None:
            login_date = unixtime_to_datetime(user['lastLoginDate'] / 1000).isoformat()
            rich_user['login_date'] = login_date

        if self.sortinghat:
            rich_user.update(self.get_item_sh(item))

        return rich_user

    def __get_rich_blog(self, item):
        rich_user = {}

        for f in self.RAW_FIELDS_COPY:
            if f in item:
                rich_user[f] = item[f]
            else:
                rich_user[f] = None

        user = item['data']

        rich_user['type'] = 'blog'
        rich_user['author'] = user['userName']
        rich_user['subtitle'] = user['subtitle']
        rich_user['title'] = user['title']

        creation_date = unixtime_to_datetime(user['createDate'] / 1000).isoformat()
        rich_user['creation_date'] = creation_date
        rich_user.update(self.get_grimoire_fields(creation_date, "user"))

        if user['displayDate'] is not None:
            display_date = unixtime_to_datetime(user['displayDate'] / 1000).isoformat()
            rich_user['display_date'] = display_date

        if self.sortinghat:
            rich_user.update(self.get_item_sh(item))

        return rich_user

    def __get_rich_message(self, item):
        rich_user = {}

        for f in self.RAW_FIELDS_COPY:
            if f in item:
                rich_user[f] = item[f]
            else:
                rich_user[f] = None

        user = item['data']

        rich_user['type'] = 'post'
        rich_user['author'] = user['userName']
        rich_user['parent_message_id'] = user['parentMessageId']
        rich_user['root_message_id'] = user['rootMessageId']
        rich_user['message_id'] = user['messageId']
        rich_user['answer'] = user['answer']
        rich_user['subject'] = user['subject']

        rich_user['is_root_message'] = False
        if user['rootMessageId'] == user['messageId']:
            rich_user['is_root_message'] = True

        if user['answer']:
            rich_user['type'] = 'answer'
            rich_user['is_message_answer'] = 1
            rich_user['is_message_post'] = 0
        else:
            rich_user['is_message_answer'] = 0
            rich_user['is_message_post'] = 1

        creation_date = unixtime_to_datetime(user['createDate'] / 1000).isoformat()
        rich_user['creation_date'] = creation_date
        rich_user.update(self.get_grimoire_fields(creation_date, "user"))

        if self.sortinghat:
            rich_user.update(self.get_item_sh(item))

        return rich_user
