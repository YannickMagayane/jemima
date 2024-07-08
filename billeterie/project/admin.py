from django.contrib import admin
from .models import User, Destination, Ticket, Payment,Bus

# Custom Admin for User
admin.site.register(User)

# Admin for Destination

admin.site.register(Destination)

# Admin for Ticket
admin.site.register(Ticket)

# Admin for Payment
admin.site.register(Payment)

#bus
admin.site.register(Bus)
