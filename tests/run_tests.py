"""
Автоматическая программа тестирования для main.py.

Запускает main.py с различными аргументами командной строки
и проверяет корректность реакции программы (exit code, stdout, stderr).

Использование:
    python tests/run_tests.py

Все тесты запускаются через subprocess, что гарантирует
тестирование программы как "чёрного ящика".
"""

import subprocess
import sys
from pathlib import Path

# Путь к основной программе относительно корня проекта
MAIN_PY = Path(__file__).resolve().parent.parent / "src" / "main.py"


def run_test(
    test_num: int,
    description: str,
    args: list[str],
    expected_exit_code: int = 0,
    must_contain_stdout: list[str] | None = None,
    must_contain_stderr: list[str] | None = None,
    must_not_contain_stdout: list[str] | None = None,
) -> bool:
    """
    Запускает один тест.

    Параметры
    ---------
    test_num : int
        Номер теста.
    description : str
        Краткое описание теста.
    args : list[str]
        Аргументы командной строки для main.py.
    expected_exit_code : int
        Ожидаемый код возврата (0 — успех, 1 — ошибка).
    must_contain_stdout : list[str] | None
        Список строк, которые ОБЯЗАТЕЛЬНО должны присутствовать в stdout.
    must_contain_stderr : list[str] | None
        Список строк, которые ОБЯЗАТЕЛЬНО должны присутствовать в stderr.
    must_not_contain_stdout : list[str] | None
        Список строк, которые НЕ должны присутствовать в stdout.

    Возвращает
    ----------
    bool
        True, если тест пройден, False — если нет.
    """
    print(f"ТЕСТ №{test_num}: {description}")

    # Запускаем main.py как отдельный процесс
    cmd = [sys.executable, str(MAIN_PY)] + args
    result = subprocess.run(cmd, capture_output=True, text=True)

    stdout = result.stdout
    stderr = result.stderr
    actual_exit_code = result.returncode

    # Проверка exit code
    if actual_exit_code != expected_exit_code:
        print(f"  → СБОЙ: ожидался exit code {expected_exit_code}, "
              f"получен {actual_exit_code}")
        _print_output(stdout, stderr)
        return False

    # Проверка обязательных строк в stdout
    if must_contain_stdout:
        for phrase in must_contain_stdout:
            if phrase not in stdout:
                print(f"  → СБОЙ: в stdout не найдена строка '{phrase}'")
                _print_output(stdout, stderr)
                return False

    # Проверка обязательных строк в stderr
    if must_contain_stderr:
        for phrase in must_contain_stderr:
            if phrase not in stderr:
                print(f"  → СБОЙ: в stderr не найдена строка '{phrase}'")
                _print_output(stdout, stderr)
                return False

    # Проверка запрещённых строк в stdout
    if must_not_contain_stdout:
        for phrase in must_not_contain_stdout:
            if phrase in stdout:
                print(f"  → СБОЙ: в stdout найдена запрещённая строка '{phrase}'")
                _print_output(stdout, stderr)
                return False

    print("  → НОРМА")
    return True


def _print_output(stdout: str, stderr: str) -> None:
    """Выводит захваченный stdout и stderr для диагностики."""
    if stdout:
        print("  [stdout]")
        for line in stdout.splitlines():
            print(f"    {line}")
    if stderr:
        print("  [stderr]")
        for line in stderr.splitlines():
            print(f"    {line}")


def main() -> None:
    """Запускает все тесты и подводит итог."""
    print("=" * 60)
    print("  ТЕСТИРОВАНИЕ ПРОГРАММЫ ПРЕОБРАЗОВАНИЯ TF → SS")
    print("=" * 60)
    print()

    tests = [
        # --- Тест 1: корректные данные (m < n) ---
        {
            "description": "Корректный вызов: m=2, n=4",
            "args": ["2", "4"],
            "expected_exit_code": 0,
            "must_contain_stdout": [
                "Матрица A (динамики)",
                "Матрица B (входа)",
                "Матрица C (выхода)",
                "Матрица D (прямого прохода)",
                "b0  b1  b2  0",
            ],
        },
        # --- Тест 2: корректные данные (m = n) ---
        {
            "description": "Корректный вызов: m=3, n=3",
            "args": ["3", "3"],
            "expected_exit_code": 0,
            "must_contain_stdout": [
                "Матрица A (динамики)",
                "Матрица C (выхода)",
                "b0  b1  b2",
            ],
        },
        # --- Тест 3: m > n (ошибка) ---
        {
            "description": "Ошибка: m > n (m=5, n=3)",
            "args": ["5", "3"],
            "expected_exit_code": 1,
            "must_contain_stderr": [
                "порядок знаменателя (n) должен быть >= порядка числителя (m)",
            ],
        },
        # --- Тест 4: отрицательный m (ошибка) ---
        {
            "description": "Ошибка: отрицательный m (m=-1, n=3)",
            "args": ["-1", "3"],
            "expected_exit_code": 1,
            "must_contain_stderr": [
                "порядок числителя должен быть >= 0",
            ],
        },
        # --- Тест 5: n = 0 (ошибка) ---
        {
            "description": "Ошибка: n=0 (m=0, n=0)",
            "args": ["0", "0"],
            "expected_exit_code": 1,
            "must_contain_stderr": [
                "порядок знаменателя должен быть > 0",
            ],
        },
        # --- Тест 6: отрицательный n (ошибка) ---
        {
            "description": "Ошибка: отрицательный n (m=1, n=-3)",
            "args": ["1", "-3"],
            "expected_exit_code": 1,
            "must_contain_stderr": [
                "порядок знаменателя должен быть > 0",
            ],
        },
        # --- Тест 7: нечисловые аргументы (ошибка) ---
        {
            "description": "Ошибка: нечисловые аргументы (m=abc, n=3)",
            "args": ["abc", "3"],
            "expected_exit_code": 1,
            "must_contain_stderr": [
                "аргументы должны быть целыми числами",
            ],
        },
        # --- Тест 8: действительные числа (ошибка) ---
        {
            "description": "Ошибка: действительные числа (m=2.5, n=4)",
            "args": ["2.5", "4"],
            "expected_exit_code": 1,
            "must_contain_stderr": [
                "аргументы должны быть целыми числами",
            ],
        },
        # --- Тест 9: m = 0, n = 1 (минимальные корректные данные) ---
        {
            "description": "Корректный вызов: m=0, n=1",
            "args": ["0", "1"],
            "expected_exit_code": 0,
            "must_contain_stdout": [
                "Матрица A (динамики)",
                "Матрица C (выхода)",
                "b0",
            ],
        },
        # --- Тест 10: большие порядки ---
        {
            "description": "Корректный вызов: m=5, n=7",
            "args": ["5", "7"],
            "expected_exit_code": 0,
            "must_contain_stdout": [
                "Матрица A (динамики)",
                "Матрица C (выхода)",
                "b0  b1  b2  b3  b4  b5  0",
            ],
        },
        # --- Тест 11: m = n = 1 (простейшая система 1-го порядка) ---
        {
            "description": "Корректный вызов: m=1, n=1",
            "args": ["1", "1"],
            "expected_exit_code": 0,
            "must_contain_stdout": [
                "Матрица A (динамики)",
                "Матрица C (выхода)",
                "b0",
            ],
        },
        # --- Тест 12: только один аргумент (ошибка) ---
        {
            "description": "Ошибка: только один аргумент (m=3)",
            "args": ["3"],
            "expected_exit_code": 1,
            "must_contain_stderr": [
                "требуется 2 аргумента",
            ],
        },
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(tests, start=1):
        success = run_test(
            test_num=i,
            description=test["description"],
            args=test["args"],
            expected_exit_code=test.get("expected_exit_code", 0),
            must_contain_stdout=test.get("must_contain_stdout"),
            must_contain_stderr=test.get("must_contain_stderr"),
            must_not_contain_stdout=test.get("must_not_contain_stdout"),
        )
        if success:
            passed += 1
        else:
            failed += 1
        print()

    # --- Итог ---
    print("=" * 60)
    print("  ИТОГ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"  Всего тестов: {len(tests)}")
    print(f"  Пройдено:     {passed}")
    print(f"  Провалено:    {failed}")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())