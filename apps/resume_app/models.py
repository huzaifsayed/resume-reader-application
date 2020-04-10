from django.db import models

class Resume(models.Model):
    name = models.CharField('Name', max_length=30, blank=True, null=True)
    email = models.CharField('Email', max_length=30, blank=True, null=True)
    phone_number = models.CharField('Phone Number', max_length=12, blank=True, null=True)
    linkedin_url = models.CharField('Linkedin Url', max_length=60, blank=True, null=True)
    skills = models.CharField('Skills', max_length=60, blank=True, null=True)
    education = models.CharField('Education', max_length=60, blank=True, null=True)
    total_lines = models.IntegerField('Total No. of Text Lines', blank=True, null=True)
    total_char = models.IntegerField('Total No. of Text characters', blank=True, null=True)
    total_words = models.IntegerField('Total No. of Text characters', blank=True, null=True)
    font_name = models.CharField('Font Name', max_length=30, blank=True, null=True)
    font_size = models.CharField('Font Size', max_length=30, blank=True, null=True)
    total_images = models.IntegerField('Total No. of Images', blank=True, null=True)
    total_tables = models.IntegerField('Total No. of Tables', blank=True, null=True)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
