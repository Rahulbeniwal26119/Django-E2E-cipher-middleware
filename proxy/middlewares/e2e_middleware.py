import json

from django.urls import resolve
from django.http import Http404

from gateway.response_helpers import http_response
import proxy.custom_exceptions as custom_exceptions
from proxy.cryptography_utils import decrypt_payload, encrypt_payload


class E2EMiddleware:
    def __init__(self, get_response):
        # This get_reponse may be the next middleware in the chain or the view
        self.get_response = get_response

    def __call__(self, request):
        # check if the request is a POST request
        if request.method in ["GET", "DELETE"]:
            return self.get_response(request)

        # check if url present in system
        try:
            resolve(request.path)
        except Http404:
            return http_response(404, "Invalid request. URL not found")

        # check if request has valid json data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return http_response(400, "Invalid request. JSON data expected")

        # check if the request has the required fields
        payload = data.get("payload")
        checksum = data.get("checksum")

        if not all([payload, checksum]):
            return http_response(400, "Invalid request. payload and checksum expected")

        # get key from headers
        key = request.headers.get("Encryption-Key")
        if not key:
            return http_response(400, "Invalid request. Encryption-Key header expected")

        # decrypt the payload
        try:
            decrypted_payload = decrypt_payload(payload, checksum, key)
        except custom_exceptions.InvalidHashException:
            return http_response(400, "Invalid request. Invalid checksum")
        except custom_exceptions.DecryptionFailure:
            return http_response(400, "Invalid request. Decryption failed")
        except json.JSONDecodeError:
            return http_response(
                400, "Invalid request. Invalid payload. JSON data expected"
            )

        # pass the decrypted payload to the next middleware or view
        request._body = json.dumps(decrypted_payload)
        response = self.get_response(request)

        # in case of template response, we donot encrypt the response
        if (
            hasattr(response, "render") and callable(response.render)
        ) or not response.headers.get("Content-Type", "").startswith(
            "application/json"
        ):
            return response

        # response is not OK then donot encrypt the response
        if response.status_code not in [200, 201]:
            return response
        else:
            # encrypt the response
            response_data = json.loads(response.content.decode("utf-8"))
            encrypted_data, digest = encrypt_payload(response_data, key)
            return http_response(200, "Success", {"payload": encrypted_data, "checksum": digest})
