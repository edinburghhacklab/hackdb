# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import unittest

# from django.contrib.auth.hashers import make_password, check_password

from .hashers import SHA256PasswordHasher, SHA512PasswordHasher


# Test data from https://akkadia.org/drepper/SHA-crypt.txt
SHA256_TEST_DATA = [
    [
        "$5$saltstring",
        "Hello world!",
        "$5$saltstring$5B8vYYiY.CVt1RlTTf8KbXBH3hsxY/GNooZaBBGWEc5",
    ],
    [
        "$5$rounds=10000$saltstringsaltstring",
        "Hello world!",
        "$5$rounds=10000$saltstringsaltst$3xv.VbSHBb41AL9AvLeujZkZRBAwqFMz2."
        "opqey6IcA",
    ],
    [
        "$5$rounds=5000$toolongsaltstring",
        "This is just a test",
        # "$5$rounds=5000$toolongsaltstrin$Un/5jzAHMgOGZ5.mWJpuVolil07guHPvOW8mGRcvxa5",
        "$5$toolongsaltstrin$Un/5jzAHMgOGZ5.mWJpuVolil07guHPvOW8mGRcvxa5",
    ],
    [
        "$5$rounds=1400$anotherlongsaltstring",
        "a very much longer text to encrypt.  This one even stretches over more"
        "than one line.",
        "$5$rounds=1400$anotherlongsalts$Rx.j8H.h8HjEDGomFU8bDkXm3XIUnzyxf12"
        "oP84Bnq1",
    ],
    [
        "$5$rounds=77777$short",
        "we have a short salt string but not a short password",
        "$5$rounds=77777$short$JiO1O3ZpDAxGJeaDIuqCoEFysAe1mZNJRs3pw0KQRd/",
    ],
    [
        "$5$rounds=123456$asaltof16chars..",
        "a short string",
        "$5$rounds=123456$asaltof16chars..$gP3VQ/6X7UUEW3HkBn2w1/Ptq2jxPyzV/"
        "cZKmF/wJvD",
    ],
    [
        "$5$rounds=10$roundstoolow",
        "the minimum number is still observed",
        "$5$rounds=1000$roundstoolow$yfvwcWrQ8l/K0DAWyuPMDNHpIVlTQebY9l/gL97" "2bIC",
    ],
]

# Test data from https://akkadia.org/drepper/SHA-crypt.txt
SHA512_TEST_DATA = [
    [
        "$6$saltstring",
        "Hello world!",
        "$6$saltstring$svn8UoSVapNtMuq1ukKS4tPQd8iKwSMHWjl/O817G3uBnIFNjnQJu"
        "esI68u4OTLiBFdcbYEdFCoEOfaS35inz1",
    ],
    [
        "$6$rounds=10000$saltstringsaltstring",
        "Hello world!",
        "$6$rounds=10000$saltstringsaltst$OW1/O6BYHV6BcXZu8QVeXbDWra3Oeqh0sb"
        "HbbMCVNSnCM/UrjmM0Dp8vOuZeHBy/YTBmSK6H9qs/y3RnOaw5v.",
    ],
    [
        "$6$rounds=5000$toolongsaltstring",
        "This is just a test",
        # "$6$rounds=5000$toolongsaltstrin$lQ8jolhgVRVhY4b5pZKaysCLi0QBxGoNeKQzQ3glMhwllF7oGDZxUhx1yxdYcz/e1JSbq3y6JMxxl8audkUEm0",
        "$6$toolongsaltstrin$lQ8jolhgVRVhY4b5pZKaysCLi0QBxGoNeKQzQ3glMhwllF7oGDZxUhx1yxdYcz/e1JSbq3y6JMxxl8audkUEm0",
    ],
    [
        "$6$rounds=1400$anotherlongsaltstring",
        "a very much longer text to encrypt.  This one even stretches over more"
        "than one line.",
        "$6$rounds=1400$anotherlongsalts$POfYwTEok97VWcjxIiSOjiykti.o/pQs.wP"
        "vMxQ6Fm7I6IoYN3CmLs66x9t0oSwbtEW7o7UmJEiDwGqd8p4ur1",
    ],
    [
        "$6$rounds=77777$short",
        "we have a short salt string but not a short password",
        "$6$rounds=77777$short$WuQyW2YR.hBNpjjRhpYD/ifIw05xdfeEyQoMxIXbkvr0g"
        "ge1a1x3yRULJ5CCaUeOxFmtlcGZelFl5CxtgfiAc0",
    ],
    [
        "$6$rounds=123456$asaltof16chars..",
        "a short string",
        "$6$rounds=123456$asaltof16chars..$BtCwjqMJGx5hrJhZywWvt0RLE8uZ4oPwc"
        "elCjmw2kSYu.Ec6ycULevoBK25fs2xXgMNrCzIMVcgEJAstJeonj1",
    ],
    [
        "$6$rounds=10$roundstoolow",
        "the minimum number is still observed",
        "$6$rounds=1000$roundstoolow$kUMsbe306n21p9R.FRkW3IGn.S9NPN0x50YhH1x"
        "hLsPuWGsUSklZt58jaTfF4ZEQpyUNGc0dqbpBYYBaHHrsX.",
    ],
]


class PasswordHasherTestCase(unittest.TestCase):
    # def test_sha256_crypt(self):
    #     password = "password"
    #     hasher = SHA256PasswordHasher()
    #     hashed_password = make_password(password, hasher=hasher)
    #     self.assertEqual(hashed_password[0:16], "sha256_crypt$$5$")
    #     self.assertEqual(check_password(password, hashed_password), True)
    #     self.assertEqual(check_password("wrong_password", hashed_password), False)

    # def test_sha512_crypt(self):
    #     password = "password"
    #     hasher = SHA512PasswordHasher()
    #     hashed_password = make_password(password, hasher=hasher)
    #     self.assertEqual(hashed_password[0:16], "sha512_crypt$$6$")
    #     self.assertEqual(check_password(password, hashed_password), True)
    #     self.assertEqual(check_password("wrong_password", hashed_password), False)

    def test_sha256_reference_data(self):
        hasher = SHA256PasswordHasher()
        for prefix, plain, crypted in SHA256_TEST_DATA:
            if prefix.startswith("$5$rounds="):
                salt = prefix.split("$")[3]
                rounds = int(prefix.split("$")[2].split("=")[1])
            else:
                salt = prefix.split("$")[2]
                rounds = 5000
            hasher.iterations = rounds
            hashed_password = hasher.encode(plain, salt)
            self.assertEqual(hashed_password, "sha256_crypt$" + crypted)

    def test_sha512_reference_data(self):
        hasher = SHA512PasswordHasher()
        for prefix, plain, crypted in SHA512_TEST_DATA:
            if prefix.startswith("$6$rounds="):
                salt = prefix.split("$")[3]
                rounds = int(prefix.split("$")[2].split("=")[1])
            else:
                salt = prefix.split("$")[2]
                rounds = 5000
            hasher.iterations = rounds
            hashed_password = hasher.encode(plain, salt)
            self.assertEqual(hashed_password, "sha512_crypt$" + crypted)
