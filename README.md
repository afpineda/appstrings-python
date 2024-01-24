# Minimal string translation library for Python

In summary:

- Developers reference translatable strings using identifiers in an enumeration class.
- Language-specific strings are written in several enumeration classes.
- The library transparently transforms string identifiers into already translated strings,
  depending on the system locale or user-selected locale.

This is neither a full internationalization library nor suitable for usual translation workflows.
Make sure it meets your needs.
If not, there are other libraries that do the job, for example,
[gettext](https://docs.python.org/3/library/gettext.html).

## How to use

### Translate text for each locale

Define all translatable strings in an enumeration class.
You **must** also define a `_lang` attribute and set its value
to the corresponding locale or language string.
A list of valid locale strings can be found at
[saimana.com](https://saimana.com/list-of-country-locale-code/).

For example:

```python
from enum import Enum

class EN(Enum):
    _lang = "en"
    TEST = "Hello world!"

class ES_MX(Enum):
    _lang = "es_MX"
    TEST = "¡Hola mundo!"
```

Those enumerations are called **translators** in the context of this library.
In order to use them, you must "install" all of them at initialization:

```python
from appstrings import install

install(EN)
install(ES_MX)
```

The library will check that all installed translators enumerate the same set of constants,
except for "sunder" and "dunder" ones.
Use that notation for non-translatable attributes if you need to. For example:

```python
class ES_MX(Enum):
    _lang = "es_MX"
    _note = "this is a developer note, not to be translated"
    TEST = "¡Hola mundo!"
```

### Use already translated text

The function `gettext()` is used for translation. For example:

```python
from appstrings import gettext

print(gettext(EN.TEST))
```

You may want to alias `gettext` to `_` for convenience:

```python
_ = gettext

print(_(EN.TEST)) # Print translated string, depending on current locale
```

This way, you may disable translation at any time for development purposes:

```python
# _ = gettext

_ = lambda id: id._value_

print(_(EN.TEST)) # Always print all strings in english, for now
```

The library chooses the best-matching translator for the current translation locale, which is initialized from `locale.getlocale()`.
You may force a specific locale for translation at any time:

```python
from appstrings import set_translation_locale

set_translation_locale("es_MX")
print(_(EN.TEST)) # Prints text in spanish language of Mexico
```

then force the system locale again:

```python
set_translation_locale()
```

Note that `set_translation_locale()` is mostly for testing purposes.
Forcing a specific locale not available in your application will not *magically* translate your strings to that locale.

### Fallback to a default language

In the previous examples, there is no translator for the locale *pt_BR*, to say one.
In such a case, the translator used in `gettext()` will work as the **default language** for non-translated locales.
In the early example, brazilian people would read the text in english.
However, if `print(_(ES_MX.TEST))` were used instead, brazilian people would read the text in spanish.

The ability to change the default language at any time comes from aliases:

```python
STR = EN

print(_(STR.TEST)) # Prints TEST string in english if there is no matching translator

STR = ES_MX

print(_(STR.TEST)) # Prints TEST string in spanish if there is no matching translator
```

This approach is developer-friendly, but not user-friendly.
Your application should allow the user to choose another default language
via command-line parameters, environment variables or other means.

The function `get_installed_translators()` will help in order to show a list of
available languages.

### Organize your code

You may spread your translators along many source files as long as your application imports and installs them.

For example:

```mermaid
flowchart TB
    main["__main__.py (your application)"]
    default["translation.py (defines default language)"]
    lang_es["translation_es.py (defines spanish translator)"]
    lang_pt["translation_pt.py (defines portuguese translator)"]

    main --imports--> default
    default --imports--> lang_es
    default --imports--> lang_pt
```

But the following schema will work just the same:

```mermaid
flowchart TB
    main["__main__.py (your application)"]
    default["translation.py (defines default language)"]
    lang_es["translation_es.py (defines spanish translator)"]
    lang_pt["translation_pt.py (defines portuguese translator)"]

    main --imports--> default
    main --imports--> lang_es
    main --imports--> lang_pt
```

The "translation*.py" files would look like this:

```python
from enum import Enum
from appstrings import install

class CertainTranslator(Enum):
    _lang = ...
    TEXT1 = ...
    TEXT2 = ...
    ...

install(CertainTranslator)
```

That is all about this library. As simple as that.
