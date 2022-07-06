import re
from .field import Field
from ..exception import ValidationError
from ..warning import InvalidLabelWarning
from datetime import date, time, datetime


def validate_list_of_number(value, size_limit, item_type):
    if type(value) is not list:
        raise ValidationError(f"expect list of num, got {value}")
    if len(value) != size_limit:
        raise ValidationError(f"expect size of list is {size_limit}, got {len(value)}")
    try:
        return [item_type(item) for item in value]
    except (TypeError, ValueError) as _:
        raise ValidationError(f"expect type of list item is float, got {value}")


class CoordField(Field):
    def validate(self, value):
        return validate_list_of_number(value, 2, float)


class Coord3DField(Field):
    def validate(self, value):
        return validate_list_of_number(value, 3, float)


class IntervalField(Field):
    def validate(self, value):
        value = validate_list_of_number(value, 2, float)
        if value[0] > value[1]:
            raise ValidationError(
                f"expect |begin| less than or equal to |end|, got {value}"
            )
        return value


class BBoxField(Field):
    def validate(self, value):
        return validate_list_of_number(value, 4, float)


class PolygonField(Field):
    def validate(self, value):
        for idx, item in enumerate(value):
            value[idx] = validate_list_of_number(item, 2, float)
        return value


class LabelField(Field):
    def __init__(self, dom):
        super(LabelField, self).__init__()
        self.dom = dom

    def validate(self, value):
        try:
            if isinstance(value, int):
                category_name = self.dom(value).name
                return dict(name=category_name, id=value, dom=self.dom.__name__)
            elif isinstance(value, str):
                category_id = getattr(self.dom, self.clean(value)).value
                return dict(name=value, id=category_id, dom=self.dom.__name__)
            else:
                raise TypeError("invalid class label type.")
        except:
            InvalidLabelWarning(f"The label {value} is not valid.")
            return dict(name="invalid", id=-1, dom=self.dom.__name__)
    @staticmethod
    def clean(varStr):
        return re.sub('\W|^(?=\d)', '_', varStr).lower()



class DateField(Field):
    def __init__(self, fmt: str = ""):
        super(DateField, self).__init__()
        self.fmt = fmt

    def validate(self, value):
        if self.fmt == "":
            return date.fromisoformat(value)
        return datetime.strptime(value, self.fmt).date()


class TimeField(Field):
    def __init__(self, fmt: str = ""):
        super(TimeField, self).__init__()
        self.fmt = fmt

    def validate(self, value):
        if self.fmt == "":
            return time.fromisoformat(value)
        return datetime.strptime(value, self.fmt).time()
