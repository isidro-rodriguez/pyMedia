"""Datos estáticos de lenguas según ISO 639-1 e ISO 639-2."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True, kw_only=True)
class Language:
    """Metadatos de una lengua según los estándares ISO 639-1 e ISO 639-2.

    Attributes:
        iso_639_1_code: Código ISO 639-1 de 2 letras, o `None` si la lengua
            no dispone de uno.
        iso_639_2_code: Código ISO 639-2 de 3 letras (variante bibliográfica).
            Es la clave de LANGUAGES y coincide con lo que reporta ffprobe
            en los tags de idioma de pistas de audio/subtítulos.
        native: Nombre de la lengua en su propio idioma.
        english: Nombre de la lengua en inglés.
    """

    iso_639_1_code: str | None
    iso_639_2_code: str
    native: str
    english: str


_LANGUAGES: tuple[Language, ...] = (
    Language(
        iso_639_1_code="aa",
        iso_639_2_code="aar",
        native="Afaraf",
        english="Afar",
    ),
    Language(
        iso_639_1_code="ab",
        iso_639_2_code="abk",
        native="Аҧсуа бызшәа",
        english="Abkhazian",
    ),
    Language(
        iso_639_1_code="af",
        iso_639_2_code="afr",
        native="Afrikaans",
        english="Afrikaans",
    ),
    Language(
        iso_639_1_code="ak",
        iso_639_2_code="aka",
        native="Akan",
        english="Akan",
    ),
    Language(
        iso_639_1_code="sq",
        iso_639_2_code="alb",
        native="Shqip",
        english="Albanian",
    ),
    Language(
        iso_639_1_code="am",
        iso_639_2_code="amh",
        native="አማርኛ",
        english="Amharic",
    ),
    Language(
        iso_639_1_code="ar",
        iso_639_2_code="ara",
        native="العربية",
        english="Arabic",
    ),
    Language(
        iso_639_1_code="an",
        iso_639_2_code="arg",
        native="Aragonés",
        english="Aragonese",
    ),
    Language(
        iso_639_1_code="hy",
        iso_639_2_code="arm",
        native="Հայերեն",
        english="Armenian",
    ),
    Language(
        iso_639_1_code="as",
        iso_639_2_code="asm",
        native="অসমীয়া",
        english="Assamese",
    ),
    Language(
        iso_639_1_code="av",
        iso_639_2_code="ava",
        native="Авар мацӀ",
        english="Avaric",
    ),
    Language(
        iso_639_1_code="ae",
        iso_639_2_code="ave",
        native="Avesta",
        english="Avestan",
    ),
    Language(
        iso_639_1_code="ay",
        iso_639_2_code="aym",
        native="Aymar aru",
        english="Aymara",
    ),
    Language(
        iso_639_1_code="az",
        iso_639_2_code="aze",
        native="Azərbaycan dili",
        english="Azerbaijani",
    ),
    Language(
        iso_639_1_code="ba",
        iso_639_2_code="bak",
        native="Башҡорт теле",
        english="Bashkir",
    ),
    Language(
        iso_639_1_code="bm",
        iso_639_2_code="bam",
        native="Bamanankan",
        english="Bambara",
    ),
    Language(
        iso_639_1_code="eu",
        iso_639_2_code="baq",
        native="Euskara",
        english="Basque",
    ),
    Language(
        iso_639_1_code="be",
        iso_639_2_code="bel",
        native="Беларуская",
        english="Belarusian",
    ),
    Language(
        iso_639_1_code="bn",
        iso_639_2_code="ben",
        native="বাংলা",
        english="Bengali",
    ),
    Language(
        iso_639_1_code="bi",
        iso_639_2_code="bis",
        native="Bislama",
        english="Bislama",
    ),
    Language(
        iso_639_1_code="bs",
        iso_639_2_code="bos",
        native="Bosanski",
        english="Bosnian",
    ),
    Language(
        iso_639_1_code="br",
        iso_639_2_code="bre",
        native="Brezhoneg",
        english="Breton",
    ),
    Language(
        iso_639_1_code="bg",
        iso_639_2_code="bul",
        native="Български",
        english="Bulgarian",
    ),
    Language(
        iso_639_1_code="my",
        iso_639_2_code="bur",
        native="မြန်မာဘာသာ",
        english="Burmese",
    ),
    Language(
        iso_639_1_code="ca",
        iso_639_2_code="cat",
        native="Català",
        english="Catalan",
    ),
    Language(
        iso_639_1_code="ch",
        iso_639_2_code="cha",
        native="Chamoru",
        english="Chamorro",
    ),
    Language(
        iso_639_1_code="ce",
        iso_639_2_code="che",
        native="Нохчийн мотт",
        english="Chechen",
    ),
    Language(
        iso_639_1_code="zh",
        iso_639_2_code="chi",
        native="中文",
        english="Chinese",
    ),
    Language(
        iso_639_1_code="cv",
        iso_639_2_code="chv",
        native="Чӑваш чӗлхи",
        english="Chuvash",
    ),
    Language(
        iso_639_1_code="kw",
        iso_639_2_code="cor",
        native="Kernewek",
        english="Cornish",
    ),
    Language(
        iso_639_1_code="co",
        iso_639_2_code="cos",
        native="Corsu",
        english="Corsican",
    ),
    Language(
        iso_639_1_code="cr",
        iso_639_2_code="cre",
        native="ᓀᐦᐃᔭᐍᐏᐣ",
        english="Cree",
    ),
    Language(
        iso_639_1_code="cs",
        iso_639_2_code="cze",
        native="Čeština",
        english="Czech",
    ),
    Language(
        iso_639_1_code="da",
        iso_639_2_code="dan",
        native="Dansk",
        english="Danish",
    ),
    Language(
        iso_639_1_code="dv",
        iso_639_2_code="div",
        native="ދިވެހި",
        english="Divehi",
    ),
    Language(
        iso_639_1_code="nl",
        iso_639_2_code="dut",
        native="Nederlands",
        english="Dutch",
    ),
    Language(
        iso_639_1_code="dz",
        iso_639_2_code="dzo",
        native="རྫོང་ཁ",
        english="Dzongkha",
    ),
    Language(
        iso_639_1_code="en",
        iso_639_2_code="eng",
        native="English",
        english="English",
    ),
    Language(
        iso_639_1_code="eo",
        iso_639_2_code="epo",
        native="Esperanto",
        english="Esperanto",
    ),
    Language(
        iso_639_1_code="et",
        iso_639_2_code="est",
        native="Eesti",
        english="Estonian",
    ),
    Language(
        iso_639_1_code="ee",
        iso_639_2_code="ewe",
        native="Eʋegbe",
        english="Ewe",
    ),
    Language(
        iso_639_1_code="fo",
        iso_639_2_code="fao",
        native="Føroyskt",
        english="Faroese",
    ),
    Language(
        iso_639_1_code="fj",
        iso_639_2_code="fij",
        native="Vosa Vakaviti",
        english="Fijian",
    ),
    Language(
        iso_639_1_code="fi",
        iso_639_2_code="fin",
        native="Suomi",
        english="Finnish",
    ),
    Language(
        iso_639_1_code="fr",
        iso_639_2_code="fre",
        native="Français",
        english="French",
    ),
    Language(
        iso_639_1_code="fy",
        iso_639_2_code="fry",
        native="Frysk",
        english="Western Frisian",
    ),
    Language(
        iso_639_1_code="ff",
        iso_639_2_code="ful",
        native="Fulfulde",
        english="Fulah",
    ),
    Language(
        iso_639_1_code="ka",
        iso_639_2_code="geo",
        native="ქართული",
        english="Georgian",
    ),
    Language(
        iso_639_1_code="de",
        iso_639_2_code="ger",
        native="Deutsch",
        english="German",
    ),
    Language(
        iso_639_1_code="gd",
        iso_639_2_code="gla",
        native="Gàidhlig",
        english="Scottish Gaelic",
    ),
    Language(
        iso_639_1_code="ga",
        iso_639_2_code="gle",
        native="Gaeilge",
        english="Irish",
    ),
    Language(
        iso_639_1_code="gl",
        iso_639_2_code="glg",
        native="Galego",
        english="Galician",
    ),
    Language(
        iso_639_1_code="gv",
        iso_639_2_code="glv",
        native="Gaelg",
        english="Manx",
    ),
    Language(
        iso_639_1_code="el",
        iso_639_2_code="gre",
        native="Ελληνικά",
        english="Greek",
    ),
    Language(
        iso_639_1_code="gn",
        iso_639_2_code="grn",
        native="Avañe'ẽ",
        english="Guarani",
    ),
    Language(
        iso_639_1_code="gu",
        iso_639_2_code="guj",
        native="ગુજરાતી",
        english="Gujarati",
    ),
    Language(
        iso_639_1_code="ht",
        iso_639_2_code="hat",
        native="Kreyòl ayisyen",
        english="Haitian",
    ),
    Language(
        iso_639_1_code="ha",
        iso_639_2_code="hau",
        native="Hausa",
        english="Hausa",
    ),
    Language(
        iso_639_1_code="he",
        iso_639_2_code="heb",
        native="עברית",
        english="Hebrew",
    ),
    Language(
        iso_639_1_code="hz",
        iso_639_2_code="her",
        native="Otjiherero",
        english="Herero",
    ),
    Language(
        iso_639_1_code="hi",
        iso_639_2_code="hin",
        native="हिन्दी",
        english="Hindi",
    ),
    Language(
        iso_639_1_code="ho",
        iso_639_2_code="hmo",
        native="Hiri Motu",
        english="Hiri Motu",
    ),
    Language(
        iso_639_1_code="hr",
        iso_639_2_code="hrv",
        native="Hrvatski",
        english="Croatian",
    ),
    Language(
        iso_639_1_code="hu",
        iso_639_2_code="hun",
        native="Magyar",
        english="Hungarian",
    ),
    Language(
        iso_639_1_code="ig",
        iso_639_2_code="ibo",
        native="Asụsụ Igbo",
        english="Igbo",
    ),
    Language(
        iso_639_1_code="is",
        iso_639_2_code="ice",
        native="Íslenska",
        english="Icelandic",
    ),
    Language(
        iso_639_1_code="io",
        iso_639_2_code="ido",
        native="Ido",
        english="Ido",
    ),
    Language(
        iso_639_1_code="ii",
        iso_639_2_code="iii",
        native="ꆈꌠ꒿ Nuosuhxop",
        english="Sichuan Yi",
    ),
    Language(
        iso_639_1_code="iu",
        iso_639_2_code="iku",
        native="ᐃᓄᒃᑎᑐᑦ",
        english="Inuktitut",
    ),
    Language(
        iso_639_1_code="ie",
        iso_639_2_code="ile",
        native="Interlingue",
        english="Interlingue",
    ),
    Language(
        iso_639_1_code="id",
        iso_639_2_code="ind",
        native="Bahasa Indonesia",
        english="Indonesian",
    ),
    Language(
        iso_639_1_code="ik",
        iso_639_2_code="ipk",
        native="Iñupiaq",
        english="Inupiaq",
    ),
    Language(
        iso_639_1_code="it",
        iso_639_2_code="ita",
        native="Italiano",
        english="Italian",
    ),
    Language(
        iso_639_1_code="jv",
        iso_639_2_code="jav",
        native="Basa Jawa",
        english="Javanese",
    ),
    Language(
        iso_639_1_code="ja",
        iso_639_2_code="jpn",
        native="日本語",
        english="Japanese",
    ),
    Language(
        iso_639_1_code="kl",
        iso_639_2_code="kal",
        native="Kalaallisut",
        english="Kalaallisut",
    ),
    Language(
        iso_639_1_code="kn",
        iso_639_2_code="kan",
        native="ಕನ್ನಡ",
        english="Kannada",
    ),
    Language(
        iso_639_1_code="ks",
        iso_639_2_code="kas",
        native="كٲشُر",
        english="Kashmiri",
    ),
    Language(
        iso_639_1_code="kr",
        iso_639_2_code="kau",
        native="Kanuri",
        english="Kanuri",
    ),
    Language(
        iso_639_1_code="kk",
        iso_639_2_code="kaz",
        native="Қазақ тілі",
        english="Kazakh",
    ),
    Language(
        iso_639_1_code="km",
        iso_639_2_code="khm",
        native="ខ្មែរ",
        english="Khmer",
    ),
    Language(
        iso_639_1_code="ki",
        iso_639_2_code="kik",
        native="Gĩkũyũ",
        english="Kikuyu",
    ),
    Language(
        iso_639_1_code="rw",
        iso_639_2_code="kin",
        native="Ikinyarwanda",
        english="Kinyarwanda",
    ),
    Language(
        iso_639_1_code="ky",
        iso_639_2_code="kir",
        native="Кыргызча",
        english="Kirghiz",
    ),
    Language(
        iso_639_1_code="kv",
        iso_639_2_code="kom",
        native="Коми кыв",
        english="Komi",
    ),
    Language(
        iso_639_1_code="kg",
        iso_639_2_code="kon",
        native="Kikongo",
        english="Kongo",
    ),
    Language(
        iso_639_1_code="ko",
        iso_639_2_code="kor",
        native="한국어",
        english="Korean",
    ),
    Language(
        iso_639_1_code="kj",
        iso_639_2_code="kua",
        native="Kuanyama",
        english="Kuanyama",
    ),
    Language(
        iso_639_1_code="ku",
        iso_639_2_code="kur",
        native="Kurdî",
        english="Kurdish",
    ),
    Language(
        iso_639_1_code="lo",
        iso_639_2_code="lao",
        native="ພາສາລາວ",
        english="Lao",
    ),
    Language(
        iso_639_1_code="la",
        iso_639_2_code="lat",
        native="Latina",
        english="Latin",
    ),
    Language(
        iso_639_1_code="lv",
        iso_639_2_code="lav",
        native="Latviešu",
        english="Latvian",
    ),
    Language(
        iso_639_1_code="li",
        iso_639_2_code="lim",
        native="Limburgs",
        english="Limburgan",
    ),
    Language(
        iso_639_1_code="ln",
        iso_639_2_code="lin",
        native="Lingála",
        english="Lingala",
    ),
    Language(
        iso_639_1_code="lt",
        iso_639_2_code="lit",
        native="Lietuvių",
        english="Lithuanian",
    ),
    Language(
        iso_639_1_code="lb",
        iso_639_2_code="ltz",
        native="Lëtzebuergesch",
        english="Luxembourgish",
    ),
    Language(
        iso_639_1_code="lu",
        iso_639_2_code="lub",
        native="Kiluba",
        english="Luba-Katanga",
    ),
    Language(
        iso_639_1_code="lg",
        iso_639_2_code="lug",
        native="Luganda",
        english="Ganda",
    ),
    Language(
        iso_639_1_code="mk",
        iso_639_2_code="mac",
        native="Македонски",
        english="Macedonian",
    ),
    Language(
        iso_639_1_code="mh",
        iso_639_2_code="mah",
        native="Kajin M̧ajeļ",
        english="Marshallese",
    ),
    Language(
        iso_639_1_code="ml",
        iso_639_2_code="mal",
        native="മലയാളം",
        english="Malayalam",
    ),
    Language(
        iso_639_1_code="mi",
        iso_639_2_code="mao",
        native="Māori",
        english="Maori",
    ),
    Language(
        iso_639_1_code="mr",
        iso_639_2_code="mar",
        native="मराठी",
        english="Marathi",
    ),
    Language(
        iso_639_1_code="ms",
        iso_639_2_code="may",
        native="Bahasa Melayu",
        english="Malay",
    ),
    Language(
        iso_639_1_code="mg",
        iso_639_2_code="mlg",
        native="Malagasy",
        english="Malagasy",
    ),
    Language(
        iso_639_1_code="mt",
        iso_639_2_code="mlt",
        native="Malti",
        english="Maltese",
    ),
    Language(
        iso_639_1_code="mn",
        iso_639_2_code="mon",
        native="Монгол хэл",
        english="Mongolian",
    ),
    Language(
        iso_639_1_code="na",
        iso_639_2_code="nau",
        native="Dorerin Naoero",
        english="Nauru",
    ),
    Language(
        iso_639_1_code="nv",
        iso_639_2_code="nav",
        native="Diné bizaad",
        english="Navajo",
    ),
    Language(
        iso_639_1_code="nr",
        iso_639_2_code="nbl",
        native="isiNdebele",
        english="South Ndebele",
    ),
    Language(
        iso_639_1_code="nd",
        iso_639_2_code="nde",
        native="isiNdebele",
        english="North Ndebele",
    ),
    Language(
        iso_639_1_code="ng",
        iso_639_2_code="ndo",
        native="Ndonga",
        english="Ndonga",
    ),
    Language(
        iso_639_1_code="ne",
        iso_639_2_code="nep",
        native="नेपाली",
        english="Nepali",
    ),
    Language(
        iso_639_1_code="nn",
        iso_639_2_code="nno",
        native="Norsk nynorsk",
        english="Norwegian Nynorsk",
    ),
    Language(
        iso_639_1_code="nb",
        iso_639_2_code="nob",
        native="Norsk bokmål",
        english="Norwegian Bokmål",
    ),
    Language(
        iso_639_1_code="no",
        iso_639_2_code="nor",
        native="Norsk",
        english="Norwegian",
    ),
    Language(
        iso_639_1_code="ny",
        iso_639_2_code="nya",
        native="Chi-Chewa",
        english="Chichewa",
    ),
    Language(
        iso_639_1_code="oc",
        iso_639_2_code="oci",
        native="Occitan",
        english="Occitan",
    ),
    Language(
        iso_639_1_code="oj",
        iso_639_2_code="oji",
        native="ᐊᓂᔑᓈᐯᒧᐎᓐ",
        english="Ojibwa",
    ),
    Language(
        iso_639_1_code="or",
        iso_639_2_code="ori",
        native="ଓଡ଼ିଆ",
        english="Oriya",
    ),
    Language(
        iso_639_1_code="om",
        iso_639_2_code="orm",
        native="Afaan Oromoo",
        english="Oromo",
    ),
    Language(
        iso_639_1_code="os",
        iso_639_2_code="oss",
        native="Ирон æвзаг",
        english="Ossetian",
    ),
    Language(
        iso_639_1_code="pa",
        iso_639_2_code="pan",
        native="ਪੰਜਾਬੀ",
        english="Panjabi",
    ),
    Language(
        iso_639_1_code="fa",
        iso_639_2_code="per",
        native="فارسی",
        english="Persian",
    ),
    Language(
        iso_639_1_code="pi",
        iso_639_2_code="pli",
        native="पाऴि",
        english="Pali",
    ),
    Language(
        iso_639_1_code="pl",
        iso_639_2_code="pol",
        native="Polski",
        english="Polish",
    ),
    Language(
        iso_639_1_code="pt",
        iso_639_2_code="por",
        native="Português",
        english="Portuguese",
    ),
    Language(
        iso_639_1_code="ps",
        iso_639_2_code="pus",
        native="پښتو",
        english="Pushto",
    ),
    Language(
        iso_639_1_code="qu",
        iso_639_2_code="que",
        native="Runa Simi",
        english="Quechua",
    ),
    Language(
        iso_639_1_code="rm",
        iso_639_2_code="roh",
        native="Rumantsch",
        english="Romansh",
    ),
    Language(
        iso_639_1_code="ro",
        iso_639_2_code="rum",
        native="Română",
        english="Romanian",
    ),
    Language(
        iso_639_1_code="rn",
        iso_639_2_code="run",
        native="Ikirundi",
        english="Rundi",
    ),
    Language(
        iso_639_1_code="ru",
        iso_639_2_code="rus",
        native="Русский",
        english="Russian",
    ),
    Language(
        iso_639_1_code="sg",
        iso_639_2_code="sag",
        native="Sängö",
        english="Sango",
    ),
    Language(
        iso_639_1_code="sa",
        iso_639_2_code="san",
        native="संस्कृतम्",
        english="Sanskrit",
    ),
    Language(
        iso_639_1_code="si",
        iso_639_2_code="sin",
        native="සිංහල",
        english="Sinhala",
    ),
    Language(
        iso_639_1_code="sk",
        iso_639_2_code="slo",
        native="Slovenčina",
        english="Slovak",
    ),
    Language(
        iso_639_1_code="sl",
        iso_639_2_code="slv",
        native="Slovenščina",
        english="Slovenian",
    ),
    Language(
        iso_639_1_code="se",
        iso_639_2_code="sme",
        native="Davvisámegiella",
        english="Northern Sami",
    ),
    Language(
        iso_639_1_code="sm",
        iso_639_2_code="smo",
        native="Gagana Samoa",
        english="Samoan",
    ),
    Language(
        iso_639_1_code="sn",
        iso_639_2_code="sna",
        native="ChiShona",
        english="Shona",
    ),
    Language(
        iso_639_1_code="sd",
        iso_639_2_code="snd",
        native="سنڌي",
        english="Sindhi",
    ),
    Language(
        iso_639_1_code="so",
        iso_639_2_code="som",
        native="Soomaaliga",
        english="Somali",
    ),
    Language(
        iso_639_1_code="st",
        iso_639_2_code="sot",
        native="Sesotho",
        english="Southern Sotho",
    ),
    Language(
        iso_639_1_code="es",
        iso_639_2_code="spa",
        native="Español",
        english="Spanish",
    ),
    Language(
        iso_639_1_code="sc",
        iso_639_2_code="srd",
        native="Sardu",
        english="Sardinian",
    ),
    Language(
        iso_639_1_code="sr",
        iso_639_2_code="srp",
        native="Српски",
        english="Serbian",
    ),
    Language(
        iso_639_1_code="ss",
        iso_639_2_code="ssw",
        native="SiSwati",
        english="Swati",
    ),
    Language(
        iso_639_1_code="su",
        iso_639_2_code="sun",
        native="Basa Sunda",
        english="Sundanese",
    ),
    Language(
        iso_639_1_code="sw",
        iso_639_2_code="swa",
        native="Kiswahili",
        english="Swahili",
    ),
    Language(
        iso_639_1_code="sv",
        iso_639_2_code="swe",
        native="Svenska",
        english="Swedish",
    ),
    Language(
        iso_639_1_code="ty",
        iso_639_2_code="tah",
        native="Reo Tahiti",
        english="Tahitian",
    ),
    Language(
        iso_639_1_code="ta",
        iso_639_2_code="tam",
        native="தமிழ்",
        english="Tamil",
    ),
    Language(
        iso_639_1_code="tt",
        iso_639_2_code="tat",
        native="Татар теле",
        english="Tatar",
    ),
    Language(
        iso_639_1_code="te",
        iso_639_2_code="tel",
        native="తెలుగు",
        english="Telugu",
    ),
    Language(
        iso_639_1_code="tg",
        iso_639_2_code="tgk",
        native="Тоҷикӣ",
        english="Tajik",
    ),
    Language(
        iso_639_1_code="tl",
        iso_639_2_code="tgl",
        native="Tagalog",
        english="Tagalog",
    ),
    Language(
        iso_639_1_code="th",
        iso_639_2_code="tha",
        native="ไทย",
        english="Thai",
    ),
    Language(
        iso_639_1_code="bo",
        iso_639_2_code="tib",
        native="བོད་སྐད",
        english="Tibetan",
    ),
    Language(
        iso_639_1_code="ti",
        iso_639_2_code="tir",
        native="ትግርኛ",
        english="Tigrinya",
    ),
    Language(
        iso_639_1_code="to",
        iso_639_2_code="ton",
        native="Faka Tonga",
        english="Tonga",
    ),
    Language(
        iso_639_1_code="tn",
        iso_639_2_code="tsn",
        native="Setswana",
        english="Tswana",
    ),
    Language(
        iso_639_1_code="ts",
        iso_639_2_code="tso",
        native="Xitsonga",
        english="Tsonga",
    ),
    Language(
        iso_639_1_code="tk",
        iso_639_2_code="tuk",
        native="Türkmençe",
        english="Turkmen",
    ),
    Language(
        iso_639_1_code="tr",
        iso_639_2_code="tur",
        native="Türkçe",
        english="Turkish",
    ),
    Language(
        iso_639_1_code="tw",
        iso_639_2_code="twi",
        native="Twi",
        english="Twi",
    ),
    Language(
        iso_639_1_code="ug",
        iso_639_2_code="uig",
        native="ئۇيغۇرچە",
        english="Uighur",
    ),
    Language(
        iso_639_1_code="uk",
        iso_639_2_code="ukr",
        native="Українська",
        english="Ukrainian",
    ),
    Language(
        iso_639_1_code="ur",
        iso_639_2_code="urd",
        native="اردو",
        english="Urdu",
    ),
    Language(
        iso_639_1_code="uz",
        iso_639_2_code="uzb",
        native="Oʻzbekcha",
        english="Uzbek",
    ),
    Language(
        iso_639_1_code="ve",
        iso_639_2_code="ven",
        native="Tshivenḓa",
        english="Venda",
    ),
    Language(
        iso_639_1_code="vi",
        iso_639_2_code="vie",
        native="Tiếng Việt",
        english="Vietnamese",
    ),
    Language(
        iso_639_1_code="vo",
        iso_639_2_code="vol",
        native="Volapük",
        english="Volapük",
    ),
    Language(
        iso_639_1_code="cy",
        iso_639_2_code="wel",
        native="Cymraeg",
        english="Welsh",
    ),
    Language(
        iso_639_1_code="wo",
        iso_639_2_code="wol",
        native="Wolof",
        english="Wolof",
    ),
    Language(
        iso_639_1_code="xh",
        iso_639_2_code="xho",
        native="isiXhosa",
        english="Xhosa",
    ),
    Language(
        iso_639_1_code="yi",
        iso_639_2_code="yid",
        native="ייִדיש",
        english="Yiddish",
    ),
    Language(
        iso_639_1_code="yo",
        iso_639_2_code="yor",
        native="Yorùbá",
        english="Yoruba",
    ),
    Language(
        iso_639_1_code="za",
        iso_639_2_code="zha",
        native="Vahcuengh",
        english="Zhuang",
    ),
    Language(
        iso_639_1_code="zu",
        iso_639_2_code="zul",
        native="isiZulu",
        english="Zulu",
    ),
)

TERMINOLOGICAL: dict[str, str] = {
    "sqi": "alb",
    "hye": "arm",
    "zho": "chi",
    "ces": "cze",
    "nld": "dut",
    "fra": "fre",
    "deu": "ger",
    "ell": "gre",
    "mkd": "mac",
    "mri": "mao",
    "msa": "may",
    "fas": "per",
    "ron": "rum",
    "slk": "slo",
    "bod": "tib",
    "cym": "wel",
}
"""Sinónimos terminológicos (T) aceptados como alias de la clave B."""


def resolve_language(raw: str) -> Language | None:
    """Resuelve una especificación de idioma a su `Language`.

    Acepta código ISO 639-1, código ISO 639-2 (variantes bibliográfica y
    terminológica), nombre en inglés o nombre nativo, sin distinción de
    mayúsculas ni espacios laterales.

    Args:
        raw: Especificación de idioma introducida por el usuario.

    Returns:
        El `Language` correspondiente, o `None` si no coincide con ninguno.
    """
    normalized = raw.strip().casefold()
    if not normalized:
        return None
    by_iso1 = {lang.iso_639_1_code: lang for lang in _LANGUAGES if lang.iso_639_1_code}
    if normalized in by_iso1:
        return by_iso1[normalized]
    by_iso2 = {lang.iso_639_2_code.casefold(): lang for lang in _LANGUAGES}
    if normalized in by_iso2:
        return by_iso2[normalized]
    target = TERMINOLOGICAL.get(normalized)
    if target is not None:
        return LANGUAGES.get(target)
    for lang in _LANGUAGES:
        if normalized == lang.english.casefold():
            return lang
    for lang in _LANGUAGES:
        if normalized == lang.native.casefold():
            return lang
    return None


LANGUAGES: Mapping[str, Language] = MappingProxyType(
    {lang.iso_639_2_code: lang for lang in _LANGUAGES}
)
"""dict[str, Language]: Lenguas indexadas por código ISO 639-2."""
