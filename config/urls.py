from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard.admin_site import clinica_admin_site

urlpatterns = [
    path("", include(("apps.pagina.urls", "pagina"), namespace="pagina")),
    path("admin/", clinica_admin_site.urls),
    path("usuarios/", include("apps.usuarios.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("medicos/", include("apps.medicos.urls")),
    path("especialidades/", include("apps.especialidades.urls")),
    path("citas/", include("apps.citas.urls")),
    path("historial/", include("apps.historial.urls")),
    path("recetas/", include("apps.recetas.urls")),
    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
