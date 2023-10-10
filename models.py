from tortoise import models, fields


class TaskDb(models.Model):
    id = fields.IntField(pk=True, )
    uuid = fields.UUIDField()
    status = fields.CharField(max_length=15, null=True)
    result = fields.FloatField(null=True)
    started_at = fields.DatetimeField(auto_now_add=True)
    finished_at = fields.DatetimeField(null=True)
