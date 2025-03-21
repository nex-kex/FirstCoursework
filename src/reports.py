import datetime
import logging
import os
from functools import wraps
from typing import Any, Callable

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.views import create_report

log_path = "../logs/reports.log"

# Устраняет ошибку отсутствия файла при импорте модуля
if str(os.path.dirname(os.path.abspath(__name__)))[-3:] != "src":
    log_path = log_path[1:]

logger = logging.getLogger("reports")
file_handler = logging.FileHandler(log_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def save_report(filename: str = "") -> Callable:
    """Декоратор для функций-отчётов, который записывает в файл результат, возвращаемый функциям,
    формирующими отчёты."""

    def my_decorator(func: Callable) -> Callable:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            # Проверка на наличие ошибок
            try:
                result = func(*args, **kwargs)

                # Запись в файл
                if filename == "":
                    logger.info("Название файла не задано, запись в стандартный файл")
                    create_report(result.to_dict(orient="records"), "../output/report_result.json")
                else:
                    create_report(result.to_dict(orient="records"), filename)

            except Exception as e:
                logger.critical(f"Произошла ошибка при выполнении функции {func.__name__}: {e}")
                raise e

            return result

        return wrapper

    return my_decorator


@save_report(filename="../output/spending_by_category.json")
def spending_by_category(transactions: pd.DataFrame, category: str, date: str = "") -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    Если дата не передана, то берется текущая дата."""

    try:
        # Приводит дату к строке обычного формата
        if not date:
            date_obj = datetime.datetime.now()
            logger.info(f"Дата для поиска не передана. Поиск ведётся от {date_obj.strftime("%d-%m-%Y")}")
        else:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            logger.info(f"Ведётся поиск от {date[:10]}")

        dates = []

        # Добавляет 3 последних месяца в список в формате MM.YYYY
        for i in range(3):
            date_i = date_obj + relativedelta(months=-i)
            date_i_str = date_i.strftime("%m.%Y")
            dates.append(date_i_str)

        # Проверка на то, что это расход и он был успешно выполнен
        sorted_transactions_list = transactions.loc[
            (transactions["Статус"] == "OK")
            & (transactions["Сумма операции"] < 0)
            & (transactions["Категория"] == category.capitalize())
        ]

        category_spending = 0

        for index, transaction in sorted_transactions_list.iterrows():
            if any(date in transaction["Дата операции"] for date in dates):
                category_spending += transaction["Сумма операции с округлением"]

        answer = {
            category.capitalize(): round(category_spending, 2),
        }

        return pd.DataFrame([answer])

    except KeyError as e:
        logger.warning(f"Передана транзакция без необходимого ключа: {e}")

    except Exception as e:
        logger.warning(f"Произошла ошибка: {e}")

    return pd.DataFrame({})


# Нет уже сил переделать, но жалко удалять(
# @save_report(filename="../output/spending_by_weekday.json")
# def spending_by_weekday(transactions: list[dict], date: str = "") -> dict:
#     """Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты).
#     Если дата не передана, то берется текущая дата."""
#
#     # Приводит дату к строке обычного формата
#     if not date:
#         date_obj = datetime.datetime.now()
#         logger.info(f"Дата для поиска не передана. Поиск ведётся от {date_obj.strftime("%d-%m-%Y")}")
#     else:
#         date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
#         logger.info(f"Ведётся поиск от {date[:10]}")
#
#     dates = []
#
#     # Добавляет 3 последних месяца в список в формате MM.YYYY
#     for i in range(3):
#         date_i = date_obj + relativedelta(months=-i)
#         date_i_str = date_i.strftime("%m.%Y")
#         dates.append(date_i_str)
#
#     weekdays_spending = defaultdict(list)
#     weekdays_avg_spending = defaultdict(float)
#
#     # Сортировка расходов за последние 3 месяца по спискам (выходные и рабочие дни)
#     for transaction in transactions:
#         try:
#             if any(date in transaction["Дата операции"] for date in dates):
#
#                 # Проверка на то, что это расход и он был успешно выполнен
#                 if transaction["Статус"] == "OK" and transaction["Сумма операции"] < 0:
#
#                     workday_str = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
#                     weekday = datetime.datetime.strftime(workday_str, "%A")
#
#                     weekdays_spending[weekday].append(transaction["Сумма операции с округлением"])
#
#         except KeyError as e:
#             logger.warning(f"Передана транзакция без необходимого ключа: {e}")
#             continue
#
#     for day, sums in weekdays_spending.items():
#         weekdays_avg_spending[day] = round(sum(sums) / len(sums), 2)
#
#     return weekdays_avg_spending
#
#
# Нет уже сил переделать, но жалко удалять(
# @save_report(filename="../output/spending_by_workday.json")
# def spending_by_workday(transactions: list[dict], date: str = "") -> dict:
#     """Функция выводит средние траты в рабочий и в выходной день за последние три месяца (от переданной даты).
#     Если дата не передана, то берется текущая дата."""
#
#     # Приводит дату к строке обычного формата
#     if not date:
#         date_obj = datetime.datetime.now()
#         logger.info(f"Дата для поиска не передана. Поиск ведётся от {date_obj.strftime("%d-%m-%Y")}")
#     else:
#         date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
#         logger.info(f"Ведётся поиск от {date[:10]}")
#
#     dates = []
#
#     # Добавляет 3 последних месяца в список в формате MM.YYYY
#     for i in range(3):
#         date_i = date_obj + relativedelta(months=-i)
#         date_i_str = date_i.strftime("%m.%Y")
#         dates.append(date_i_str)
#
#     workdays_transactions = []
#     weekends_transactions = []
#
#     # Сортировка расходов за последние 3 месяца по спискам (выходные и рабочие дни)
#     for transaction in transactions:
#         try:
#             if any(date in transaction["Дата операции"] for date in dates):
#
#                 # Проверка на то, что это расход и он был успешно выполнен
#                 if transaction["Статус"] == "OK" and transaction["Сумма операции"] < 0:
#
#                     workday_str = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
#                     workday = datetime.datetime.strftime(workday_str, "%w")
#
#                     if workday == "0" or workday == "6":  # 0 — воскресенье, 6 — суббота
#                         weekends_transactions.append(transaction["Сумма операции с округлением"])
#
#                     else:
#                         workdays_transactions.append(transaction["Сумма операции с округлением"])
#
#         except KeyError as e:
#             logger.warning(f"Передана транзакция без необходимого ключа: {e}")
#             continue
#
#     if len(workdays_transactions):
#         avg_workday_spending = round(sum(workdays_transactions) / len(workdays_transactions), 2)
#         logger.info("Успешно получена средние траты в будние дни")
#
#     else:
#         avg_workday_spending = 0
#         logger.info("Трат в будние дни не было")
#
#     if len(weekends_transactions):
#         avg_weekend_spending = round(sum(weekends_transactions) / len(weekends_transactions), 2)
#         logger.info("Успешно получена средние траты в выходные дни")
#
#     else:
#         avg_weekend_spending = 0
#         logger.info("Трат в выходные дни не было")
#
#     answer = {
#         "avg_workday_spending": avg_workday_spending,
#         "avg_weekend_spending": avg_weekend_spending,
#     }
#
#     return answer
