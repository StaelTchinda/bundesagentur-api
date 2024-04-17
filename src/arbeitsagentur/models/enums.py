from enum import Enum


class EducationType(Enum):
    au="Ausbildung"
    dsa="Duales Studium (ausbildungsintegrierend)"
    dsp="Duales Studium (praxisintegrierend)"


class LocationRadius(Enum):
    zero="0"
    ten="10"
    fifteen="15"
    twenty="20"
    fifty="50"
    hundred="100"
    two_hundred="200"

    def pretty_print(self):
        if self == LocationRadius.zero:
            return "ganzer Ort"
        else:
            return self.value + " km"


class OfferType(Enum):
    ar="Arbeitskräfte"
    au="Auszubildende/Duales Studium"
    pt="Praktikanten/Trainees"
    se="Selbstständige"
    
class WorkingTime(Enum):
    vz="VOLLZEIT"
    tz="TEILZEIT"
    snw="SCHICHT_NACHTARBEIT_WOCHENENDE"
    ht="HEIM_TELEARBEIT"
    mj="MINIJOB"

    def __str__(self):
        if self == WorkingTime.vz:
            return "Vollzeit"
        elif self == WorkingTime.tz:
            return "Teilzeit"
        elif self == WorkingTime.snw:
            return "Schicht,Nacht,Wochenende"
        elif self == WorkingTime.ht:
            return "Heim-/Telearbeit"
        elif self == WorkingTime.mj:
            return "Minijob"
        else:
            raise ValueError(f"Unknown WorkingTime: {self}")


class WorkExperience(Enum):
    be="Berufseinsteiger*innen"
    mb="Mit Berufserfahrung"


class ContractType(Enum):
    be="Befristet"
    ub="Unbefristet"


class Disability(Enum):
    an="Nur Schwerbehinderte oder ihnen gleichgestellte Bewerber*innen anzeigen"
    all="Alle Bewerber*innen anzeigen"

