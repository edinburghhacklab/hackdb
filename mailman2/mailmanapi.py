# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import requests
from django.conf import settings


def get_list(list_name):
    response = requests.get(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    response.raise_for_status()
    return response.json()


def get_lists():
    response = requests.get(
        f"{settings.MAILMAN_API_URL}/lists",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    response.raise_for_status()
    return response.json()


def get_list_member_data(list_name, email):
    response = requests.get(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}/members/{email}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


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
    response.raise_for_status()
    return True


def unsubscribe(list_name, email):
    response = requests.delete(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}/members/{email}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
    )
    response.raise_for_status()
    return True


def change_address(list_name, old_address, new_address):
    response = requests.patch(
        f"{settings.MAILMAN_API_URL}/lists/{list_name}/members/{old_address}",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
        json={"address": new_address},
    )
    response.raise_for_status()
    return True


def global_change_address(old_address, new_address):
    response = requests.post(
        f"{settings.MAILMAN_API_URL}/members/{old_address}/change_address",
        auth=(settings.MAILMAN_API_USERNAME, settings.MAILMAN_API_PASSWORD),
        json={"new_address": new_address},
    )
    response.raise_for_status()
    return True
