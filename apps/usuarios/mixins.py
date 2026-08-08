from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Perfil


class PerfilActivoRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        perfil, _ = Perfil.objects.get_or_create(usuario=self.request.user, defaults={"rol": Perfil.Rol.ADMIN if self.request.user.is_superuser else Perfil.Rol.PACIENTE})
        return perfil.activo


class RolesRequiredMixin(PerfilActivoRequiredMixin):
    roles_permitidos = ()

    def test_func(self):
        return super().test_func() and (self.request.user.is_superuser or self.request.user.perfil.rol in self.roles_permitidos)
