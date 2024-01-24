# ****************************************************************************
# @file appstrings.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-22
# @brief Translation utility
# @copyright 2024. Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

"""
Minimal strings translation library for Python

This is not a full internationalization library,
nor suitable for usual translation workflows.
Make sure it meets your needs.

Functions:
    gettext(): Returns a translated string
    install(): Install an enumeration as a translator
    set_translation_locale(): Set a locale for translation
    get_translation_locale(): Get current locale used for translation


Exceptions:
    TranslatorException: for invalid language translators

"""

# *****************************************************************************
# Imports
# *****************************************************************************

from enum import Enum
from locale import getlocale, setlocale, LC_ALL

# *****************************************************************************
# "private" global variables
# *****************************************************************************

__translators = []
__current_translator = None
__first_call = True

# *****************************************************************************
# Classes
# *****************************************************************************


class TranslatorException(Exception):
    """Exception for invalid language translators"""

    pass


# *****************************************************************************
# "private" functions
# *****************************************************************************


def _decode_locale(locale: str) -> (str, str):
    l = len(locale)
    if l >= 2:
        lang = locale[0:2].lower()
        if l == 2:
            return (lang, "")
        if (l == 5) and (locale[2] == "_"):
            return (lang, locale[3:5].lower())
    raise TranslatorException(f"'{locale}' is not a valid locale string")


def _reset():
    global __current_locale
    global __translators
    global __current_translator
    global __first_call
    setlocale(LC_ALL, "")
    __current_locale = _decode_locale(getlocale()[0])
    __translators = []
    __current_translator = None
    __first_call = True


def _match_installed_translator(current_lang: str, current_country: str) -> Enum:
    result = None
    global __translators
    for translator in __translators:
        translator_locale = _decode_locale(translator._lang._value_)
        translator_lang = translator_locale[0]
        translator_country = translator_locale[1]
        if translator_lang == current_lang:
            if translator_country == current_country:
                result = translator
                break
            if (translator_country == "") or (not result):
                result = translator
    return result


def __initialize():
    global __first_call
    global __current_translator
    global __current_locale
    __first_call = False
    if not __current_locale:
        raise TranslatorException("Current locale is unknown")
    current_lang = __current_locale[0]
    current_country = __current_locale[1]
    __current_translator = _match_installed_translator(current_lang, current_country)


def __check_string_ids(cls1: Enum, cls2: Enum):
    if cls1 != cls2:
        for id in cls1:
            attr_name = id._name_
            if (attr_name[0] != "_") and (not hasattr(cls2, attr_name)):
                raise TranslatorException(
                    f"String ID '{attr_name}' from '{cls1.__name__} is missing at '{cls2.__name__}'"
                )
        for id in cls2:
            attr_name = id._name_
            if (attr_name[0] != "_") and (not hasattr(cls1, attr_name)):
                raise TranslatorException(
                    f"String ID '{attr_name}' from '{cls2.__name__} is missing at '{cls1.__name__}'"
                )


# *****************************************************************************
# "public" functions
# *****************************************************************************


def gettext(id) -> str:
    """Return a translated string

    The best-matching translator for the selected locale is used.

    Args:
        id (Enumeration attribute): Identifier of the string to translate

    Returns:
        str: Translated string
    """
    global __current_translator
    global __first_call
    if __first_call:
        __initialize()
    if __current_translator:
        return getattr(__current_translator, id._name_)._value_
    else:
        return id._value_


def install(translator: Enum):
    """Install an enumeration as a translator

    Args:
        translator (Enum): An enumeration to work as a translator.
                           Must define a "_lang" attribute containing
                           a locale string or language string. For example:
                           "en" or "en_US"

    Raises:
        TranslatorException: The given translator is not valid
    """
    global __translators
    global __first_call
    __first_call = True
    if not hasattr(translator, "_lang"):
        raise TranslatorException(
            f"{translator.__name__} is missing the '_lang' attribute"
        )
    _decode_locale(translator._lang._value_)
    if translator not in __translators:
        if len(__translators) > 0:
            __check_string_ids(translator, __translators[0])
        __translators.append(translator)


def set_translation_locale(locale_str: str = None):
    """Set a locale for translation

    Args:
        locale_str (str): A locale string. For example, "en_US".
                          If not given, system locale is used.

    Remarks:
        Not mandatory. If not called, current system locale is used.
    """
    global __current_locale
    __current_locale = _decode_locale(locale_str if locale_str else getlocale()[0])


def get_translation_locale() -> str:
    """Get current locale used for translation

    Returns:
        str: Locale string
    """
    if __current_locale:
        result = __current_locale[0]
        locale_country = __current_locale[1]
        if locale_country != "":
            result += "_"
            result += locale_country.upper()
    else:
        result = ""
    return result


def get_installed_translators() -> list:
    """Retrieve a list of all installed translators"""
    global __translators
    return __translators.copy()


# *****************************************************************************
# Initialization
# *****************************************************************************

_reset()

# *****************************************************************************
# Automated Test
# *****************************************************************************

if __name__ == "__main__":
    print("----------------------------------")
    print("Automated test")
    print("----------------------------------")
    system_locale = getlocale()[0]
    print(f"Current language: {system_locale}")

    class EN(Enum):
        _lang = "en"
        _desc = "for testing purposes"
        TEST = "English"

    class ES(Enum):
        _lang = "es"
        TEST = "Spanish"

    class ES_MX(Enum):
        _lang = "es_MX"
        TEST = "Spanish_Mexico"

    class Error1(Enum):
        TEST = "Not valid"

    class Error2(Enum):
        _lang = "pt"

    class Error3(Enum):
        _lang = "pt_"

    print("Testing custom translation locale")
    set_translation_locale("ch")
    if get_translation_locale() != "ch":
        print("Failure: 'ch' not set")
    set_translation_locale()
    if get_translation_locale() != system_locale:
        print("Failure: system locale not set")
    print("Done")

    print("Testing invalid translator installation")
    _reset()
    try:
        install(Error1)
        print("Failure: Class Error1 should not install")
    except:
        pass

    _reset()
    try:
        install(EN)
        install(Error2)
        print("Failure: Class Error2 should not install")
    except:
        pass

    _reset()
    try:
        install(Error3)
        print("Failure: Class Error3 should not install")
    except:
        pass

    print("Done")

    print("Testing no default translator")
    _reset()

    try:
        t = gettext(EN.TEST)
        if t != EN.TEST._value_:
            print("Failure at EN.TEST")
        t = gettext(ES.TEST)
        if t != ES.TEST._value_:
            print("Failure at ES.TEST")
    except:
        print("Failure due to exception")
    print("Done")

    print("Testing current language")
    _reset()
    set_translation_locale("en")
    l = get_translation_locale()
    if l != "en":
        print("Failure: 'en' was not set as current language")

    set_translation_locale("en_US")
    l = get_translation_locale()
    if l != "en_US":
        print("Failure: 'en_US' was not set as current locale")

    set_translation_locale("PT")
    l = get_translation_locale()
    if l != "pt":
        print("Failure: 'PT' was not set as current language")
    print("Done")

    print("Test translation #1")
    _reset()
    set_translation_locale("en")
    install(ES)
    install(EN)
    t = gettext(ES.TEST)
    if t != EN.TEST._value_:
        print("Failure")
    print("Done")

    print("Test translation #2")
    _reset()
    set_translation_locale("pt")
    install(ES)
    install(EN)
    t = gettext(EN.TEST)
    if t != EN.TEST._value_:
        print("Failure")
    print("Done")

    print("Test translation #3")
    _reset()
    set_translation_locale("es_MX")
    install(ES)
    install(EN)
    t = gettext(ES.TEST)
    if t != ES.TEST._value_:
        print("Failure")
    print("Done")

    print("Test translation #4")
    _reset()
    set_translation_locale("es_MX")
    install(ES)
    install(ES_MX)
    t = gettext(ES.TEST)
    if t != ES_MX.TEST._value_:
        print("Failure")
    print("Done")

    print("Testing enumeration of installed translators")
    _reset()
    install(ES)
    install(ES_MX)
    l = get_installed_translators()
    if len(l) != 2:
        print("Failure.")
    print(" Printing for eye-review")
    for t in l:
        print(f"  {t._lang._value_}")
    print("Done")
    print("----------------------------------")
