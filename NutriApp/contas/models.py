from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, tipo, password=None):
        if not email:
            raise ValueError("Usuário deve ter um email válido")
        email = self.normalize_email(email)
        usuario = self.model(email=email, nome=nome, tipo=tipo)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nome, password=None):
        usuario = self.create_user(email, nome, tipo='ADMIN', password=password)
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPOS = (
        ('ADMIN', 'Administrador'),
        ('NUTRI', 'Nutricionista'),
        ('PAC', 'Paciente'),
    )

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=150)
    # Este campo define o papel do usuário (Nutricionista, Paciente, Admin)
    tipo = models.CharField(max_length=10, choices=TIPOS) 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
class NutricionistaProfile(models.Model):
    # Ligação OneToOne para garantir que cada Usuario (Nutri) tenha 1 perfil
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_nutricionista')
    endereco = models.CharField(max_length=255)
    celular = models.CharField(max_length=20)
    crn = models.CharField(max_length=20, unique=True)
    numero = models.CharField(max_length=10) 
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    uf = models.CharField(max_length=2,)
    cidade = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.usuario.nome} - CRN: {self.crn}"