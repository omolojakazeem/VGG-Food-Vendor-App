from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="VGG Food Vendor API ",
        default_version='v1',
        description="Developed by Kazeem Omoloja - Python Track",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    path('admin/', admin.site.urls),
    path('api/v1/customers/', include('customer.urls')),
    path('api/v1/vendors/', include('vendor.urls')),
    path('api/v1/orders/', include('order.urls')),
    path('api/v1/accounts/', include('account.urls')),
    path('api/v1/notifications/', include('notify.urls')),
    path('api/v1/menus/', include('menu.urls')),
    path('api/v1/payment/', include('payment.urls')),
    path('api/v1/', include('django.contrib.auth.urls')),

    path('swagger(<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('documentation/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]
