import datetime
from collections import defaultdict

from src.api_search import get_currency_rate, get_stock_exchange


def greet_user(date: str) -> str:
    """Приветствует пользователя в зависимости от текущего времени суток.
    00:00-05:59: ночь
    06:00-11:59: утро
    12:00-17:59: день
    18:00-23:59: вечер"""

    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    current_time = date_obj.replace(year=1, month=1, day=1)

    if current_time >= datetime.datetime(1, 1, 1, 18, 0, 0):
        return "Добрый вечер"
    elif current_time >= datetime.datetime(1, 1, 1, 12, 0, 0):
        return "Добрый день"
    elif current_time >= datetime.datetime(1, 1, 1, 6, 0, 0):
        return "Доброе утро"
    else:
        return "Доброй ночи"


def get_cards_numbers(transactions_list: list[dict]) -> list[dict]:
    """По каждой карте находит последние 4 цифры, общую сумму расходов за текущий (последний) месяц и кешбэк."""

    cards: dict = defaultdict(int)
    for transaction in transactions_list:
        if transaction["Сумма операции"] < 0:
            cards[transaction["Номер карты"]] += transaction["Сумма операции с округлением"]

    result = []
    for key, value in cards.items():
        if str(key) != "nan":
            result.append(
                {
                    "last_digits": str(key)[1:],
                    "total_spent": round(value, 2),
                    "cashback": round(value / 100, 2),
                }
            )

    return result


def get_top_transactions(transactions_list: list[dict]) -> list[dict]:
    """Находит информацию по 5 наибольшим транзакциям за текущий (последний) месяц."""

    sorted_transactions_list = sorted(transactions_list, key=lambda x: x["Сумма операции"])
    top_transactions = []

    for i in range(5):
        if sorted_transactions_list[i]["Сумма операции"] < 0:
            top_transactions.append(
                {
                    "date": sorted_transactions_list[i]["Дата платежа"],
                    "amount": sorted_transactions_list[i]["Сумма операции с округлением"],
                    "category": sorted_transactions_list[i]["Категория"],
                    "description": sorted_transactions_list[i]["Описание"],
                }
            )
        else:
            # Если пополнения входят в топ 5, то платежей меньше 5
            return top_transactions

    return top_transactions


def main_page_func(
    date: str, transactions_list: list[dict], currencies: list[str], stocks: list[str], usd_rate: float = 1
) -> dict:
    """Основная функция страницы "Главная"."""
    result = {
        "greeting": greet_user(date),
        "cards": get_cards_numbers(transactions_list),
        "top_transactions": get_top_transactions(transactions_list),
        # "currency_rates": get_currency_rate(currencies),
        # "stock_prices": get_stock_exchange(stocks, usd_rate),
    }

    return result
