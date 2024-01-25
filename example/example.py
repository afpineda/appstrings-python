# ****************************************************************************
# @file example.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-22
# @brief Translation utility
# @copyright 2024. Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

from enum import Enum
from appstrings import *

class EN(Enum):
    _lang = "en"
    _domain = "appstrings.example"
    TEST = "Hello world!"

class ES_MX(Enum):
    _lang = "es_MX"
    _domain = "appstrings.example"
    TEST = "¡Hola mundo!"

install(EN)
install(ES_MX)

_ = gettext
STR = EN

set_translation_locale("es_MX")
print(f"Locale 'es_MX': {_(STR.TEST)}")

set_translation_locale("en_US")
print(f"Locale 'en_US': {_(STR.TEST)}")
