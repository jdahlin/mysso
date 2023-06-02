from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from sso2.oauth.models import OAuth2Client
from sso2.oauth.models.oauth2_client_model import OAuth2ClientCredential


class ApplicationSerializer(ModelSerializer):
    tenant = SerializerMethodField()

    def get_tenant(self, client: OAuth2Client) -> str:
        return client.tenant.name

    class Meta:
        model = OAuth2Client
        fields = "__all__"


class ApplicationCredentialSerializer(ModelSerializer):
    class Meta:
        model = OAuth2ClientCredential
        fields = "__all__"
        ordering = ["-created_at"]

    def create(self, validated_data: dict[str, Any]) -> OAuth2ClientCredential:
        as_bytes = validated_data["pem_data"].encode("utf-8")
        certificate = x509.load_pem_x509_certificate(as_bytes)
        # A x509 certificate has a fingerprint which is required to be in SHA1
        validated_data["thumbprint"] = (
            certificate.fingerprint(hashes.SHA1()).hex().upper()  # noqa: S303
        )
        return super().create(validated_data)


class ApplicationViewSet(ModelViewSet):
    queryset = OAuth2Client.objects.all()
    serializer_class = ApplicationSerializer
    filter_backends = [OrderingFilter]
    lookup_field = "pk"
    lookup_url_kwarg = "client_id"
    lookup_value_converter = "int"
    # This will be used as the default ordering
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def credential(self, request: Request, client_id: str) -> Response:
        errors = []
        self.get_object()
        request.data["client"] = client_id
        request.data["tenant"] = request.tenant.id
        serializer = ApplicationCredentialSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            errors = e.detail
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            serializer.save()
            status_code = status.HTTP_201_CREATED

        response = {}
        if errors:
            response["errors"] = errors
        return Response(response, status=status_code)
