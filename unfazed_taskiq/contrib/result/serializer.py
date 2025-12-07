from unfazed.serializer import Serializer

from . import models as m


class UnfazedTaskiqResultSerializer(Serializer):
    class Meta:
        model = m.UnfazedTaskiqResult
