"""
Консольное приложение для преобразования передаточной функции
в описание в пространстве состояний (State-Space Representation).

Используются символьные вычисления (sympy).
Форма представления: каноническая управляемая форма (Controllable Canonical Form).

Передаточная функция:
          b_m * s^m + b_{m-1} * s^{m-1} + ... + b_0
G(s) = ----------------------------------------------
        s^n + a_{n-1} * s^{n-1} + ... + a_1 * s + a_0

Индекс коэффициента совпадает с показателем степени переменной s.
Номер свободного коэффициента — 0.
Порядок знаменателя n >= порядка числителя m.
"""

import sys
import sympy as sp


def tf_to_ss(num_order: int, den_order: int) -> tuple:
    """
    Преобразует передаточную функцию в пространство состояний
    с использованием символьных вычислений.

    Параметры
    ---------
    num_order : int
        Порядок числителя (m).
    den_order : int
        Порядок знаменателя (n). Должен быть >= num_order.

    Возвращает
    ----------
    (A, B, C, D) : tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]
        Матрицы пространства состояний:
        - A (n x n) — матрица динамики (сопровождающая)
        - B (n x 1) — матрица входа
        - C (1 x n) — матрица выхода
        - D (1 x 1) — матрица прямого прохода
    """
    if den_order < num_order:
        raise ValueError(
            "Порядок знаменателя (n) должен быть >= порядка числителя (m)."
        )

    n = den_order  # порядок системы

    # --- Символьные коэффициенты числителя: b0, b1, ..., bm ---
    # Индекс = показатель степени при s
    b = sp.symbols(f'b0:{num_order + 1}')

    # --- Символьные коэффициенты знаменателя: a0, a1, ..., a_{n-1} ---
    # Индекс = показатель степени при s (a_n = 1 — нормировка)
    a = sp.symbols(f'a0:{n}')

    # --- Матрица A (n x n) — сопровождающая матрица ---
    # Первая строка: [0, 0, ..., 0, -a0, -a1, ..., -a_{n-1}]
    # Единичная подматрица (n-1 x n-1) под первой строкой
    #
    # В управляемой канонической форме для:
    #   s^n + a_{n-1}*s^{n-1} + ... + a_0
    # первая строка A: [0, 0, ..., 0, -a0, -a1, ..., -a_{n-1}]
    # но в классической записи (с обратным порядком коэффициентов):
    #   A = [0   1   0  ...  0]
    #       [0   0   1  ...  0]
    #       [...           ...]
    #       [0   0   0  ...  1]
    #       [-a0 -a1 -a2 ... -a_{n-1}]
    #
    # Это companion matrix с коэффициентами в последней строке.
    A = sp.zeros(n, n)
    for i in range(n - 1):
        A[i, i + 1] = 1
    for j in range(n):
        A[n - 1, j] = -a[j]

    # --- Матрица B (n x 1) ---
    B = sp.zeros(n, 1)
    B[n - 1, 0] = 1

    # --- Матрица C (1 x n) ---
    # Коэффициенты числителя b0, b1, ..., b_{min(m, n-1)} располагаются
    # в первых (min(m, n-1) + 1) позициях.
    # Если m == n, то старший коэффициент b_n идёт в прямой проход D,
    # а в C записываются только b0..b_{n-1}.
    # Если m < n, то все b0..bm помещаются, остальные позиции — нули.
    C = sp.zeros(1, n)
    c_limit = min(num_order, n - 1)
    for j in range(c_limit + 1):
        C[0, j] = b[j]

    # --- Матрица D (1 x 1) ---
    # Прямой проход: D = 0, так как порядок числителя <= порядка знаменателя
    # (строго меньше — D=0; если равны — потребовалось бы деление,
    #  но в классической форме для строго правильных систем D=0).
    D = sp.zeros(1, 1)

    return A, B, C, D


def print_matrix(label: str, matrix: sp.Matrix) -> None:
    """Выводит матрицу с заголовком в читаемом виде."""
    print(f"\n{label}:")
    sp.pprint(matrix, use_unicode=False)


def parse_cli_args(args: list[str]) -> tuple[int, int] | None:
    """
    Парсит аргументы командной строки.

    Ожидается 2 аргумента: <порядок_числителя> <порядок_знаменателя>.

    Возвращает (m, n) или None, если аргументы некорректны.
    """
    if len(args) < 2:
        print(
            "Ошибка: требуется 2 аргумента: <порядок_числителя> <порядок_знаменателя>.",
            file=sys.stderr,
        )
        return None

    try:
        num_order = int(args[0])
        den_order = int(args[1])
    except ValueError:
        print("Ошибка: аргументы должны быть целыми числами.", file=sys.stderr)
        return None

    if num_order < 0:
        print("Ошибка: порядок числителя должен быть >= 0.", file=sys.stderr)
        return None

    if den_order <= 0:
        print("Ошибка: порядок знаменателя должен быть > 0.", file=sys.stderr)
        return None

    if den_order < num_order:
        print(
            "Ошибка: порядок знаменателя (n) должен быть >= порядка числителя (m).",
            file=sys.stderr,
        )
        return None

    return num_order, den_order


def interactive_input() -> tuple[int, int]:
    """Запрашивает у пользователя m и n в интерактивном режиме."""
    # --- Ввод порядка числителя ---
    while True:
        try:
            num_order = int(input("Введите порядок числителя (m): "))
            if num_order < 0:
                print("Ошибка: порядок должен быть натуральным числом (>= 0).")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число.")

    # --- Ввод порядка знаменателя ---
    while True:
        try:
            den_order = int(input("Введите порядок знаменателя (n): "))
            if den_order <= 0:
                print("Ошибка: порядок знаменателя должен быть натуральным числом (> 0).")
                continue
            if den_order < num_order:
                print("Ошибка: порядок знаменателя (n) должен быть >= порядка числителя (m).")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число.")

    return num_order, den_order


def print_banner() -> None:
    """Выводит приветственный баннер."""
    print("=" * 60)
    print("  ПРЕОБРАЗОВАНИЕ ПЕРЕДАТОЧНОЙ ФУНКЦИИ В ПРОСТРАНСТВО СОСТОЯНИЙ")
    print("=" * 60)
    print()
    print("Передаточная функция имеет вид:")
    print("    G(s) = (b_m*s^m + b_{m-1}*s^(m-1) + ... + b_0)")
    print("           / (s^n + a_{n-1}*s^(n-1) + ... + a_0)")
    print()
    print("Индекс коэффициента совпадает с показателем степени s.")
    print()


def print_result(num_order: int, den_order: int, A, B, C, D) -> None:
    """Выводит результат преобразования."""
    print(f"\nВыполняю преобразование для m={num_order}, n={den_order}...")

    print("\n" + "=" * 60)
    print("  РЕЗУЛЬТАТ: МАТРИЦЫ ПРОСТРАНСТВА СОСТОЯНИЙ")
    print("=" * 60)

    print_matrix("Матрица A (динамики)", A)
    print_matrix("Матрица B (входа)", B)
    print_matrix("Матрица C (выхода)", C)
    print_matrix("Матрица D (прямого прохода)", D)

    print("\n" + "=" * 60)
    print("  Система уравнений:")
    print("    dx/dt = A * x + B * u")
    print("    y     = C * x + D * u")
    print("=" * 60)


def main() -> None:
    """Главная функция консольного приложения."""
    has_cli_args = len(sys.argv) > 1

    if has_cli_args:
        # Режим командной строки — аргументы обязательны
        cli_result = parse_cli_args(sys.argv[1:])
        if cli_result is None:
            sys.exit(1)
        num_order, den_order = cli_result
        print_banner()
        print(f"Получены аргументы из командной строки: m={num_order}, n={den_order}")
    else:
        # Интерактивный режим (ввод с клавиатуры)
        print_banner()
        num_order, den_order = interactive_input()

    # --- Преобразование ---
    try:
        A, B, C, D = tf_to_ss(num_order, den_order)
    except ValueError as e:
        print(f"\nОшибка: {e}")
        return

    # --- Вывод результатов ---
    print_result(num_order, den_order, A, B, C, D)


if __name__ == "__main__":
    main()