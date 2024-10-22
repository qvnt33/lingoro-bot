from aiogram.fsm.state import State, StatesGroup


class VocabCreation(StatesGroup):
    waiting_for_vocab_name = State()  # Стан очікування назви словника
    waiting_for_vocab_note = State()  # Стан очікування примітки до словника
    waiting_for_wordpairs = State()  # Стан очікування словникових пар


class VocabTraining(StatesGroup):
    waiting_for_translation = State()  # Стан очікування перекладу
