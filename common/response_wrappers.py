from rest_framework import status
from rest_framework.response import Response


def success_response(data: dict):
    wrapped_data = {
        "success": True,
        "data": data
    }
    return Response(data=wrapped_data, status=status.HTTP_200_OK)


def bad_request(error_code: str):
    wrapped_data = {
        "success": False,
        "error_code": error_code
    }
    return Response(data=wrapped_data, status=status.HTTP_400_BAD_REQUEST)



