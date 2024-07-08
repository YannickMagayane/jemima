from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

# User Manager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Vous devez mettre une adresse mail')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superuser n\'est pas activé')

        return self._create_user(email, password, **extra_fields)

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(('email address'), unique=True)
    first_name = models.CharField(('first name'), max_length=30, blank=True)
    last_name = models.CharField(('last name'), max_length=30, blank=True)
    phone_number = models.CharField(max_length=100,unique=True,blank=True)
    date_joined = models.DateTimeField(('date joined'), auto_now_add=True)
    is_active = models.BooleanField(('active'), default=True)
    is_staff = models.BooleanField(('staff'), default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')

    def get_full_name(self, full_name=None):
        nom_complet = '%s %s' % (self.first_name, self.last_name)
        return nom_complet.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)



#bus
class Bus(models.Model):
    nom_bus = models.CharField(max_length=50)
    nombre_place = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nom_bus


# Destination Model
class Destination(models.Model):
    name = models.CharField(max_length=100)
    heure_depart = models.TimeField()
    bus = models.ForeignKey(Bus,on_delete=models.CASCADE)
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