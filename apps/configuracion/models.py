from django.db import models


class ConfiguracionEmergencia(models.Model):
    titulo = models.CharField(max_length=100, default="¿Tienes una emergencia?")
    mensaje = models.CharField(max_length=280, default="Si hay riesgo vital, llama ahora. Nuestro equipo está disponible para orientarte.")
    telefono = models.CharField(max_length=30, default="0988128636")
    whatsapp = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "configuración de emergencias"
        verbose_name_plural = "configuración de emergencias"

    def __str__(self):
        return self.titulo


class ConfiguracionPaginaPrincipal(models.Model):
    distintivo = models.CharField(max_length=100, default="Cuidado médico de confianza")
    titulo = models.CharField(max_length=180, default="Tu salud está en las mejores manos")
    descripcion = models.CharField(max_length=320, default="Contamos con médicos especialistas, tecnología moderna y atención personalizada para cuidar de ti y tu familia.")
    boton_principal = models.CharField(max_length=60, default="Agendar cita")
    boton_secundario = models.CharField(max_length=60, default="Contactar")
    pacientes_cifra = models.PositiveIntegerField(default=5000)
    pacientes_texto = models.CharField(max_length=80, default="Pacientes atendidos")
    medicos_cifra = models.PositiveIntegerField(default=50)
    medicos_texto = models.CharField(max_length=80, default="Médicos especialistas")
    experiencia_cifra = models.PositiveIntegerField(default=15)
    experiencia_texto = models.CharField(max_length=80, default="Años de experiencia")
    especialidades_cifra = models.PositiveIntegerField(default=20)
    especialidades_texto = models.CharField(max_length=80, default="Especialidades")
    titulo_especialidades = models.CharField(max_length=120, default="Especialidades médicas")
    descripcion_especialidades = models.CharField(max_length=220, default="Profesionales preparados para cuidar tu salud en cada etapa.")
    titulo_medicos = models.CharField(max_length=120, default="Médicos que cuidan de ti")
    descripcion_medicos = models.CharField(max_length=220, default="Especialistas comprometidos con tu bienestar y una atención cercana.")
    titulo_servicios = models.CharField(max_length=120, default="Nuestros servicios")
    descripcion_servicios = models.CharField(max_length=220, default="Soluciones pensadas para ofrecerte una experiencia de salud ágil y completa.")
    titulo_cta = models.CharField(max_length=160, default="Agenda una consulta con nuestros especialistas")
    texto_cta = models.CharField(max_length=80, default="Tu bienestar comienza hoy")
    mostrar_estadisticas = models.BooleanField(default=True)
    mostrar_especialidades = models.BooleanField(default=True)
    mostrar_medicos = models.BooleanField(default=True)
    mostrar_servicios = models.BooleanField(default=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "página principal"
        verbose_name_plural = "página principal"

    def __str__(self):
        return self.titulo


class ConfiguracionContacto(models.Model):
    titulo = models.CharField(max_length=120, default="Siempre cerca de ti")
    descripcion = models.CharField(max_length=300, default="Puedes comunicarte para solicitar orientación sobre servicios, especialistas y citas.")
    telefono = models.CharField(max_length=30, default="0988128636")
    correo = models.EmailField(default="contacto@clinicareina.com")
    ubicacion = models.CharField(max_length=180, default="Loja, Ecuador")
    horario = models.CharField(max_length=180, default="Lun–Vie 08:00–18:00")
    enlace_mapa = models.URLField(blank=True)
    facebook = models.URLField(blank=True, verbose_name="Facebook", help_text="Enlace completo al perfil de Facebook")
    instagram = models.URLField(blank=True, verbose_name="Instagram", help_text="Enlace completo al perfil de Instagram")
    whatsapp = models.URLField(blank=True, verbose_name="WhatsApp", help_text="Ejemplo: https://wa.me/593999999999")
    tiktok = models.URLField(blank=True, verbose_name="TikTok", help_text="Enlace completo al perfil de TikTok")
    youtube = models.URLField(blank=True, verbose_name="YouTube", help_text="Enlace completo al canal de YouTube")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn", help_text="Enlace completo al perfil de LinkedIn")
    activo = models.BooleanField(default=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "configuración de contacto"
        verbose_name_plural = "configuración de contacto"

    def __str__(self):
        return self.titulo
