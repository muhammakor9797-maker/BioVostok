from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns, set_language

from goods.views import index, catalog, product_detail, sitemap_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', set_language, name='set_language'),
    path('users/', include('users.urls')),
    path('cart/', include('carts.urls')),
    path('orders/', include('orders.urls')),
    path('sitemap.xml', sitemap_view, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

urlpatterns += i18n_patterns(
    path('', index, name='home'),
    path('catalog/', catalog, name='catalog'),
    path('product/<slug:product_slug>/', product_detail, name='product_detail'),
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)