import re
from typing import Any, Dict, List, Text, Union


def ignore_case_in_regex(regex: Text) -> Text:
    return f"(?i){regex}"


def search_regex_in_deep(
    regex: Text, 
    obj: Union[Text, Dict[Text, Any], List[Text], List[Dict[Text, Any]]], 
    flags: Union[int, re.RegexFlag] = 0) -> bool:
    did_match: bool = False

    if isinstance(obj, dict):
        for value in obj.values():
            did_match = did_match or search_regex_in_deep(regex, value, flags)
            if did_match:
                return did_match
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) \
                or isinstance(item, str) \
                or (isinstance(item, list) and len(item) > 0 and isinstance(item[0], dict)) \
                or (isinstance(item, list) and len(item) > 0 and isinstance(item[0], str)):
                did_match = did_match or search_regex_in_deep(regex, item, flags)
                if did_match:
                    return did_match
    elif isinstance(obj, str):
        did_match = did_match or bool(re.search(regex, obj, flags))
        if did_match:
            return did_match

    return did_match
