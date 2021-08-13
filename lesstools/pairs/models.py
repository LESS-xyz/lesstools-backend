from django.db import models


class Pairs(models.Model):
    """New pairs"""
    main_currency = models.CharField(max_length=4, blank=False)
    sub_currency = models.CharField(max_length=4, blank=False)
    likes = models.PositiveSmallIntegerField(default=0, editable=False)
    dislikes = models.PositiveSmallIntegerField(default=0, editable=False)
    # users' trust in the pair
    trust = models.PositiveSmallIntegerField(default=0, auto_created=True, editable=False)

    def like(self):
        self.likes += 1
        return self.save()

    def dislike(self):
        self.dislikes += 1
        return self.save()
