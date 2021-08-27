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
        (MID, 'middle'),
        (BOT, 'bottom'),
    )
    
    SIZE_TOP = [1100, 87]
    SIZE_MID = [72, 72]
    SIZE_BOT = [353, 105]
    
    name = models.CharField(max_length=32, blank=True, help_text='Company name (only for middle position)')
    sub_name = models.CharField(max_length=32, blank=True, help_text='Company tag (only for middle position)')
    icon = models.ImageField(upload_to='img-%Y-%m-%d/',
                             help_text=f'image (for top position not less than {SIZE_TOP[0]}px/{SIZE_TOP[1]}px,\n'
                                       f'for middle position not less than {SIZE_MID[0]}px/{SIZE_MID[1]}px,\n'
                                       f'for bottom position not less than {SIZE_BOT[0]}px/{SIZE_BOT[1]}px)')
    description = models.CharField(max_length=128, blank=True,
                                   help_text='Company description (only for middle position)')
    position = models.CharField(max_length=3, choices=POS, help_text='max count for top=1, middle=3, bottom=3')
    hash = models.CharField(max_length=256, blank=True, help_text='Hash for ipfs')

    def save(self, *args, **kwargs):
        if self.position == self.TOP:
            if not (self.icon.width >= self.SIZE_TOP[0] and self.icon.height >= self.SIZE_TOP[1]):
                raise ImgError(f'img is smaller than {self.SIZE_TOP}')
        elif self.position == self.MID:
            if not (self.icon.width >= self.SIZE_MID[0] and self.icon.height >= self.SIZE_MID[1]
                    and len(self.name) >= 2 and len(self.sub_name) >+ 3 and len(self.description) >= 10):
                raise ImgError(f'img is smaller than {self.SIZE_MID} or name/sub_name/description is too short')
        elif self.position == self.BOT:
            if not (self.icon.width >= self.SIZE_BOT[0] and self.icon.height >= self.SIZE_BOT[1]):
                raise ImgError(f'img is smaller than {self.SIZE_BOT}')
        super(ADV, self).save(*args, **kwargs)

    def get_ipfs_img(self):
        """Give url if server can't give img"""
        return f'https://ipfs.io/ipfs/{self.hash}'

    def __str__(self):
        return f'{self.name} {self.position}'
