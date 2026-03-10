from django.db import models


class ProjectMaterial(models.Model):
    title = models.CharField(max_length=200)

    excel_file = models.FileField(upload_to='materials/excel/', blank=True, null=True)
    excel_link = models.URLField(blank=True, null=True)

    github_link = models.URLField(blank=True, null=True)

    powerpoint_file = models.FileField(upload_to='materials/powerpoint/', blank=True, null=True)
    powerpoint_link = models.URLField(blank=True, null=True)

    pdf_file = models.FileField(upload_to='materials/pdf/', blank=True, null=True)
    pdf_link = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Project Material'
        verbose_name_plural = 'Project Materials'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Ensure only one active record exists at a time
        if self.is_active:
            ProjectMaterial.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def get_excel_url(self):
        if self.excel_file:
            return self.excel_file.url
        return self.excel_link or ''

    def get_powerpoint_url(self):
        if self.powerpoint_file:
            return self.powerpoint_file.url
        return self.powerpoint_link or ''

    def get_pdf_url(self):
        if self.pdf_file:
            return self.pdf_file.url
        return self.pdf_link or ''

