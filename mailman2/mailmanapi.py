# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import requests
from django.conf import settings


def get_list(list_name):
    return requests.get(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    ).json()


def get_lists():
    return requests.get(
        f"{settings.MAILMAN_API_URL}/lists",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    ).json()


def get_list_member_data(list_name, email):
    response = requests.get(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}/members/{email}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    if response:
        return response.json()
    else:
        return None


def is_subscribed(list_name, email):
    response = requests.get(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}/members/{email}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    if response:
        return True
    else:
        return False


def get_list_members(list_name):
    response = requests.get(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}/members",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    if response:
        return response.json()
    else:
        return []


def get_member(email):
    response = requests.get(
        f"{settings.MAILMAN_API_URL}/members/{email}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    if response:
        return response.json()
    else:
        return None


def subscribe(list_name, email):
    response = requests.post(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}/members/{email}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    if response and response.status_code == 200:
        return True
    else:
        return False


def unsubscribe(list_name, email):
    response = requests.delete(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}/members/{email}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    if response and response.status_code == 200:
        return True
    else:
        return False


def change_address(old_address, new_address):
    response = requests.post(
        f"{settings.MAILMAN_API_URL}/members/{old_address}/change_address",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
        json={"new_address": new_address},
    )
    if response and response.status_code == 200:
        return True
    else:
        return False
