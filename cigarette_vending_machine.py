"""
Digital Cigarette Vending Machine
==================================
A command-line simulation of a digital cigarette vending machine.

Features:
  - Product catalog with multiple brands and prices
  - Inventory / stock tracking
  - Insert money (coins and bills)
  - Purchase flow with change calculation
  - Age-verification gate
  - Admin mode: restock items and view sales report
"""

from __future__ import annotations

import secrets
import sys
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class Product:
    """Represents a cigarette product available in the machine."""

    def __init__(self, name: str, brand: str, price: float, stock: int) -> None:
        if price < 0:
            raise ValueError(f"Price cannot be negative: {price}")
        if stock < 0:
            raise ValueError(f"Stock cannot be negative: {stock}")
        self.name = name
        self.brand = brand
        self.price = price
        self.stock = stock

    def is_available(self) -> bool:
        """Return True when there is at least one unit in stock."""
        return self.stock > 0

    def restock(self, quantity: int) -> None:
        """Add *quantity* units to stock."""
        if quantity <= 0:
            raise ValueError(f"Restock quantity must be positive, got {quantity}")
        self.stock += quantity

    def dispense(self) -> None:
        """Remove one unit from stock (call after a successful purchase)."""
        if self.stock == 0:
            raise RuntimeError(f"'{self.name}' is out of stock")
        self.stock -= 1

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Product(name={self.name!r}, brand={self.brand!r}, "
            f"price={self.price:.2f}, stock={self.stock})"
        )


class SaleRecord:
    """Immutable record of a completed sale."""

    def __init__(self, product: Product, amount_paid: float, change: float) -> None:
        self.product_name = product.name
        self.brand = product.brand
        self.price = product.price
        self.amount_paid = amount_paid
        self.change = change

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SaleRecord(product={self.product_name!r}, price={self.price:.2f}, "
            f"paid={self.amount_paid:.2f}, change={self.change:.2f})"
        )


# ---------------------------------------------------------------------------
# Machine core
# ---------------------------------------------------------------------------

COIN_DENOMINATIONS: List[float] = [0.05, 0.10, 0.25, 0.50, 1.00]
BILL_DENOMINATIONS: List[float] = [1.00, 2.00, 5.00, 10.00, 20.00]
VALID_DENOMINATIONS: List[float] = sorted(
    set(COIN_DENOMINATIONS + BILL_DENOMINATIONS)
)

DEFAULT_CATALOG: List[Dict] = [
    {"name": "Marlboro Red",      "brand": "Marlboro",  "price": 12.50, "stock": 10},
    {"name": "Marlboro Gold",     "brand": "Marlboro",  "price": 12.50, "stock": 10},
    {"name": "Camel Blue",        "brand": "Camel",     "price": 11.00, "stock": 10},
    {"name": "Lucky Strike",      "brand": "Lucky Strike", "price": 10.50, "stock": 10},
    {"name": "Winston Red",       "brand": "Winston",   "price": 10.00, "stock": 10},
    {"name": "Newport Menthol",   "brand": "Newport",   "price": 11.50, "stock": 10},
]


class CigaretteVendingMachine:
    """Core logic of the digital cigarette vending machine."""

    # Default admin PIN – MUST be changed in any production/non-demo deployment.
    ADMIN_PIN: str = "1234"

    def __init__(
        self,
        catalog: Optional[List[Dict]] = None,
        admin_pin: Optional[str] = None,
    ) -> None:
        self._catalog: List[Product] = []
        raw = catalog if catalog is not None else DEFAULT_CATALOG
        for item in raw:
            self._catalog.append(
                Product(
                    name=item["name"],
                    brand=item["brand"],
                    price=item["price"],
                    stock=item["stock"],
                )
            )
        self._inserted_amount: float = 0.0
        self._sales_history: List[SaleRecord] = []
        self._age_verified: bool = False
        if admin_pin is not None:
            self.ADMIN_PIN = admin_pin

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def inserted_amount(self) -> float:
        """Total money currently inserted by the customer (in dollars)."""
        return self._inserted_amount

    @property
    def catalog(self) -> List[Product]:
        """Read-only view of the product catalog."""
        return list(self._catalog)

    @property
    def sales_history(self) -> List[SaleRecord]:
        """Read-only copy of all completed sale records."""
        return list(self._sales_history)

    # ------------------------------------------------------------------
    # Age verification
    # ------------------------------------------------------------------

    def verify_age(self, age: int) -> bool:
        """
        Verify that the customer is of legal age (18+).

        Returns True when age is 18 or older and sets the internal flag so
        further purchases in the same session are not blocked.

        **Simulation only** – this check relies entirely on the customer's
        self-reported age.  A production system must integrate with a hardware
        ID scanner or an external identity-verification service.
        """
        if age >= 18:
            self._age_verified = True
            return True
        self._age_verified = False
        return False

    # ------------------------------------------------------------------
    # Money handling
    # ------------------------------------------------------------------

    def insert_money(self, amount: float) -> float:
        """
        Insert *amount* dollars into the machine.

        Only accepts valid denominations.  Returns the new running total.
        Raises ValueError for invalid or non-positive amounts.
        """
        if amount <= 0:
            raise ValueError(f"Amount must be positive, got {amount}")
        rounded = round(amount, 2)
        if rounded not in VALID_DENOMINATIONS:
            raise ValueError(
                f"Invalid denomination ${amount:.2f}. "
                f"Accepted: {[f'${d:.2f}' for d in VALID_DENOMINATIONS]}"
            )
        self._inserted_amount = round(self._inserted_amount + rounded, 2)
        return self._inserted_amount

    def cancel_and_return(self) -> float:
        """Cancel the current transaction and return all inserted money."""
        refund = self._inserted_amount
        self._inserted_amount = 0.0
        return refund

    # ------------------------------------------------------------------
    # Browsing
    # ------------------------------------------------------------------

    def get_available_products(self) -> List[Tuple[int, Product]]:
        """Return list of (slot_number, product) tuples for in-stock items."""
        return [
            (i + 1, p) for i, p in enumerate(self._catalog) if p.is_available()
        ]

    def get_product_by_slot(self, slot: int) -> Optional[Product]:
        """Return the Product at *slot* (1-based) or None if invalid."""
        idx = slot - 1
        if 0 <= idx < len(self._catalog):
            return self._catalog[idx]
        return None

    # ------------------------------------------------------------------
    # Purchase flow
    # ------------------------------------------------------------------

    def purchase(self, slot: int) -> Tuple[bool, str, float]:
        """
        Attempt to purchase the product at *slot*.

        Returns a tuple of (success, message, change_amount).

        Possible outcomes
        -----------------
        - Age not verified → (False, age_message, 0.0)
        - Invalid slot      → (False, error_message, 0.0)
        - Out of stock      → (False, error_message, 0.0)
        - Insufficient funds→ (False, error_message, 0.0)
        - Success           → (True, success_message, change)
        """
        if not self._age_verified:
            return False, "Age verification required before purchase.", 0.0

        product = self.get_product_by_slot(slot)
        if product is None:
            return False, f"Invalid slot number: {slot}.", 0.0

        if not product.is_available():
            return False, f"'{product.name}' is out of stock.", 0.0

        if self._inserted_amount < product.price:
            shortfall = round(product.price - self._inserted_amount, 2)
            return (
                False,
                f"Insufficient funds. Please insert ${shortfall:.2f} more.",
                0.0,
            )

        change = round(self._inserted_amount - product.price, 2)
        product.dispense()
        self._sales_history.append(
            SaleRecord(product, self._inserted_amount, change)
        )
        self._inserted_amount = 0.0

        return (
            True,
            f"Dispensing '{product.name}'. Enjoy your purchase.",
            change,
        )

    # ------------------------------------------------------------------
    # Admin operations
    # ------------------------------------------------------------------

    def admin_authenticate(self, pin: str) -> bool:
        """Return True if *pin* matches the admin PIN (constant-time comparison)."""
        return secrets.compare_digest(pin, self.ADMIN_PIN)

    def admin_restock(self, slot: int, quantity: int) -> str:
        """
        Restock the product at *slot* by *quantity* units.
        Returns a status message.
        """
        product = self.get_product_by_slot(slot)
        if product is None:
            return f"Invalid slot number: {slot}."
        product.restock(quantity)
        return f"Restocked '{product.name}' by {quantity}. New stock: {product.stock}."

    def admin_sales_report(self) -> str:
        """Return a formatted sales report string."""
        if not self._sales_history:
            return "No sales recorded yet."
        lines = ["=== Sales Report ==="]
        total_revenue = 0.0
        for i, record in enumerate(self._sales_history, 1):
            lines.append(
                f"  {i}. {record.product_name} ({record.brand}) "
                f"- ${record.price:.2f} "
                f"[paid: ${record.amount_paid:.2f}, change: ${record.change:.2f}]"
            )
            total_revenue += record.price
        lines.append(f"Total Revenue: ${total_revenue:.2f}")
        lines.append(f"Total Transactions: {len(self._sales_history)}")
        return "\n".join(lines)

    def admin_inventory_report(self) -> str:
        """Return a formatted inventory report string."""
        lines = ["=== Inventory Report ==="]
        for i, p in enumerate(self._catalog, 1):
            status = "IN STOCK" if p.is_available() else "OUT OF STOCK"
            lines.append(
                f"  Slot {i}: {p.name} ({p.brand}) "
                f"- ${p.price:.2f} | Stock: {p.stock} [{status}]"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def _display_catalog(machine: CigaretteVendingMachine) -> None:
    print("\n--- Available Products ---")
    available = machine.get_available_products()
    if not available:
        print("  (No products currently available)")
        return
    for slot, product in available:
        print(f"  [{slot}] {product.name} ({product.brand}) - ${product.price:.2f}")
    print(f"\n  Inserted: ${machine.inserted_amount:.2f}")


def _age_gate(machine: CigaretteVendingMachine) -> bool:
    """Prompt for age verification. Returns True when verified."""
    print("\n--- Age Verification ---")
    print("You must be 18 or older to use this machine.")
    try:
        age = int(input("Please enter your age: ").strip())
    except (ValueError, EOFError):
        print("Invalid input. Session cancelled.")
        return False
    if machine.verify_age(age):
        print("Age verified. Welcome!")
        return True
    print("Sorry, you must be 18 or older to purchase cigarettes.")
    return False


def _customer_session(machine: CigaretteVendingMachine) -> None:
    """Run one complete customer session."""
    if not _age_gate(machine):
        return

    while True:
        print("\n=== Cigarette Vending Machine ===")
        print("  1. View products")
        print("  2. Insert money")
        print("  3. Select product")
        print("  4. Cancel / Return money")
        print("  5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            _display_catalog(machine)

        elif choice == "2":
            try:
                amount = float(input("Enter amount to insert (e.g. 10.00): $").strip())
                new_total = machine.insert_money(amount)
                print(f"Accepted. Total inserted: ${new_total:.2f}")
            except (ValueError, EOFError) as exc:
                print(f"Error: {exc}")

        elif choice == "3":
            _display_catalog(machine)
            try:
                slot = int(input("Enter slot number: ").strip())
                success, message, change = machine.purchase(slot)
                print(f"\n  {message}")
                if success and change > 0:
                    print(f"  Change returned: ${change:.2f}")
            except (ValueError, EOFError):
                print("Invalid input.")

        elif choice == "4":
            refund = machine.cancel_and_return()
            print(f"Transaction cancelled. ${refund:.2f} returned.")
            break

        elif choice == "5":
            refund = machine.cancel_and_return()
            if refund > 0:
                print(f"Returning ${refund:.2f}. Goodbye!")
            else:
                print("Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")


def _admin_session(machine: CigaretteVendingMachine) -> None:
    """Run an admin management session."""
    pin = input("Enter admin PIN: ").strip()
    if not machine.admin_authenticate(pin):
        print("Incorrect PIN. Access denied.")
        return

    print("Admin access granted.")
    while True:
        print("\n=== Admin Menu ===")
        print("  1. View inventory")
        print("  2. Restock product")
        print("  3. View sales report")
        print("  4. Exit admin menu")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            print(machine.admin_inventory_report())

        elif choice == "2":
            print(machine.admin_inventory_report())
            try:
                slot = int(input("Enter slot number to restock: ").strip())
                qty = int(input("Enter quantity to add: ").strip())
                msg = machine.admin_restock(slot, qty)
                print(msg)
            except (ValueError, EOFError):
                print("Invalid input.")

        elif choice == "3":
            print(machine.admin_sales_report())

        elif choice == "4":
            print("Exiting admin menu.")
            break

        else:
            print("Invalid option.")


def main() -> None:  # pragma: no cover
    """Entry point for the interactive digital cigarette vending machine."""
    machine = CigaretteVendingMachine()
    print("Welcome to the Digital Cigarette Vending Machine")

    while True:
        print("\n--- Main Menu ---")
        print("  1. Start customer session")
        print("  2. Admin access")
        print("  3. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            _customer_session(machine)

        elif choice == "2":
            _admin_session(machine)

        elif choice == "3":
            print("Machine shutting down. Goodbye!")
            sys.exit(0)

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
