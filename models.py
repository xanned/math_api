from tortoise import models, fields


class Task(models.Model):
    id = fields.CharField(max_length=50, pk=True)
    status = fields.CharField(max_length=50, null=True)
    result = fields.FloatField(null=True)
    started_at = fields.DatetimeField(auto_now_add=True)
    finished_at = fields.DatetimeField(null=True)
