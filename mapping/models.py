from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Publications(models.Model):
    author = models.CharField(max_length=30)
    paperurl = models.CharField(max_length=1000, null=False)
    oldPk = models.IntegerField(null=True)
    datetimeModified = models.DateTimeField()
    lastEditedBy = models.CharField(max_length=30,null=True)
    lastEditNotes = models.TextField(null=True)

class Locations(models.Model):
    locationName = models.TextField()
    lon = models.FloatField()
    lat = models.FloatField()
    locationType = models.TextField()
    matchNotes = models.TextField()
    locality = models.CharField(max_length=30)
    accuracy = models.IntegerField()
    oldPk = models.IntegerField(null=True)
    datetimeModified = models.DateTimeField()
    lastEditedBy = models.CharField(max_length=30,null=True)
    lastEditNotes = models.TextField(null=True)



class Sequences(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    seq = models.TextField()
    oldPk = models.IntegerField(null=True)
    datetimeModified = models.DateTimeField()
    lastEditedBy = models.CharField(max_length=30,null=True)
    lastEditNotes = models.TextField(null=True)


class LocHapPub(models.Model):
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    haplotype = models.ForeignKey(Sequences, on_delete=models.CASCADE)
    #genebankAccession = models.CharField(max_length=30)
    author = models.ForeignKey(Publications, on_delete=models.CASCADE, null=True)
    oldPk = models.IntegerField(null=True)
    datetimeModified = models.DateTimeField()
    lastEditedBy = models.CharField(max_length=30,null=True)
    lastEditNotes = models.TextField(null=True)


class LHPIndividual(models.Model):
    LHP = models.ForeignKey(LocHapPub, on_delete=models.CASCADE, null=True)
    genBankAccession = models.CharField(max_length=30,null=True)
    numElephants = models.IntegerField(null=True)
    datetimeModified = models.DateTimeField()
    lastEditedBy = models.CharField(max_length=30,null=True)
    lastEditNotes = models.TextField(null=True)
