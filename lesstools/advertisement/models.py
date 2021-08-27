from django.db import models
from django.contrib.postgres.fields import ArrayField


class ImgError(Exception):
    """Custom Exception for check img settings"""
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'Img error, can\'t save img, because {self.message}'
        else:
            return 'Img error'


class ADV(models.Model):
    """ADV position to web page"""
    TOP = 'TOP'
    MID = 'MID'
    BOT = 'BOT'
    POS = (
        (TOP, 'top'),
        (MID, 'mid'),
        (BOT, 'bot'),
    )
    
    SIZE_TOP = [1100, 87]
    SIZE_MID = [72, 72]
    SIZE_BOT = [353, 105]
    
    name = models.CharField(max_length=32, blank=True, help_text='Company name (only for MID position)')
    sub_name = models.CharField(max_length=32, blank=True, help_text='Company tag (only for MID position)')
    icon = models.ImageField(upload_to='img-%Y-%m-%d/', help_text='image ('
                                                                  f'for TOP position not less than {SIZE_TOP[0]}px/{SIZE_TOP[1]}px,\n'
                                                                  f'for MID position not less than {SIZE_MID[0]}px/{SIZE_MID[1]}px,\n'
                                                                  f'for BOT position not less than {SIZE_BOT[0]}px/{SIZE_BOT[1]}px)')
    description = models.CharField(max_length=128, blank=True, help_text='Company description (only for MID position)')
    position = models.CharField(max_length=3, choices=POS, default='MID', help_text='max count for TOP=1, MID=3, BOT=3')
    hash = models.CharField(max_length=256, blank=True, help_text='Hash for ipfs')

    def save(self, *args, **kwargs):
        if self.position == 'TOP' and self.icon.width < self.SIZE_TOP[0] and self.icon.height < self.SIZE_TOP[1]:
            raise ImgError(f'img width or height less than {self.SIZE_TOP[0]} or/and {self.SIZE_TOP[1]}')
        elif self.position == 'MID' and self.icon.width < self.SIZE_MID[0] and self.icon.height < self.SIZE_MID[1]\
                or len(self.name) < 2 or len(self.sub_name) < 3 or len(self.description) < 10:
            raise ImgError(f'img width or height less than {self.SIZE_MID} or name/sub_name/description too short')
        elif self.position == 'BOT' and self.icon.width < self.SIZE_BOT[0] and self.icon.height < self.SIZE_BOT[1]:
            raise ImgError(f'img width or height less than {self.SIZE_BOT[0]} or/and {self.SIZE_BOT[1]}')
        super(ADV, self).save(*args, **kwargs)

    def get_ipfs_img(self):
        """Give url if server can't give img"""
        return f'https://ipfs.io/ipfs/{self.hash}'

    def __str__(self):
        return f'{self.name} {self.position}'
