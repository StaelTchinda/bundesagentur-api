from enum import Enum
from typing import Any, Callable


class ParamEnum(Enum):
    def __init__(self, value, param_value):
        self._value_ = value
        self._param_value_ = param_value

    @classmethod
    def __flex_init__(cls, value_or_param_value, param_value=None) -> "ParamEnum":
        compare_nullable: Callable[[Any, Any], bool] = lambda a, b: a == b or (
            a is None and b is None
        )

        _value_ = None
        _param_value_ = None
        if param_value is not None:
            _value_ = value_or_param_value
            _param_value_ = param_value
        else:
            for enum_entity in cls:
                if compare_nullable(
                    enum_entity.value, value_or_param_value
                ) or compare_nullable(enum_entity.param_value, value_or_param_value):
                    _value_ = enum_entity.value
                    _param_value_ = enum_entity.param_value

        try:
            enum_value = cls(_value_, _param_value_)
        except Exception as e:
            raise ValueError(
                f"Could not instantiate enum {cls.__name__} with parameters ({value_or_param_value}, {param_value}): {e}"
            )

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
    TRAINING = "Ausbildung", "1"
    DUAL_STUDY_INTEGRATED = "Duales Studium (ausbildungsintegrierend)", "2"
    DUAL_STUDY_PRACTICE_INTEGRATED = "Duales Studium (praxisintegrierend)", "3"
    UNDEFINED = "", None


class LocationRadius(ParamEnum):
    ZERO = "ganzer Ort", 0
    TEN = "10 km", 10
    FIFTEEN = "15 km", 15
    TWENTY = "20 km", 20
    FIFTY = "50 km", 50
    HUNDRED = "100 km", 100
    TWO_HUNDRED = "200 km", 200
    UNDEFINED = "", None


class OfferType(ParamEnum):
    WORKER = "Arbeitskräfte", 1
    TRAINEE = "Auszubildende/Duales Studium", 2
    INTERN = "Praktikanten/Trainees", 3
    SELF_EMPLOYED = "Selbstständige", 4
    UNDEFINED = "", None


class InputWorkingTime(ParamEnum):
    FULL_TIME = "Vollzeit", "vz"
    PART_TIME = "Teilzeit", "tz"
    SHIFT_NIGHT_WEEKEND = "Schicht,Nacht,Wochenende", "snw"
    HOME_TELEWORK = "Heim-/Telearbeit", "ho"
    MINI_JOB = "Minijob", "mj"
    UNDEFINED = "", None


class WorkingTime(ParamEnum):
    FULL_TIME = "Vollzeit", "VOLLZEIT"
    PART_TIME = "Teilzeit", "TEILZEIT"
    SHIFT_NIGHT_WEEKEND = "Schicht,Nacht,Wochenende", "SCHICHT_NACHTARBEIT_WOCHENENDE"
    HOME_TELEWORK = "Heim-/Telearbeit", "HEIM_TELEARBEIT"
    MINI_JOB = "Minijob", "MINIJOB"
    UNDEFINED = "", None


class WorkExperience(ParamEnum):
    YOUNG_PROFESSIONAL = "Berufseinsteiger*innen", 1
    WITH_EXPERIENCE = "Mit Berufserfahrung", 2
    UNDEFINED = "", None


class ContractType(ParamEnum):
    LIMITED = "Befristet", 0
    UNLIMITED = "Unbefristet", 1
    UNDEFINED = "", None


class Disability(ParamEnum):
    ONLY_SEVERELY_DISABLED = (
        "Nur Schwerbehinderte oder ihnen gleichgestellte Bewerber*innen anzeigen",
        1,
    )
    ALL = "Alle Bewerber*innen anzeigen", 2
    UNDEFINED = "", None


class JobType(ParamEnum):
    ARBEIT = "Arbeit", "ARBEIT"
    UNDEFINED = "", None
    # TODO: Add other job types
