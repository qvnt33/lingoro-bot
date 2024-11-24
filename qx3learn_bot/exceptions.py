class UserNotFoundError(Exception):
    """Виняток, якщо користувача не знайдено у БД"""

    pass


class InvalidVocabIndexError(Exception):
    """Виняток, якщо у БД немає словника з заданим ID"""

    pass
