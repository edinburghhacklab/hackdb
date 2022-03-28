# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from . import mailmanapi
from .models import MailingList
from .utils import user_prompt


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
            text = user_prompt(request.user, mailing_list)
            if text:
                data.append({"list_name": mailing_list.name, "message": text})

    return {
        "mailman2_prompts": data,
    }
