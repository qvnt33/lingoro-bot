import re


def escape_markdown(text: str) -> str:
    """Екранує спеціальні символи Markdown у тексті, щоб вони не впливали на форматування"""
    # Регулярний вираз знаходить усі спеціальні символи Markdown і перед ними додає символ екранування `\`
    special_characters = r'([_*[\]()~`>#+-=|{}.!])'  # Спеціальні символи
    # Екранування кожного символу, додаючи перед ним символ "\""
    escaped_text: str = re.sub(special_characters, r'\\\1', text)
    return escaped_text
