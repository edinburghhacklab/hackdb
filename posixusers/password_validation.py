# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from passlib.hash import sha512_crypt


class UpdatePosixPassword:
    def get_help_text(self):
        return ""

    def password_changed(self, password, user=None):
        if user:
            user.posix.password = sha512_crypt.hash(password)
            user.posix.save()

    def validate(self, password, user=None):
        pass
