from drf_spectacular.utils import OpenApiExample


from drf_spectacular.utils import OpenApiResponse
from rest_framework import status
from rest_framework.serializers import Serializer, CharField


class Error400Serializer(Serializer):
    detail = CharField(default="Bad Request", help_text="Error message")


class Error401Serializer(Serializer):
    detail = CharField(default="Unauthorized", help_text="Error message")


class Error403Serializer(Serializer):
    detail = CharField(default="Forbidden", help_text="Error message")


class Error404Serializer(Serializer):
    detail = CharField(example="Not found.", help_text="Error message")


api_400 = OpenApiResponse(
    response=Error400Serializer,
    description="Bad Request",
    examples=[
        OpenApiExample(
            'Invalid input',
            value={'detail': 'Invalid data provided'},
            status_codes=[str(status.HTTP_400_BAD_REQUEST)],
        ),
    ]
)

api_401 = OpenApiResponse(
    response=Error401Serializer,
    description="Unauthorized",
    examples=[
        OpenApiExample(
            'Unauthorized access',
            value={'detail': 'Authentication credentials were not provided'},
            status_codes=[str(status.HTTP_401_UNAUTHORIZED)],
        ),
    ]
)

api_403 = OpenApiResponse(
    response=Error403Serializer,
    description="Forbidden",
    examples=[
        OpenApiExample(
            'Forbidden access',
            value={'detail': 'You do not have permission to perform this action.'},
            status_codes=[str(status.HTTP_403_FORBIDDEN)],
        ),
    ]
)

api_404 = OpenApiResponse(
    response=Error404Serializer,
    description="Not Found",
    examples=[
        OpenApiExample(
            'Quiz not found',
            value={'detail': 'Not found.'},
            status_codes=[str(status.HTTP_404_NOT_FOUND)],
        ),
    ]
)
