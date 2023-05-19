from django.db.models import CASCADE, DateTimeField, ForeignKey, Model, TextField


class OAuth2AuthorizedApp(Model):
    class Meta:
        verbose_name = "OAuth2 Authorized Application"
        verbose_name_plural = "OAuth2 Authorized Applications"
        unique_together = ["tenant", "client", "user"]

    tenant = ForeignKey("core.Tenant", on_delete=CASCADE)
    client = ForeignKey("oauth.OAuth2Client", on_delete=CASCADE)
    user = ForeignKey("core.User", on_delete=CASCADE)
    scope = TextField()
    approved_at = DateTimeField(auto_now_add=True)
