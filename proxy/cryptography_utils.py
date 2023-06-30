import json
import typing
import binascii
import logging
from hashlib import sha512

from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes

from proxy import custom_exceptions

# create a custom type for JSON
JSON = typing.Union[dict, list]

logger = logging.getLogger(__name__)


def pad(data: str, block_size: int) -> str:
    pad_len = block_size - len(data) % block_size
    return data + pad_len * chr(pad_len)


def encrypt(data: bytes, key: bytes) -> str:
    cipher = DES3.new(key, DES3.MODE_ECB)
    ct_bytes = cipher.encrypt(data)
    return binascii.hexlify(ct_bytes).decode("utf-8")


def decrypt(data: str, key: bytes) -> str:
    cipher = DES3.new(key, DES3.MODE_ECB)

    ct_bytes = binascii.unhexlify(data)
    pt = cipher.decrypt(ct_bytes).decode("utf-8")
    pad_len = ord(pt[-1])
    return pt[:-pad_len]


def parse_json(data: str | bytes) -> JSON:
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return json.loads(data)


def generate_hash(data: str) -> str:
    return sha512(data.encode("utf-8")).hexdigest()


def validate_hash(data: str, digest: str) -> bool:
    return generate_hash(data) == digest


def decrypt_payload(encrypted_data: str, digest: str, key: str | bytes) -> list | dict:
    # verify the hash
    if isinstance(key, str):
        key = binascii.unhexlify(key)
    try:
        decrypted_data = decrypt(encrypted_data, key)
    except custom_exceptions.DecryptionFailure:
        raise custom_exceptions.DecryptionFailure()
    except Exception as e:
        logger.error(e)
        raise custom_exceptions.DecryptionFailure()
    if not validate_hash(decrypted_data, digest):
        raise custom_exceptions.InvalidHashException()
    try:
        return parse_json(decrypted_data)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError() from e


def encrypt_payload(data: list | dict, key: str | bytes) -> tuple[str, str]:
    if not isinstance(key, bytes):
        key = binascii.unhexlify(key)
    if isinstance(data, (list, dict)):
        data = json.dumps(data)
    padded_input = pad(data, DES3.block_size)
    encrypted_data = encrypt(padded_input.encode("utf-8"), key)
    digest = generate_hash(data)
    return encrypted_data, digest


def generate_key() -> str:
    key = binascii.hexlify(get_random_bytes(24)).decode("utf-8")
    logger.info("Generated key: {}".format(key))
    return key
