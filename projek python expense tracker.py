"""
Expense Tracker App
Aplikasi pencatat pengeluaran sederhana berbasis CLI (Command Line Interface)
menggunakan Python murni (tanpa library eksternal) dan penyimpanan data ke file JSON.

Fitur:
1. Tambah pengeluaran (kategori, jumlah, tanggal, catatan)
2. Lihat semua pengeluaran
3. Edit pengeluaran
4. Hapus pengeluaran
5. Laporan total pengeluaran per kategori
6. Laporan total pengeluaran per bulan
7. Cari pengeluaran berdasarkan kategori
8. Data tersimpan otomatis ke file expenses.json
"""

import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"


class ExpenseTracker:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.expenses = self.load_data()

    # ------------------ Penyimpanan Data ------------------
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Peringatan: file data rusak, memulai dengan data kosong.")
                return []
        return []

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4, ensure_ascii=False)

    # ------------------ Operasi CRUD ------------------
    def generate_id(self):
        if not self.expenses:
            return 1
        return max(item["id"] for item in self.expenses) + 1

    def add_expense(self, category, amount, date, note=""):
        expense = {
            "id": self.generate_id(),
            "category": category,
            "amount": amount,
            "date": date,
            "note": note,
        }
        self.expenses.append(expense)
        self.save_data()
        return expense

    def get_all_expenses(self):
        return self.expenses

    def get_expense_by_id(self, expense_id):
        for item in self.expenses:
            if item["id"] == expense_id:
                return item
        return None

    def update_expense(self, expense_id, category=None, amount=None, date=None, note=None):
        item = self.get_expense_by_id(expense_id)
        if item is None:
            return False
        if category is not None:
            item["category"] = category
        if amount is not None:
            item["amount"] = amount
        if date is not None:
            item["date"] = date
        if note is not None:
            item["note"] = note
        self.save_data()
        return True

    def delete_expense(self, expense_id):
        item = self.get_expense_by_id(expense_id)
        if item is None:
            return False
        self.expenses.remove(item)
        self.save_data()
        return True

    # ------------------ Laporan ------------------
    def total_by_category(self):
        summary = {}
        for item in self.expenses:
            summary[item["category"]] = summary.get(item["category"], 0) + item["amount"]
        return summary

    def total_by_month(self):
        summary = {}
        for item in self.expenses:
            try:
                month_key = datetime.strptime(item["date"], "%Y-%m-%d").strftime("%Y-%m")
            except ValueError:
                month_key = "Tidak diketahui"
            summary[month_key] = summary.get(month_key, 0) + item["amount"]
        return summary

    def search_by_category(self, keyword):
        keyword = keyword.lower()
        return [item for item in self.expenses if keyword in item["category"].lower()]

    def total_all(self):
        return sum(item["amount"] for item in self.expenses)


# ------------------ Utility Tampilan ------------------
def format_rupiah(amount):
    return f"Rp{amount:,.0f}".replace(",", ".")


def print_expense_table(expenses):
    if not expenses:
        print("Tidak ada data pengeluaran.")
        return
    print(f"{'ID':<4}{'Tanggal':<12}{'Kategori':<15}{'Jumlah':<15}{'Catatan':<20}")
    print("-" * 66)
    for item in expenses:
        print(
            f"{item['id']:<4}{item['date']:<12}{item['category']:<15}"
            f"{format_rupiah(item['amount']):<15}{item.get('note', ''):<20}"
        )


def input_amount(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("Jumlah tidak boleh negatif.")
                continue
            return value
        except ValueError:
            print("Input tidak valid, masukkan angka.")


def input_date(prompt):
    while True:
        value = input(prompt).strip()
        if value == "":
            return datetime.today().strftime("%Y-%m-%d")
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Format tanggal salah. Gunakan YYYY-MM-DD, atau kosongkan untuk hari ini.")


# ------------------ Menu Program ------------------
def main_menu():
    tracker = ExpenseTracker()

    menu = """
=========================================
        EXPENSE TRACKER APP
=========================================
1. Tambah Pengeluaran
2. Lihat Semua Pengeluaran
3. Edit Pengeluaran
4. Hapus Pengeluaran
5. Laporan per Kategori
6. Laporan per Bulan
7. Cari Pengeluaran (per Kategori)
8. Total Keseluruhan
0. Keluar
=========================================
"""

    while True:
        print(menu)
        choice = input("Pilih menu: ").strip()

        if choice == "1":
            category = input("Kategori (misal: Makanan, Transport, dll): ").strip()
            amount = input_amount("Jumlah pengeluaran: ")
            date = input_date("Tanggal (YYYY-MM-DD, kosongkan = hari ini): ")
            note = input("Catatan (opsional): ").strip()
            expense = tracker.add_expense(category, amount, date, note)
            print(f"Pengeluaran berhasil ditambahkan dengan ID {expense['id']}.")

        elif choice == "2":
            print("\nDaftar Semua Pengeluaran:")
            print_expense_table(tracker.get_all_expenses())

        elif choice == "3":
            try:
                expense_id = int(input("Masukkan ID pengeluaran yang ingin diedit: "))
            except ValueError:
                print("ID tidak valid.")
                continue
            item = tracker.get_expense_by_id(expense_id)
            if item is None:
                print("Data dengan ID tersebut tidak ditemukan.")
                continue
            print("Kosongkan input jika tidak ingin mengubah field tersebut.")
            category = input(f"Kategori baru [{item['category']}]: ").strip()
            amount_str = input(f"Jumlah baru [{item['amount']}]: ").strip()
            date = input(f"Tanggal baru [{item['date']}]: ").strip()
            note = input(f"Catatan baru [{item.get('note', '')}]: ").strip()

            amount = float(amount_str) if amount_str else None
            success = tracker.update_expense(
                expense_id,
                category=category or None,
                amount=amount,
                date=date or None,
                note=note or None,
            )
            print("Data berhasil diperbarui." if success else "Gagal memperbarui data.")

        elif choice == "4":
            try:
                expense_id = int(input("Masukkan ID pengeluaran yang ingin dihapus: "))
            except ValueError:
                print("ID tidak valid.")
                continue
            confirm = input(f"Yakin ingin menghapus data ID {expense_id}? (y/n): ").strip().lower()
            if confirm == "y":
                success = tracker.delete_expense(expense_id)
                print("Data berhasil dihapus." if success else "Data tidak ditemukan.")
            else:
                print("Penghapusan dibatalkan.")

        elif choice == "5":
            summary = tracker.total_by_category()
            if not summary:
                print("Belum ada data.")
            else:
                print("\nTotal Pengeluaran per Kategori:")
                for category, total in sorted(summary.items(), key=lambda x: -x[1]):
                    print(f"- {category:<15}: {format_rupiah(total)}")

        elif choice == "6":
            summary = tracker.total_by_month()
            if not summary:
                print("Belum ada data.")
            else:
                print("\nTotal Pengeluaran per Bulan:")
                for month, total in sorted(summary.items()):
                    print(f"- {month:<10}: {format_rupiah(total)}")

        elif choice == "7":
            keyword = input("Masukkan kata kunci kategori: ").strip()
            results = tracker.search_by_category(keyword)
            print(f"\nHasil pencarian untuk '{keyword}':")
            print_expense_table(results)

        elif choice == "8":
            total = tracker.total_all()
            print(f"\nTotal keseluruhan pengeluaran: {format_rupiah(total)}")

        elif choice == "0":
            print("Terima kasih telah menggunakan Expense Tracker App. Sampai jumpa!")
            break

        else:
            print("Pilihan tidak valid, silakan coba lagi.")


if __name__ == "__main__":
    main_menu()
