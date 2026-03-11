"""
Unit tests for the Digital Cigarette Vending Machine.
"""

import pytest
from cigarette_vending_machine import (
    CigaretteVendingMachine,
    Product,
    SaleRecord,
    VALID_DENOMINATIONS,
)


# ---------------------------------------------------------------------------
# Product tests
# ---------------------------------------------------------------------------

class TestProduct:
    def test_creation(self):
        p = Product("Marlboro Red", "Marlboro", 12.50, 10)
        assert p.name == "Marlboro Red"
        assert p.brand == "Marlboro"
        assert p.price == 12.50
        assert p.stock == 10

    def test_is_available_when_in_stock(self):
        p = Product("Test", "Brand", 5.00, 3)
        assert p.is_available() is True

    def test_is_not_available_when_out_of_stock(self):
        p = Product("Test", "Brand", 5.00, 0)
        assert p.is_available() is False

    def test_restock_increases_stock(self):
        p = Product("Test", "Brand", 5.00, 2)
        p.restock(5)
        assert p.stock == 7

    def test_restock_zero_or_negative_raises(self):
        p = Product("Test", "Brand", 5.00, 2)
        with pytest.raises(ValueError):
            p.restock(0)
        with pytest.raises(ValueError):
            p.restock(-1)

    def test_dispense_decrements_stock(self):
        p = Product("Test", "Brand", 5.00, 3)
        p.dispense()
        assert p.stock == 2

    def test_dispense_out_of_stock_raises(self):
        p = Product("Test", "Brand", 5.00, 0)
        with pytest.raises(RuntimeError):
            p.dispense()

    def test_negative_price_raises(self):
        with pytest.raises(ValueError):
            Product("Test", "Brand", -1.00, 5)

    def test_negative_stock_raises(self):
        with pytest.raises(ValueError):
            Product("Test", "Brand", 5.00, -1)


# ---------------------------------------------------------------------------
# CigaretteVendingMachine – age verification
# ---------------------------------------------------------------------------

class TestAgeVerification:
    def setup_method(self):
        self.machine = CigaretteVendingMachine()

    def test_adult_age_verified(self):
        assert self.machine.verify_age(18) is True
        assert self.machine._age_verified is True

    def test_adult_age_above_threshold(self):
        assert self.machine.verify_age(25) is True

    def test_minor_age_rejected(self):
        assert self.machine.verify_age(17) is False
        assert self.machine._age_verified is False

    def test_zero_age_rejected(self):
        assert self.machine.verify_age(0) is False


# ---------------------------------------------------------------------------
# CigaretteVendingMachine – money handling
# ---------------------------------------------------------------------------

class TestMoneyHandling:
    def setup_method(self):
        self.machine = CigaretteVendingMachine()

    def test_insert_valid_denomination(self):
        total = self.machine.insert_money(10.00)
        assert total == 10.00

    def test_insert_accumulates(self):
        self.machine.insert_money(5.00)
        self.machine.insert_money(5.00)
        assert self.machine.inserted_amount == 10.00

    def test_insert_invalid_denomination_raises(self):
        with pytest.raises(ValueError, match="Invalid denomination"):
            self.machine.insert_money(3.00)

    def test_insert_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            self.machine.insert_money(-1.00)

    def test_insert_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            self.machine.insert_money(0)

    def test_cancel_returns_all_money(self):
        self.machine.insert_money(10.00)
        self.machine.insert_money(5.00)
        refund = self.machine.cancel_and_return()
        assert refund == 15.00
        assert self.machine.inserted_amount == 0.0

    def test_cancel_with_no_money_inserted(self):
        refund = self.machine.cancel_and_return()
        assert refund == 0.0

    def test_all_valid_denominations_accepted(self):
        for denom in VALID_DENOMINATIONS:
            m = CigaretteVendingMachine()
            total = m.insert_money(denom)
            assert total == pytest.approx(denom)


# ---------------------------------------------------------------------------
# CigaretteVendingMachine – purchase flow
# ---------------------------------------------------------------------------

CATALOG = [
    {"name": "TestBrand A", "brand": "BrandA", "price": 10.00, "stock": 2},
    {"name": "TestBrand B", "brand": "BrandB", "price": 5.00,  "stock": 0},
]


class TestPurchase:
    def setup_method(self):
        self.machine = CigaretteVendingMachine(catalog=CATALOG)

    def _verify_adult(self):
        self.machine.verify_age(21)

    def test_purchase_requires_age_verification(self):
        self.machine.insert_money(10.00)
        success, msg, change = self.machine.purchase(1)
        assert success is False
        assert "Age verification" in msg

    def test_purchase_invalid_slot(self):
        self._verify_adult()
        self.machine.insert_money(10.00)
        success, msg, change = self.machine.purchase(99)
        assert success is False
        assert "Invalid slot" in msg

    def test_purchase_out_of_stock(self):
        self._verify_adult()
        self.machine.insert_money(10.00)
        success, msg, change = self.machine.purchase(2)  # stock=0
        assert success is False
        assert "out of stock" in msg

    def test_purchase_insufficient_funds(self):
        self._verify_adult()
        self.machine.insert_money(5.00)
        success, msg, change = self.machine.purchase(1)  # costs 10.00
        assert success is False
        assert "Insufficient funds" in msg
        assert change == 0.0
        # money should NOT have been consumed
        assert self.machine.inserted_amount == 5.00

    def test_purchase_exact_amount(self):
        self._verify_adult()
        self.machine.insert_money(10.00)
        success, msg, change = self.machine.purchase(1)
        assert success is True
        assert change == 0.0
        assert self.machine.inserted_amount == 0.0

    def test_purchase_with_change(self):
        self._verify_adult()
        self.machine.insert_money(20.00)
        success, msg, change = self.machine.purchase(1)  # costs 10.00
        assert success is True
        assert change == pytest.approx(10.00)
        assert self.machine.inserted_amount == 0.0

    def test_purchase_reduces_stock(self):
        self._verify_adult()
        self.machine.insert_money(10.00)
        self.machine.purchase(1)
        product = self.machine.get_product_by_slot(1)
        assert product.stock == 1

    def test_purchase_records_sale(self):
        self._verify_adult()
        self.machine.insert_money(10.00)
        self.machine.purchase(1)
        assert len(self.machine.sales_history) == 1
        record = self.machine.sales_history[0]
        assert record.product_name == "TestBrand A"
        assert record.price == 10.00
        assert record.change == 0.0

    def test_purchase_until_out_of_stock(self):
        self._verify_adult()
        # stock=2, buy twice
        for _ in range(2):
            self.machine.insert_money(10.00)
            success, _, _ = self.machine.purchase(1)
            assert success is True
        # third attempt should fail
        self.machine.insert_money(10.00)
        success, msg, _ = self.machine.purchase(1)
        assert success is False
        assert "out of stock" in msg

    def test_purchase_change_exact_precision(self):
        """Ensure floating-point rounding doesn't produce nonsense change."""
        machine = CigaretteVendingMachine(
            catalog=[{"name": "X", "brand": "B", "price": 10.50, "stock": 1}]
        )
        machine.verify_age(21)
        machine.insert_money(20.00)
        success, _, change = machine.purchase(1)
        assert success is True
        assert change == pytest.approx(9.50)


# ---------------------------------------------------------------------------
# CigaretteVendingMachine – catalog helpers
# ---------------------------------------------------------------------------

class TestCatalogHelpers:
    def setup_method(self):
        self.machine = CigaretteVendingMachine(catalog=CATALOG)

    def test_get_available_products_excludes_out_of_stock(self):
        available = self.machine.get_available_products()
        slots = [slot for slot, _ in available]
        assert 1 in slots
        assert 2 not in slots  # stock=0

    def test_get_product_by_valid_slot(self):
        product = self.machine.get_product_by_slot(1)
        assert product is not None
        assert product.name == "TestBrand A"

    def test_get_product_by_invalid_slot(self):
        assert self.machine.get_product_by_slot(0) is None
        assert self.machine.get_product_by_slot(99) is None

    def test_catalog_property_returns_copy(self):
        catalog = self.machine.catalog
        catalog.clear()
        assert len(self.machine.catalog) == 2  # original unaffected


# ---------------------------------------------------------------------------
# CigaretteVendingMachine – admin operations
# ---------------------------------------------------------------------------

class TestAdminOperations:
    def setup_method(self):
        self.machine = CigaretteVendingMachine(catalog=CATALOG, admin_pin="9999")

    def test_authenticate_correct_pin(self):
        assert self.machine.admin_authenticate("9999") is True

    def test_authenticate_wrong_pin(self):
        assert self.machine.admin_authenticate("0000") is False

    def test_restock_valid_slot(self):
        msg = self.machine.admin_restock(2, 5)
        assert "Restocked" in msg
        assert self.machine.get_product_by_slot(2).stock == 5

    def test_restock_invalid_slot(self):
        msg = self.machine.admin_restock(99, 5)
        assert "Invalid slot" in msg

    def test_inventory_report_contains_all_products(self):
        report = self.machine.admin_inventory_report()
        assert "TestBrand A" in report
        assert "TestBrand B" in report
        assert "OUT OF STOCK" in report
        assert "IN STOCK" in report

    def test_sales_report_empty(self):
        report = self.machine.admin_sales_report()
        assert "No sales" in report

    def test_sales_report_after_purchase(self):
        self.machine.verify_age(21)
        self.machine.insert_money(10.00)
        self.machine.purchase(1)
        report = self.machine.admin_sales_report()
        assert "TestBrand A" in report
        assert "Total Revenue" in report
        assert "Total Transactions: 1" in report


# ---------------------------------------------------------------------------
# Default catalog smoke test
# ---------------------------------------------------------------------------

class TestDefaultCatalog:
    def test_default_catalog_has_products(self):
        machine = CigaretteVendingMachine()
        assert len(machine.catalog) > 0

    def test_default_catalog_all_in_stock(self):
        machine = CigaretteVendingMachine()
        for product in machine.catalog:
            assert product.is_available()

    def test_full_purchase_flow_default_catalog(self):
        machine = CigaretteVendingMachine()
        machine.verify_age(21)
        machine.insert_money(20.00)
        success, msg, change = machine.purchase(1)
        assert success is True
        assert "Dispensing" in msg
