from django.http import HttpResponse
import json


def http_response(status_code, message, data={}) -> HttpResponse:
    return HttpResponse(
        json.dumps(
            {
                "status_code": status_code,
                "message": message,
                "data": data,
            }
        ),
        content_type="application/json",
        status=status_code,
    )
