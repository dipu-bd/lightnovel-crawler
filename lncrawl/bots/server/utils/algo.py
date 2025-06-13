from typing import Any, Callable, List


def binary_search(
    items: List[Any],
    target: Any,
    compare: Callable[[Any, Any], bool],
):
    left = 0
    right = len(items) - 1
    while left <= right:
        mid = (left + right) // 2
        if compare(items[mid], target):
            left = mid + 1
        elif compare(target, items[mid]):
            right = mid - 1
        else:
            return mid
    return None
