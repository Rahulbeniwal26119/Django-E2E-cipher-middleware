from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
import json
from gateway.response_helpers import http_response


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
def calculate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        num1 = int(data.get("num1"))
        num2 = int(data.get("num2"))
        if not all([num1, num2]):
            return http_response(400, "Invalid request. num1 and num2 expected")
        result = num1 + num2
        return http_response(200, "Success", {"result": result})
    else:
        return http_response(400, "Invalid request. POST request expected")


@csrf_exempt
def calculate_template(request):
    if request.method == "POST":
        data = json.loads(request.body)
        num1 = int(data.get("num1"))
        num2 = int(data.get("num2"))
        if not all([num1, num2]):
            return HttpResponse(400, "Invalid request. num1 and num2 expected")
        result = num1 + num2
        return HttpResponse(f"<b> Sum : {result} </b>")
    else:
        return HttpResponse("Invalid request. POST request expected", status=400)
