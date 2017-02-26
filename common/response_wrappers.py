from rest_framework import status
from rest_framework.response import Response


def bad_request_response(error_code: str):
    wrapped_data = {
        "error_code": error_code
    }
    return Response(data=wrapped_data, status=status.HTTP_400_BAD_REQUEST)
