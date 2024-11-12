
from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


async def save_current_fsm_state(state: FSMContext, new_state: State) -> None:
    """Зберігає поточний стан FSM та оновлює FSM-Cache зі значенням нового стану"""
    await state.set_state(new_state)
    await state.update_data(current_stage=new_state)


async def extend_valid_wordpairs_to_fsm_cache(state: FSMContext, wordpairs: list[str] | None) -> None:
    """Розширює список валідних словникових пар в FSM-кеші"""
    data_fsm: dict[str, Any] = await state.get_data()

    valid_wordpairs_cache: list[str] = data_fsm.get('all_valid_wordpairs') or []
    valid_wordpairs_cache.extend(wordpairs)

    # Оновлення FSM-Cache із новим списком валідних пар
    await state.update_data(all_valid_wordpairs=valid_wordpairs_cache)


async def extend_invalid_wordpairs_to_fsm_cache(state: FSMContext, wordpairs: list[dict] | None) -> None:
    """Розширює список не валідних словникових пар в FSM-кеші"""
    data_fsm: dict[str, Any] = await state.get_data()

    invalid_wordpairs_cache: list[dict] = data_fsm.get('all_invalid_wordpairs') or []
    invalid_wordpairs_cache.extend(wordpairs)

    # Оновлення FSM-Cache із новим списком не валідних пар
    await state.update_data(all_invalid_wordpairs=invalid_wordpairs_cache)


def check_has_valid_wordpairs_in_fsm_cache(data_fsm: dict) -> bool:
    """Перевіряє, чи є валідні словникові пари в FSM-кеші"""
    all_valid_wordpairs: list[str] | None = data_fsm.get('all_valid_wordpairs')
    return bool(all_valid_wordpairs)
