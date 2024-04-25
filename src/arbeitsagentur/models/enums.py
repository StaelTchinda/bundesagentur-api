from enum import Enum


class ParamEnum(Enum):
    def __init__(self, value, param_value):
        self._value_ = value
        self._param_value_ = param_value

    @classmethod
    def __flex_init__(cls, value_or_param_value, param_value = None) -> 'ParamEnum':
        _value_ = None
        _param_value_ = None
        if param_value is not None:
            _value_ = value_or_param_value
            _param_value_ = param_value
        else:
            for enum_entity in cls:
                if enum_entity.value == value_or_param_value \
                        or enum_entity.param_value == value_or_param_value:
                    _value_ = enum_entity.value
                    _param_value_ = enum_entity.param_value
        if _value_ is None or _param_value_ is None:
            raise ValueError(f"Invalid parameters for class {cls.__name__}: {value_or_param_value}, {param_value}")
        
        enum_value = cls(_value_, _param_value_)
        return enum_value

    @classmethod
    def _missing_(cls, value):
        return cls.__flex_init__(value)     

    @property
    def value(self):
        return self._value_

    @property
    def name(self):
        return self._name_

    @property
    def param_value(self):
        return self._param_value_

    @param_value.setter
    def param_value(self, param_value):
        self._param_value_ = param_value


class EducationType(ParamEnum):
    au = "Ausbildung", "1"
    dsa = "Duales Studium (ausbildungsintegrierend)", "2"
    dsp = "Duales Studium (praxisintegrierend)", "3"




class LocationRadius(ParamEnum):
    zero = "ganzer Ort", 0
    ten = "10 km", 10
    fifteen = "15 km", 15
    twenty = "20 km", 20
    fifty = "50 km", 50
    hundred = "100 km", 100
    two_hundred = "200 km", 200


class OfferType(ParamEnum):
    ar = "Arbeitskräfte", 1
    au = "Auszubildende/Duales Studium", 2
    pt = "Praktikanten/Trainees", 3
    se = "Selbstständige", 4


class WorkingTime(ParamEnum):
    vz = "Vollzeit", "VOLLZEIT"
    tz = "Teilzeit", "TEILZEIT"
    snw = "Schicht,Nacht,Wochenende", "SCHICHT_NACHTARBEIT_WOCHENENDE"
    ht = "Heim-/Telearbeit", "HEIM_TELEARBEIT"
    mj = "Minijob", "MINIJOB"


class WorkExperience(ParamEnum):
    be = "Berufseinsteiger*innen", 1
    mb = "Mit Berufserfahrung", 2


class ContractType(ParamEnum):
    be = "Befristet", 0
    ub = "Unbefristet", 1


class Disability(ParamEnum):
    an = "Nur Schwerbehinderte oder ihnen gleichgestellte Bewerber*innen anzeigen", 1
    all = "Alle Bewerber*innen anzeigen", 2 


class JobType(ParamEnum):
    ARBEIT = "Arbeit", "ARBEIT"
    # TODO: Add other job types

