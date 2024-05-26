from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver


# User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number

# Destination Model
class Destination(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='voyage')
    montant = models.PositiveBigIntegerField(default=0)
    def __str__(self):
        return self.name

# Ticket Model
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    is_confirmed = models.BooleanField(default=False)
    amount_paid = models.PositiveBigIntegerField(default=0)
    pdf = models.FileField(upload_to='tickets/', null=True, blank=True)  # Champ pour le fichier PDF


    def __str__(self):
        return f"{self.user.phone_number} - {self.destination.name}"

# Payment Model
class Payment(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)

    def simulate_payment(self):
        if self.ticket.amount_paid == self.ticket.destination.montant:
            self.ticket.is_confirmed = True
            self.ticket.save()
            return True  # Simulation de paiement réussie
        else:
            return False  # Simulation de paiement échouée

    def __str__(self):
        return f"Payment for ticket {self.ticket.id}"

# Signal pour déclencher la simulation de paiement après la création d'un paiement
@receiver(post_save, sender=Payment)
def simulate_payment(sender, instance, created, **kwargs):
    if created:
        instance.simulate_payment()