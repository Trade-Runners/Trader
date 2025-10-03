import csv
import os
from typing import List, Set, Optional
from pathlib import Path

current_dir = Path(__file__).parent
submission_path = current_dir.parent / "data" / "processed" / "submission.csv"
# test_path = current_dir.parent / "data" / "processed" / "test_.csv"


class SubmissionValidator:
    """
    Валидатор submission файла.

    Проверяет:
    - Наличие файла data/processed/submission.csv (или указанного файла)
    - Правильную структуру (uid;type;request)
    - Соответствие количества строк с test.csv
    - Наличие всех uid из test.csv
    - Валидность HTTP методов в type
    - Валидность API путей в request
    - Отсутствие пустых значений
    - Уникальность uid
    """

    def __init__(
        self,
        test_path: str,
        submission_path: Optional[str] = None,
    ):

        # Устанавливаем путь по умолчанию, если не указан
        if submission_path is None:
            self.submission_path = submission_path
        else:
            self.submission_path = Path(submission_path)

        self.test_path = current_dir.parent / test_path
        self.valid_methods = {
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
        }

    def run_all_validations(self) -> List[tuple]:
        """
        Запуск всех проверок валидации.

        Returns:
            Список кортежей (название_проверки, успех, ошибка)
        """
        results = []

        # Проверка наличия файла submission
        if not self.submission_path.exists():
            results.append(
                (
                    "Проверка наличия submission файла",
                    False,
                    f"Файл {self.submission_path} не найден",
                )
            )
            return results

        results.append(("Проверка наличия submission файла", True, None))

        # Проверка наличия файла test
        if not self.test_path.exists():
            results.append(
                (
                    "Проверка наличия test файла",
                    False,
                    f"Файл {self.test_path} не найден",
                )
            )
            return results

        results.append(("Проверка наличия test файла", True, None))

        try:
            # Чтение файлов
            submission_data = self._read_csv(self.submission_path)
            test_data = self._read_csv(self.test_path)

            # Проверка структуры submission файла
            if len(submission_data) == 0:
                results.append(
                    ("Проверка структуры файла", False, "Файл submission.csv пуст")
                )
                return results

            if not all(len(row) == 3 for row in submission_data):
                results.append(
                    (
                        "Проверка структуры файла",
                        False,
                        "Некорректная структура файла: ожидается 3 колонки (uid;type;request)",
                    )
                )
                return results

            results.append(("Проверка структуры файла", True, None))

            # Извлечение данных
            submission_rows = submission_data[1:]  # Пропускаем заголовок
            test_uids = {row[0] for row in test_data[1:]}  # Получаем uid из test.csv

            submission_uids = set()
            for i, row in enumerate(submission_rows, start=2):
                if len(row) != 3:
                    continue  # Ошибка структуры уже проверена выше

                uid, method, request = row

                # Проверка на пустые значения
                if not uid or not method or not request:
                    results.append(
                        (
                            f"Проверка пустых значений (строка {i})",
                            False,
                            f"Строка {i}: обнаружены пустые значения",
                        )
                    )
                    continue

                # Проверка уникальности uid
                if uid in submission_uids:
                    results.append(
                        (
                            f"Проверка уникальности uid (строка {i})",
                            False,
                            f"Строка {i}: дублирование uid '{uid}'",
                        )
                    )
                submission_uids.add(uid)

                # Проверка валидности HTTP метода
                if method not in self.valid_methods:
                    results.append(
                        (
                            f"Проверка валидности HTTP метода (строка {i})",
                            False,
                            f"Строка {i}: некорректный HTTP метод '{method}'. Допустимые значения: {', '.join(sorted(self.valid_methods))}",
                        )
                    )

                # Проверка валидности API пути
                if not request.startswith("/"):
                    results.append(
                        (
                            f"Проверка валидности API пути (строка {i})",
                            False,
                            f"Строка {i}: некорректный путь запроса '{request}'. Путь должен начинаться с '/'",
                        )
                    )

            # Проверка соответствия количества строк
            if len(submission_rows) != len(test_uids):
                results.append(
                    (
                        "Проверка соответствия количества строк",
                        False,
                        f"Некорректное количество строк: ожидается {len(test_uids)}, найдено {len(submission_rows)}",
                    )
                )
            else:
                results.append(("Проверка соответствия количества строк", True, None))

            # Проверка наличия всех uid из test.csv
            missing_uids = test_uids - submission_uids
            if missing_uids:
                results.append(
                    (
                        "Проверка наличия всех uid из test.csv",
                        False,
                        f"Отсутствуют записи для uid: {', '.join(sorted(missing_uids)[:5])}{'...' if len(missing_uids) > 5 else ''}",
                    )
                )
            else:
                results.append(("Проверка наличия всех uid из test.csv", True, None))

            # Проверка отсутствия лишних uid
            extra_uids = submission_uids - test_uids
            if extra_uids:
                results.append(
                    (
                        "Проверка отсутствия лишних uid",
                        False,
                        f"Обнаружены лишние uid, отсутствующие в test.csv: {', '.join(sorted(extra_uids)[:5])}{'...' if len(extra_uids) > 5 else ''}",
                    )
                )
            else:
                results.append(("Проверка отсутствия лишних uid", True, None))

        except Exception as e:
            results.append(
                (
                    "Проверка обработки файлов",
                    False,
                    f"Ошибка при обработке файлов: {str(e)}",
                )
            )

        return results  # ⚠️ ВАЖНО: добавить возврат результатов!

    def _read_csv(self, file_path: Path) -> List[List[str]]:
        """
        Чтение CSV файла с разделителем ';'.

        Args:
            file_path: Путь к файлу

        Returns:
            Список строк, каждая строка - список значений
        """
        data = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=";")
                for row in reader:
                    data.append([cell.strip() for cell in row])
        except Exception as e:
            raise Exception(f"Не удалось прочитать файл {file_path}: {str(e)}")

        return data
