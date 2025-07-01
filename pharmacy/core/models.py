from django.db import models


class MarkingImport(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=255)
    markings_count = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "markings_count": self.markings_count,
            "uploaded_at": self.uploaded_at,
        }


class Marking(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.IntegerField()
    date = models.DateField()
    hour = models.TimeField()

    marking_import = models.ForeignKey(MarkingImport, on_delete=models.CASCADE)

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "date": self.date,
            "hour": self.hour,
            "marking_import": self.marking_import.to_dict(),
        }
