from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms

class SequencesFileUploadForm(forms.Form):
	jsonFile = forms.FileField(label="Choose a sequence JSON file")
    
class LocationsFileUploadForm(forms.Form):
	csvFile = forms.FileField(label="Choose a location csv file")
	
class ElephantsFileUploadForm(forms.Form):
	eleFile = forms.FileField(label="Choose a elephants tab delimited file")