# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.hashers import BasePasswordHasher, get_random_string, mask_hash
from passlib.hash import sha256_crypt, sha512_crypt


class SHA256PasswordHasher(BasePasswordHasher):
    algorithm = "sha256_crypt"
    salt_entropy = 95
    iterations = 535000

    def salt(self):
        return get_random_string(16)

    def verify(self, password, encoded):
        return sha256_crypt.verify(password, encoded.split("$", 1)[1])

    def encode(self, password, salt):
        if self.iterations < 1000:
            self.iterations = 1000
        return (
            self.algorithm
            + "$"
            + sha256_crypt.hash(password, salt=salt[0:16], rounds=self.iterations)
        )

    def decode(self, encoded):
        if encoded.startswith(self.algorithm + "$$5$rounds="):
            algorithm, void, void, rounds, salt, hash = encoded.split("$", 5)
            iterations = int(rounds.split("=", 1)[1])
        elif encoded.startswith(self.algorithm + "$$5$"):
            algorithm, void, void, salt, hash = encoded.split("$", 4)
            iterations = 5000
        else:
            raise ValueError("password format not recognised")
        return {
            "algorithm": algorithm,
            "iterations": int(iterations),
            "salt": salt,
            "hash": hash,
        }

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            "algorithm": decoded["algorithm"],
            "iterations": decoded["iterations"],
            "salt": mask_hash(decoded["salt"]),
            "hash": mask_hash(decoded["hash"]),
        }

    def harden_runtime(self, password, encoded):
        pass


class SHA512PasswordHasher(BasePasswordHasher):
    algorithm = "sha512_crypt"
    salt_entropy = 95
    iterations = 656000

    def salt(self):
        return get_random_string(16)

    def verify(self, password, encoded):
        return sha512_crypt.verify(password, encoded.split("$", 1)[1])

    def encode(self, password, salt):
        if self.iterations < 1000:
            self.iterations = 1000
        return (
            self.algorithm
            + "$"
            + sha512_crypt.hash(password, salt=salt[0:16], rounds=self.iterations)
        )

    def decode(self, encoded):
        if encoded.startswith(self.algorithm + "$$6$rounds="):
            algorithm, void, void, rounds, salt, hash = encoded.split("$", 5)
            iterations = int(rounds.split("=", 1)[1])
        elif encoded.startswith(self.algorithm + "$$6$"):
            algorithm, void, void, salt, hash = encoded.split("$", 4)
            iterations = 5000
        else:
            raise ValueError("password format not recognised")
        return {
            "algorithm": algorithm,
            "iterations": int(iterations),
            "salt": salt,
            "hash": hash,
        }

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            "algorithm": decoded["algorithm"],
            "iterations": decoded["iterations"],
            "salt": mask_hash(decoded["salt"]),
            "hash": mask_hash(decoded["hash"]),
        }

    def harden_runtime(self, password, encoded):
        pass
