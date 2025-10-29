"""Inventory system module.

Provides a tiny in-memory inventory with load/save helpers. This module is
intentionally small and includes input validation and safe file handling so it
is suitable for static-analysis exercises.
"""

import json
import logging
from datetime import datetime

stock_data = {}


def add_item(item="default", qty=0, logs=None):
    """Add ``qty`` of ``item`` to :data:`stock_data`.

    Args:
        item (str): item name.
        qty (int): non-negative quantity to add.
        logs (list|None): optional list to append a timestamped message.

    The function validates inputs and logs errors rather than raising for
    invalid user-supplied values.
    """
    if logs is None:
        logs = []
    # input validation
    if not isinstance(item, str):
        logging.error(
            "add_item: 'item' must be a str (got %s). Skipping.", type(item)
        )
        return
    if not isinstance(qty, int) or qty < 0:
        logging.error(
            "add_item: 'qty' must be a non-negative int (got %r). "
            "Skipping.",
            qty,
        )
        return

    if not item:
        return

    stock_data[item] = stock_data.get(item, 0) + qty
    logs.append(f"{datetime.now()}: Added {qty} of {item}")


def remove_item(item, qty):
    """Remove ``qty`` of ``item`` from :data:`stock_data`.

    If the item does not exist, a warning is logged. Only :class:`KeyError` is
    handled explicitly to avoid masking programming errors.
    """
    if not isinstance(item, str):
        logging.error(
            "remove_item: 'item' must be a str (got %s). Skipping.", type(item)
        )
        return
    if not isinstance(qty, int) or qty <= 0:
        logging.error(
            "remove_item: 'qty' must be a positive int (got %r). "
            "Skipping.",
            qty,
        )
        return

    try:
        stock_data[item] -= qty
        if stock_data[item] <= 0:
            del stock_data[item]
    except KeyError:
        logging.warning("remove_item: item '%s' not found in stock.", item)


def get_qty(item):
    """Return quantity for ``item`` (0 if missing)."""
    if not isinstance(item, str):
        logging.error("get_qty: 'item' must be a str (got %s).", type(item))
        return 0
    return stock_data.get(item, 0)


def load_data(file="inventory.json"):
    """Load inventory from a JSON file into :data:`stock_data`.

    The function logs and keeps the existing in-memory data if the file is
    missing or contains invalid JSON.
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.warning(
            "load_data: file %s not found - starting with empty "
            "inventory",
            file,
        )
        return
    except json.JSONDecodeError:
        logging.exception("load_data: failed to decode JSON from %s", file)
        return

    if isinstance(data, dict):
        stock_data.clear()
        stock_data.update(data)
    else:
        logging.error("load_data: expected a JSON object/dict in %s", file)


def save_data(file="inventory.json"):
    """Save the in-memory :data:`stock_data` to a JSON file.

    Uses explicit encoding and reports IO errors.
    """
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(stock_data, f, ensure_ascii=False, indent=2)
    except OSError:
        logging.exception("save_data: failed to write to %s", file)


def print_data():
    """Log the inventory contents at INFO level."""
    logging.info("Items Report")
    for i in stock_data:
        logging.info("%s -> %s", i, stock_data.get(i))


def check_low_items(threshold=5):
    """Return a list of item names whose quantity is below ``threshold``."""
    result = []
    for i in stock_data:
        if stock_data.get(i, 0) < threshold:
            result.append(i)
    return result


def main():
    """Entry point for manual runs of this module (configures logging)."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )

    add_item("apple", 10)
    add_item("banana", 2)
    add_item("orange", 5)
    remove_item("apple", 3)
    remove_item("orange", 1)

    logging.info("Apple stock: %s", get_qty("apple"))
    logging.info("Low items: %s", check_low_items())

    save_data()
    load_data()
    print_data()


if __name__ == "__main__":
    main()
