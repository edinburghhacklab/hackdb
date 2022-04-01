# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from . import mailmanapi
from .models import MailingList


def mailman2_prompts(request):
    try:
        member = mailmanapi.get_member(request.user.email)
        if member is None:
            return ""
    except:
        return ""

    data = []
    for mailing_list in MailingList.objects.order_by("name"):
        if mailing_list.name not in member:
            text = mailing_list.user_prompt(request.user)
            if text:
                data.append({"list_name": mailing_list.name, "message": text})

    return {
        "mailman2_prompts": data,
    }
