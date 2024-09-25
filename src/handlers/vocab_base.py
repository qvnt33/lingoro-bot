from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData  # Для створення callback data
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm.query import Query

from db.database import Session
from db.models import Vocabulary, User
from tools.read_data import app_data

router = Router(name='vocab_base')

vocabulary_lst = [
    {
        'id': 1,
        'name': '(first)Basic English',
        'wordpairs': [
            {'word': 'hello', 'translation': 'привіт', 'annotation': 'common greeting'}]},
    {
        'id': 2,
        'name': 'Advanced Grammar',
        'wordpairs': [
            {'word': 'predicate', 'translation': 'присудок', 'annotation': 'part of a sentence'},
            {'word': 'noun', 'translation': 'іменник'}]},
    {
        'id': 3,
        'name': 'Business English',
        'wordpairs': [
            {'word': 'meeting', 'translation': 'зустріч'},
            {'word': 'deadline', 'translation': 'крайній термін', 'annotation': 'important for projects'},
            {'word': 'presentation', 'translation': 'презентація'}]},
    {
        'id': 4,
        'name': 'Idioms & Phrases',
        'wordpairs': [
            {'word': 'break the ice', 'translation': 'зруйнувати лід'},
            {'word': 'hit the books', 'translation': 'вчитися старанно'}]},
    {
        'id': 5,
        'name': 'Common Verbs',
        'wordpairs': [
            {'word': 'run', 'translation': 'бігти'}]},
    {
        'id': 6,
        'name': 'Technical Terms',
        'wordpairs': [
            {'word': 'algorithm', 'translation': 'алгоритм', 'annotation': 'step-by-step procedure'},
            {'word': 'binary', 'translation': 'двійковий'}]},
    {
        'id': 7,
        'name': 'Travel Vocabulary',
        'wordpairs': [
            {'word': 'passport', 'translation': 'паспорт'},
            {'word': 'reservation', 'translation': 'бронювання'},
            {'word': 'luggage', 'translation': 'багаж', 'annotation': 'travel necessity'}]},
    {
        'id': 8,
        'name': 'Academic Words',
        'wordpairs': [
            {'word': 'thesis', 'translation': 'теза'},
            {'word': 'research', 'translation': 'дослідження', 'annotation': 'systematic investigation'}]},
    {
        'id': 9,
        'name': 'Conversational English',
        'wordpairs': [
            {'word': 'how are you?', 'translation': 'як ти?'}]},
    {
        'id': 10,
        'name': 'Slang & Colloquialisms',
        'wordpairs': [
            {'word': 'cool', 'translation': 'круто'},
            {'word': 'awesome', 'translation': 'чудово', 'annotation': 'expression of approval'},
            {'word': 'chill', 'translation': 'відпочивати'}]},
    {
        'id': 11,
        'name': 'Philosophy Terms',
        'wordpairs': [
            {'word': 'existence', 'translation': 'існування'}]},
    {
        'id': 12,
        'name': 'Medical Vocabulary',
        'wordpairs': [
            {'word': 'diagnosis', 'translation': 'діагноз'},
            {'word': 'treatment', 'translation': 'лікування', 'annotation': 'method of curing disease'}]},
    {
        'id': 13,
        'name': 'Computer Science Terms',
        'wordpairs': [
            {'word': 'variable', 'translation': 'змінна'},
            {'word': 'function', 'translation': 'функція', 'annotation': 'block of code'}]},
    {
        'id': 14,
        'name': 'Science Vocab',
        'wordpairs': [
            {'word': 'gravity', 'translation': 'гравітація'},
            {'word': 'atom', 'translation': 'атом', 'annotation': 'basic unit of matter'}]},
    {
        'id': 15,
        'name': 'Culinary Vocabulary',
        'wordpairs': [
            {'word': 'recipe', 'translation': 'рецепт'}]},
    {
        'id': 16,
        'name': 'Historical Terms',
        'wordpairs': [
            {'word': 'revolution', 'translation': 'революція'},
            {'word': 'empire', 'translation': 'імперія'}]},
    {
        'id': 17,
        'name': 'Geography Words',
        'wordpairs': [
            {'word': 'continent', 'translation': 'континент'},
            {'word': 'latitude', 'translation': 'широта'},
            {'word': 'equator', 'translation': 'екватор', 'annotation': 'imaginary line around the Earth'}]},
    {
        'id': 18,
        'name': 'Art & Culture',
        'wordpairs': [
            {'word': 'sculpture', 'translation': 'скульптура'},
            {'word': 'painting', 'translation': 'картина'}]},
    {
        'id': 19,
        'name': 'Literature Vocabulary',
        'wordpairs': [
            {'word': 'novel', 'translation': 'роман'},
            {'word': 'poetry', 'translation': 'поезія', 'annotation': 'literary form'}]},
    {
        'id': 20,
        'name': 'Sports Terms',
        'wordpairs': [
            {'word': 'goal', 'translation': 'гол'}]},
    {
        'id': 21,
        'name': 'Legal Terminology',
        'wordpairs': [
            {'word': 'contract', 'translation': 'контракт'},
            {'word': 'lawsuit', 'translation': 'судовий позов'}]},
    {
        'id': 22,
        'name': 'Engineering Vocabulary',
        'wordpairs': [
            {'word': 'blueprint', 'translation': 'план'},
            {'word': 'mechanism', 'translation': 'механізм', 'annotation': 'system of parts'}]},
    {
        'id': 23,
        'name': 'Financial Terms',
        'wordpairs': [
            {'word': 'investment', 'translation': 'інвестиція'},
            {'word': 'profit', 'translation': 'прибуток', 'annotation': 'financial gain'}]},
    {
        'id': 24,
        'name': 'Marketing Jargon',
        'wordpairs': [
            {'word': 'branding', 'translation': 'брендинг'},
            {'word': 'strategy', 'translation': 'стратегія'}]},
    {
        'id': 25,
        'name': '(last)Environmental Science',
        'wordpairs': [
            {'word': 'ecosystem', 'translation': 'екосистема'},
            {'word': 'pollution', 'translation': 'забруднення'}]}]


class VocabCallback(CallbackData, prefix='vocab'):
    vocab_id: int


class PaginationCallback(CallbackData, prefix='pagination'):
    name: str  # Ім'я
    page: int  # Номер сторінки
    limit: int  # Ліміт словників на сторінці


@router.callback_query(PaginationCallback.filter(F.name == 'vocab_base'))
async def process_vocab_base(callback: CallbackQuery, callback_data: PaginationCallback) -> None:
    current_page: int = callback_data.page  # Поточна сторінка
    total_vocabs: int = len(vocabulary_lst)  # Кількість всіх словників
    limit: int = callback_data.limit  # Ліміт словників на сторінці
    total_pages: int = (total_vocabs + limit - 1) // limit  # Кількість всіх можливих сторінок

    with Session() as db:
        # Отримання всіх словників, фільтруючи по user_id користувача
        user_vocabs: Query[Vocabulary] = db.query(Vocabulary).filter(User.id == Vocabulary.user_id)
        is_vocab_base_empty: bool = user_vocabs.count() == 0  # Флаг, чи порожня база словників користувача
        db.commit()

    if is_vocab_base_empty:
        msg_vocab_base: str = app_data['handlers']['vocab_base']['vocab_base_is_empty']
    else:
        msg_vocab_base: str = app_data['handlers']['vocab_base']['msg_select_vocab']

    # Перевірка меж сторінок
    if current_page <= 0:
        current_page = total_pages
    elif current_page > total_pages:
        current_page = 1

    # Початковий та кінцевий індекси для відображення словників
    start_offset: int = (current_page - 1) * limit
    end_offset: int = min(start_offset + limit, total_vocabs)

    # Клавіатура для пагінації
    kb: InlineKeyboardMarkup = get_inline_kb_vocab_base(start_offset,
                                                        end_offset,
                                                        current_page,
                                                        total_pages,
                                                        limit,
                                                        is_vocab_base_empty)

    await callback.message.edit_text(text=msg_vocab_base, reply_markup=kb)


def get_inline_kb_vocab_base(start_offset: int,
                                   end_offset: int,
                                   current_page: int,
                                   total_pages: int,
                                   limit: int,
                                   is_vocab_base_empty: bool) -> InlineKeyboardMarkup:
    """Генерує клавіатуру з кнопками для вибору словників та пагінації"""
    kb = InlineKeyboardBuilder()

    if not is_vocab_base_empty:
        # Додавання кнопок словників для поточної сторінки
        for vocab in vocabulary_lst[start_offset:end_offset]:
            total_wordpairs: int = len(vocab['wordpairs'])  # Кількість словникових пар у словнику
            vocab_button_text: str = f'{vocab['name']} [{total_wordpairs}]'
            kb.button(text=vocab_button_text, callback_data=VocabCallback(vocab_id=vocab['id']).pack())

        kb.adjust(1)

        btn_prev_page = InlineKeyboardButton(
            text='⬅️',
            callback_data=PaginationCallback(name='vocab_base', page=current_page - 1, limit=limit).pack())
        btn_page_info = InlineKeyboardButton(
            text=f'{current_page}/{total_pages}',
            callback_data='no_call')
        btn_next_page = InlineKeyboardButton(
            text='➡️',
            callback_data=PaginationCallback(name='vocab_base', page=current_page + 1, limit=limit).pack())

        kb.row(btn_prev_page, btn_page_info, btn_next_page, width=3)

    btn_add_vocab = InlineKeyboardButton(
        text='➕ Додати новий словник',
        callback_data='add_vocab')

    btn_menu = InlineKeyboardButton(
        text='🏠 Головне меню',
        callback_data='menu')

    kb.row(btn_add_vocab, btn_menu, width=1)

    return kb.as_markup()
