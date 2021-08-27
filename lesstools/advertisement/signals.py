from django.db.models.signals import post_save
from django.dispatch import receiver
from lesstools.advertisement.models import ADV
import ipfshttpclient


@receiver(post_save, sender=ADV)
def ipfs_add_img(sender, instance, created, **kwargs):
    try:
        client = ipfshttpclient.connect('/dns/144.76.201.50/tcp/6001/http')
        file_res = client.add(instance.icon.path)
        instance.hash = file_res['Hash']
        instance.save()
    except Exception as e:
        print(e)
