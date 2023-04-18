import typer

from sso2.core.models.tenant_model import Tenant


def get_tenant_or_exit(tenant: str) -> Tenant:
    try:
        return Tenant.objects.get(name=tenant)
    except Tenant.DoesNotExist:
        typer.echo(f"No such tenant: {tenant}")
        raise typer.Exit(1) from None


TenantOption = typer.Option("master", "--tenant")
