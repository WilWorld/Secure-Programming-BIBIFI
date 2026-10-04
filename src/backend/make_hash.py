"""Create an Argon2id hash for seed.sql:  python make_hash.py"""
import getpass

from argon2 import PasswordHasher

print(PasswordHasher().hash(getpass.getpass("Password: ")))