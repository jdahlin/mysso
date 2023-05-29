from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from sso2.core.models import Tenant


class TenantSerializer(ModelSerializer):
    issuer = SerializerMethodField()

    def get_issuer(self, tenant: Tenant) -> str:
        return tenant.get_issuer()

    class Meta:
        model = Tenant
        fields = "__all__"


class TenantViewSet(ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    lookup_url_kwarg = "tenant_id"
    lookup_value_converter = "uuid"
