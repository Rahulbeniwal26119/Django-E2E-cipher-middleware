# Encryption process

body = {"num1": "10", "num2": "20"}

from proxy.cryptography_utils import encrypt_payload, decrypt_payload

encrypt_payload(body, "d1ac58881d60188f7ec65e4a8b43eff1ede175ae62a8a35e")

# ('897afe5b8d5d60955221adfc243e94d2cf9fae5d9b23f4344930178d84748d99',
#  'ade4b2e54e66e0ace0c800143f20095ec1411df65daf9a4699e799eb3f2739b3205b3c8b9469fc2b4f7dd4e16fb25707afed93333c0661a17e1f2e03a55e58c2')

# Decryption Process

encrypted_res = {
    "payload": "f03217c5278baf57ccf0d6b7f8225d31",
    "checksum": "8f8360acf8f45e9f22e516311187638f4d02a688360fb67c68cce38ae97fe5c094ef3627e96926a842afe635fa5d24312e06fda71f879359062b851b625b18c9",
}

decrypt_payload(
    encrypted_res["payload"],
    encrypted_res["checksum"],
    "d1ac58881d60188f7ec65e4a8b43eff1ede175ae62a8a35e",
)

# {'result': 30}
