from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData  # Для створення callback data
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm.query import Query

from db.database import Session
from db.models import Vocabulary
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
async def process_vocab_pagination(callback: CallbackQuery, callback_data: PaginationCallback) -> None:
    current_page: int = callback_data.page  # Поточна сторінка
    total_vocabs: int = len(vocabulary_lst)  # Кількість всіх словників
    limit: int = callback_data.limit  # Ліміт словників на сторінці
    total_pages: int = (total_vocabs + limit - 1) // limit  # Кількість всіх можливих сторінок
    msg_select_vocab: str = app_data['handlers']['vocab_base']['msg_select_vocab']

    # Перевірка меж сторінок
    if current_page <= 0:
        current_page = total_pages
    elif current_page > total_pages:
        current_page = 1

    # Початковий та кінцевий індекси для відображення словників
    start_offset: int = (current_page - 1) * limit
    end_offset: int = min(start_offset + limit, total_vocabs)

    # Клавіатура для пагінації
    kb: InlineKeyboardMarkup = get_inline_kb_vocab_pagination(start_offset,
                                                              end_offset,
                                                              current_page,
                                                              total_pages,
                                                              limit)

    await callback.message.edit_text(text=msg_select_vocab, reply_markup=kb)


def get_inline_kb_vocab_pagination(start_offset: int,
                                   end_offset: int,
                                   current_page: int,
                                   total_pages: int,
                                   limit: int) -> InlineKeyboardMarkup:
    """Генерує клавіатуру з кнопками для вибору словників та пагінації"""
    kb = InlineKeyboardBuilder()

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
        callback_data='no_callback')
    btn_next_page = InlineKeyboardButton(
        text='➡️',
        callback_data=PaginationCallback(name='vocab_base', page=current_page + 1, limit=limit).pack())

    btn_add_vocab = InlineKeyboardButton(
        text='➕ Додати новий словник',
        callback_data='add_vocab')

    btn_menu = InlineKeyboardButton(
        text='🏠 Головне меню',
        callback_data='menu')

    kb.row(btn_prev_page, btn_page_info, btn_next_page, width=3)
    kb.row(btn_add_vocab, btn_menu, width=1)

    return kb.as_markup()

'''
def get_inline_kb_user_vocabs(user_vocabs) -> InlineKeyboardMarkup:
    """Повертає клавіатуру з словниками користувача"""
    inline_builder = InlineKeyboardBuilder()

    btn_menu = InlineKeyboardButton(text='Головне меню',
                                    callback_data='menu')
    btn_vocab_add = InlineKeyboardButton(text='Додати словник',
                                        callback_data='vocab_add')

    # Флаг, чи порожня база словників користувача
    is_vocab_base_empty: bool = len(user_vocabs.all()) == 0

    if not is_vocab_base_empty:
        with Session() as db:
            wordpair_count: str = len(user_vocabs.all())  # Кількість словникових пар в словнику

            for num, item in enumerate(iterable=user_vocabs,
                                       start=1):
                vocab_name: str = item.name  # Назва словника
                # Кількість словникових пар у словнику
                wordpair_count = db.query(WordPair).filter(WordPair.vocabulary_id == item.id).count()

                btn_text: str = f'{vocab_name} [{wordpair_count}]'  # Текст кнопки

                inline_builder.button(text=btn_text,
                                      callback_data=f'vocab_id_{num}')

    inline_builder.adjust(1)  # Кількість кнопок у рядку
    inline_builder.row(btn_vocab_add, btn_menu, width=2)

    return inline_builder.as_markup()
    vocab_id: str  # Дія (наступна або попередня сторінка)


def paginator(page: int = 0):
    vocabulary_lst = [
    {
        'id': 1,
        'name': 'Basic English',
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
        'name': 'Environmental Science',
        'wordpairs': [
            {'word': 'ecosystem', 'translation': 'екосистема'},
            {'word': 'pollution', 'translation': 'забруднення'}]}]

    builder = InlineKeyboardBuilder()  # Создание объекта InlineKeyboardBuilder
    start_offset = page * 3  # Вычисление начального смещения на основе номера страницы
    limit = 3  # Определение лимита пользователей на одной странице
    end_offset = start_offset + limit  # Вычисление конечного смещения
    for vocab in vocabulary_lst[start_offset:end_offset]:  # Перебор пользователей для текущей страницы
        builder.row(InlineKeyboardButton(text=vocab['name'], callback_data=Vocab(vocab_id=vocab['id']).pack()))  # Добавление кнопки для каждого пользователя

    buttons_row = []  # Создание списка кнопок
    if page > 0:  # Проверка, что страница не первая
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=Pagination(action='prev', page=page - 1).pack()))  # Добавление кнопки "назад"
    if end_offset < len(vocabulary_lst):  # Проверка, что ещё есть пользователи для следующей страницы
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action='next', page=page + 1).pack()))  # Добавление кнопки "вперед"
    else:  # Если пользователи закончились
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action='next', page=0).pack()))  # Возвращение на первую страницу
    builder.row(*buttons_row)  # Добавление кнопок навигации
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))  # Добавление кнопки "назад"
    return builder.as_markup()  # Возвращение клавиатуры в виде разметки


# Обработчик нажатия кнопок навигации
@router.callback_query(Pagination.filter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination):
    page = callback_data.page  # Получение номера страницы из callback data
    await call.message.edit_reply_markup(reply_markup=paginator(page=page))  # Обновление клавиатуры при нажатии кнопок "вперед" или "назад"


@router.callback_query(F.data == 'vocab_base')
async def process_btn_vocab_base(callback: CallbackQuery) -> None:
    """Відстежує натискання на кнопку бази словників.
    Відправляє користувачу список його словників.
    """
    vocabulary_dict: dict[str, dict[str, dict[str, str]]] = {
    'Basic English': {
        'wordpair1': {'word': 'hello', 'translation': 'привіт', 'annotation': 'common greeting'}},
    'Advanced Grammar': {
        'wordpair1': {'word': 'predicate', 'translation': 'присудок', 'annotation': 'part of a sentence'},
        'wordpair2': {'word': 'noun', 'translation': 'іменник'}},
    'Business English': {
        'wordpair1': {'word': 'meeting', 'translation': 'зустріч'},
        'wordpair2': {'word': 'deadline', 'translation': 'крайній термін', 'annotation': 'important for projects'},
        'wordpair3': {'word': 'presentation', 'translation': 'презентація'}},
    'Idioms & Phrases': {
        'wordpair1': {'word': 'break the ice', 'translation': 'зруйнувати лід'},
        'wordpair2': {'word': 'hit the books', 'translation': 'вчитися старанно'}},
    'Common Verbs': {
        'wordpair1': {'word': 'run', 'translation': 'бігти'}},
    'Technical Terms': {
        'wordpair1': {'word': 'algorithm', 'translation': 'алгоритм', 'annotation': 'step-by-step procedure'},
        'wordpair2': {'word': 'binary', 'translation': 'двійковий'}},
    'Travel Vocabulary': {
        'wordpair1': {'word': 'passport', 'translation': 'паспорт'},
        'wordpair2': {'word': 'reservation', 'translation': 'бронювання'},
        'wordpair3': {'word': 'luggage', 'translation': 'багаж', 'annotation': 'travel necessity'}},
    'Academic Words': {
        'wordpair1': {'word': 'thesis', 'translation': 'теза'},
        'wordpair2': {'word': 'research', 'translation': 'дослідження', 'annotation': 'systematic investigation'}},
    'Conversational English': {
        'wordpair1': {'word': 'how are you?', 'translation': 'як ти?'}},
    'Slang & Colloquialisms': {
        'wordpair1': {'word': 'cool', 'translation': 'круто'},
        'wordpair2': {'word': 'awesome', 'translation': 'чудово', 'annotation': 'expression of approval'},
        'wordpair3': {'word': 'chill', 'translation': 'відпочивати'}},
    'Philosophy Terms': {
        'wordpair1': {'word': 'existence', 'translation': 'існування'}},
    'Medical Vocabulary': {
        'wordpair1': {'word': 'diagnosis', 'translation': 'діагноз'},
        'wordpair2': {'word': 'treatment', 'translation': 'лікування', 'annotation': 'method of curing disease'}},
    'Computer Science Terms': {
        'wordpair1': {'word': 'variable', 'translation': 'змінна'},
        'wordpair2': {'word': 'function', 'translation': 'функція', 'annotation': 'block of code'}},
    'Science Vocab': {
        'wordpair1': {'word': 'gravity', 'translation': 'гравітація'},
        'wordpair2': {'word': 'atom', 'translation': 'атом', 'annotation': 'basic unit of matter'}},
    'Culinary Vocabulary': {
        'wordpair1': {'word': 'recipe', 'translation': 'рецепт'}},
    'Historical Terms': {
        'wordpair1': {'word': 'revolution', 'translation': 'революція'},
        'wordpair2': {'word': 'empire', 'translation': 'імперія'}},
    'Geography Words': {
        'wordpair1': {'word': 'continent', 'translation': 'континент'},
        'wordpair2': {'word': 'latitude', 'translation': 'широта'},
        'wordpair3': {'word': 'equator', 'translation': 'екватор', 'annotation': 'imaginary line around the Earth'}},
    'Art & Culture': {
        'wordpair1': {'word': 'sculpture', 'translation': 'скульптура'},
        'wordpair2': {'word': 'painting', 'translation': 'картина'}},
    'Literature Vocabulary': {
        'wordpair1': {'word': 'novel', 'translation': 'роман'},
        'wordpair2': {'word': 'poetry', 'translation': 'поезія', 'annotation': 'literary form'}},
    'Sports Terms': {
        'wordpair1': {'word': 'goal', 'translation': 'гол'}},
    'Legal Terminology': {
        'wordpair1': {'word': 'contract', 'translation': 'контракт'},
        'wordpair2': {'word': 'lawsuit', 'translation': 'судовий позов'}},
    'Engineering Vocabulary': {
        'wordpair1': {'word': 'blueprint', 'translation': 'план'},
        'wordpair2': {'word': 'mechanism', 'translation': 'механізм', 'annotation': 'system of parts'}},
    'Financial Terms': {
        'wordpair1': {'word': 'investment', 'translation': 'інвестиція'},
        'wordpair2': {'word': 'profit', 'translation': 'прибуток', 'annotation': 'financial gain'}},
    'Marketing Jargon': {
        'wordpair1': {'word': 'branding', 'translation': 'брендинг'},
        'wordpair2': {'word': 'strategy', 'translation': 'стратегія'}},
    'Environmental Science': {
        'wordpair1': {'word': 'ecosystem', 'translation': 'екосистема'},
        'wordpair2': {'word': 'pollution', 'translation': 'забруднення'}}}

    user_id: int = callback.from_user.id

    kb: InlineKeyboardMarkup = paginator()

    msg_vocab_base: str = app_data['handlers']['vocab_base']['msg_select_vocab']

    await callback.message.edit_text(text=msg_vocab_base,
                                     reply_markup=kb)
'''

"""@router.callback_query(F.data == 'vocab_base')
async def process_btn_vocab_base(callback: CallbackQuery) -> None:
    '''Відстежує натискання на кнопку бази словників.
    Відправляє користувачу список його словників.
    '''
    with Session() as db:
        user_id: int = callback.from_user.id
        # Отримання усіх словників, фільтруючи їх по user_id користувача
        user_vocabs: Query[Vocabulary] = db.query(Vocabulary).filter(user_id == Vocabulary.user_id)

        # Флаг, чи порожня база словників користувача
        is_vocab_base_empty: bool = len(user_vocabs.all()) == 0

        kb: InlineKeyboardMarkup = get_inline_kb_user_vocabs(user_vocabs)
        db.commit()

    # Якщо база словників порожня
    if is_vocab_base_empty:
        msg_vocab_base: str = app_data['handlers']['vocab_base']['vocab_base_is_empty']
    else:
        msg_vocab_base: str = app_data['handlers']['vocab_base']['msg_select_vocab']

    await callback.message.edit_text(text=msg_vocab_base,
                                     reply_markup=kb)

"""
"""
@router.callback_query(F.data == 'dict_add')
async def process_btn_dict_add(callback: CallbackQuery):

    text_dict_add = 'Введите название нового словаря'
    await callback.message.edit_text(text=text_dict_add)


# Обработчик нажатия кнопок
@router.callback_query()
async def process_callback(callback: CallbackQuery):
    if callback.data.startswith('call_dict_'):
        # Получаем номер словаря из callback_data
        dict_id = int(callback.data.split('_')[1])
        with Session as db:
            all_user_dicts = db.query(
                Vocab).filter(User.id == Vocab.user_id)
            # Vocab_name = db.query(Vocab).filter(
            #     Vocab.id == vocab_id)
            db.commit()

    inline_keyboard = get_inline_kb_dict()
    await callback.message.edit_text(
        text=all_user_dicts[dict_id],
        reply_markup=inline_keyboard)
"""
