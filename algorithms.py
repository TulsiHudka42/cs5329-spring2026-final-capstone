"""
algorithms.py
Contains the baseline and optimized implementations.
"""

from collections import defaultdict


def linear_search_by_title(records: list[dict], target_title: str) -> list[dict]:
    """
    Baseline approach: linear scan.

    Time complexity per query: O(n)
    Space complexity beyond input: O(k), where k is number of matches returned.
    """
    target = str(target_title).strip().lower()
    matches = []

    for record in records:
        if record.get("normalizedTitle", "") == target:
            matches.append(record)

    return matches


def build_title_hash_index(records: list[dict]) -> dict[str, list[dict]]:
    """
    Optimized approach: hash table index from normalized title to matching records.

    Build time: O(n)
    Extra space: O(n)
    """
    index = defaultdict(list)

    for record in records:
        index[record.get("normalizedTitle", "")].append(record)

    return dict(index)


def hash_search_by_title(index: dict[str, list[dict]], target_title: str) -> list[dict]:
    """
    Optimized search using a pre-built hash table.

    Average time complexity per query: O(1 + k), where k is number of matches returned.
    Worst case: O(n), if many records share the same key or hash collisions are severe.
    """
    target = str(target_title).strip().lower()
    return index.get(target, [])


def extract_ids(records: list[dict]) -> set[str]:
    """Return tconst IDs so baseline and optimized outputs can be compared."""
    return {str(record.get("tconst")) for record in records}
