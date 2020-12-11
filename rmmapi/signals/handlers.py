from django.dispatch import receiver
from django.db.models.signals import pre_save

@receiver(pre_save)
def pre_save_handler(sender, instance, *args, **kwargs):
    instance.full_clean()
