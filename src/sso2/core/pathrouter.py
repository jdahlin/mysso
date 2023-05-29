from django.urls import path
from rest_framework.routers import DefaultRouter, DynamicRoute, Route
from rest_framework.viewsets import ModelViewSet


class PathRouter(DefaultRouter):
    include_format_suffixes = False
    include_root_view = False

    routes = [
        # List route.
        Route(
            url="{prefix}{trailing_slash}",
            mapping={"get": "list", "post": "create"},
            name="{basename}-list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset.
        DynamicRoute(
            url="{prefix}/{url_path}{trailing_slash}",
            name="{basename}-{url_name}",
            detail=False,
            initkwargs={},
        ),
        # Detail route.
        Route(
            url="{prefix}/{lookup}{trailing_slash}",
            mapping={
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            },
            name="{basename}-detail",
            detail=True,
            initkwargs={"suffix": "Instance"},
        ),
        # Dynamically generated detail routes. Generated using
        # @action(detail=True) decorator on methods of the viewset.
        DynamicRoute(
            url="{prefix}/{lookup}/{url_path}{trailing_slash}",
            name="{basename}-{url_name}",
            detail=True,
            initkwargs={},
        ),
    ]

    def get_lookup_path(self, viewset: ModelViewSet) -> str:
        lookup_field = getattr(viewset, "lookup_field", "pk")
        lookup_url_kwarg = getattr(viewset, "lookup_url_kwarg", None) or lookup_field
        lookup_value_converter = getattr(viewset, "lookup_value_converter", "str")
        return f"<{lookup_value_converter}:{lookup_url_kwarg}>"

    def get_urls(self) -> list[path]:
        ret = []
        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_path(viewset)
            routes = self.get_routes(viewset)
            for route in routes:
                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue
                initkwargs = route.initkwargs.copy()
                initkwargs.update(
                    {
                        "basename": basename,
                        "detail": route.detail,
                    },
                )
                route_path = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash,
                )
                view = viewset.as_view(mapping, **initkwargs)
                name = route.name.format(basename=basename)
                ret.append(path(route_path, view, name=name))
        return ret
