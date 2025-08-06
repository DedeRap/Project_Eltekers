from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Manager model pengguna kustom yang disesuaikan untuk mewajibkan nomor telepon.
    """
    def create_user(self, username, password, **extra_fields):
        """
        Membuat dan menyimpan User dengan username, password, dan nomor telepon.
        """
        if not username:
            raise ValueError('Username harus diisi')
        
        # Memastikan nomor telepon ada di dalam extra_fields
        if 'nomor_telepon' not in extra_fields:
            raise ValueError('Nomor Telepon harus diisi')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Membuat dan menyimpan SuperUser dengan username dan password.
        """
        # Set default value untuk field yang wajib ada di superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        # Saran: Atur level superuser ke level tertinggi (Admin)
        extra_fields.setdefault('level', 5)

        # Validasi field superuser
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser harus memiliki is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser harus memiliki is_superuser=True.')
        
        # Panggil metode create_user utama untuk membuat pengguna
        return self.create_user(username, password, **extra_fields)