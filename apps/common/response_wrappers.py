from rest_framework import status
from rest_framework.response import Response


def bad_request_response(error_code: str):
    return Response(data={"error_code": error_code},
                    status=status.HTTP_400_BAD_REQUEST)
