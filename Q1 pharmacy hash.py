"""
Question 1: Hashing - Pharmacy Inventory Management System

Data is loaded from and saved to 'Medicines.txt'
============================================================
"""

import time
import os


# =============================================================================
# SECTION 1: Entity Class - Medicine
# =============================================================================

class Medicine:
    """
    Entity class representing a pharmacy product (Medicine).

    Attributes:
        medicine_id (str)  : Unique identifier / key for hashing (e.g. "MED001")
        name        (str)  : Name of the medicine
        category    (str)  : Category  (Tablet / Syrup / Supplement / Capsule)
        price       (float): Price per unit in MYR
        quantity    (int)  : Current stock quantity
        expiry_date (str)  : Expiry date in DD/MM/YYYY format
    """

    def __init__(self, medicine_id: str, name: str, category: str,
                 price: float, quantity: int, expiry_date: str):
        self.medicine_id = medicine_id   # str   – used as hash key
        self.name        = name          # str   – product name
        self.category    = category      # str   – Tablet/Syrup/Supplement/Capsule
        self.price       = price         # float – price in MYR
        self.quantity    = quantity      # int   – stock level
        self.expiry_date = expiry_date   # str   – DD/MM/YYYY

    def to_file_line(self) -> str:
        """Serialise to a single pipe-delimited line for writing to file."""
        return (f"{self.medicine_id}|{self.name}|{self.category}|"
                f"{self.price:.2f}|{self.quantity}|{self.expiry_date}")

    @staticmethod
    def from_file_line(line: str):
        """
        Deserialise a pipe-delimited line back into a Medicine object.
        Returns None if the line is malformed.
        """
        line = line.strip()
        if not line or line.startswith("#"):
            return None
        parts = line.split("|")
        if len(parts) != 6:
            return None
        try:
            mid, name, cat, price, qty, expiry = parts
            return Medicine(mid.strip(), name.strip(), cat.strip(),
                            float(price), int(qty), expiry.strip())
        except ValueError:
            return None

    def __str__(self):
        return (f"[{self.medicine_id}] {self.name:<28} | "
                f"Category: {self.category:<12} | "
                f"Price: RM{self.price:>7.2f} | "
                f"Qty: {self.quantity:>4} | "
                f"Expiry: {self.expiry_date}")

    def __repr__(self):
        return f"Medicine({self.medicine_id!r}, {self.name!r})"


# =============================================================================
# SECTION 2: File I/O helpers
# =============================================================================

DATA_FILE = "medicines.txt"

FILE_HEADER = (
    "# PharmaCare Inventory Data File\n"
    "# Format: medicine_id|name|category|price|quantity|expiry_date\n"
    "# Do NOT edit medicine_id as it is the hash key.\n"
)


def load_from_file(filepath: str = DATA_FILE) -> list:
    """
    Read all Medicine records from the data file.
    Skips blank lines and comment lines (starting with '#').
    Returns a list of Medicine objects.
    """
    medicines = []
    if not os.path.exists(filepath):
        print(f"  [INFO] Data file '{filepath}' not found. Starting with empty inventory.")
        return medicines
    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            med = Medicine.from_file_line(line)
            if med is not None:
                medicines.append(med)
            elif line.strip() and not line.strip().startswith("#"):
                print(f"  [WARNING] Skipping malformed line {line_no}: {line.strip()!r}")
    return medicines


def save_to_file(hash_table, filepath: str = DATA_FILE):
    """
    Write all active Medicine records from the hash table back to the data file, preserving the comment header.
    Overwrites the file completely to reflect deletions and edits.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(FILE_HEADER)
        for bucket in hash_table._buckets:
            if bucket is not None and bucket != HashTable.DELETED:
                f.write(bucket.to_file_line() + "\n")


# =============================================================================
# SECTION 3: Hash Table with Linear Probing
# =============================================================================

class HashTable:
    """
    Hash Table using Open Addressing with Linear Probing.

    Bucket structure: A fixed-size Python list (array) of Medicine objects
    (or None for empty slots, DELETED sentinel for lazily-deleted slots).

    Choice rationale:
      - Array-based buckets give O(1) index access and excellent cache locality.
      - No extra pointer overhead unlike a linked-list per bucket.
      - Linear probing keeps data contiguous in memory, maximising CPU cache hits.
      - Simple implementation with predictable behaviour.
    """

    DELETED = "__DELETED__"

    def __init__(self, size: int = 17):
        """
        Initialise the hash table.
        Size is a prime number to reduce clustering in linear-probing tables.
        """
        self._size    = size
        self._buckets = [None] * size   # Core array: Medicine | None | DELETED
        self._count   = 0

    # ------------------------------------------------------------------
    # Hash Function
    # ------------------------------------------------------------------

    def _hash(self, key: str) -> int:
        """
        Polynomial rolling hash mapped to table size.
        Converts each character to its ASCII value, accumulates with a
        prime multiplier (31), then takes modulo table size.
        Time complexity: O(k) where k = len(key).
        """
        hash_value = 0
        prime = 31
        for char in key:
            hash_value = (hash_value * prime + ord(char)) % self._size
        return hash_value

    # ------------------------------------------------------------------
    # Core Operations
    # ------------------------------------------------------------------

    def insert(self, medicine: Medicine) -> bool:
        """
        Insert a Medicine object using linear probing on collision.
        Returns False if table is full or duplicate key exists.
        Time complexity: O(1) average, O(n) worst case.
        """
        if self._count >= self._size:
            print("  [ERROR] Hash table is full.")
            return False

        key   = medicine.medicine_id
        index = self._hash(key)

        first_deleted = None
        for i in range(self._size):
            probe = (index + i) % self._size

            if self._buckets[probe] is None:
                target = first_deleted if first_deleted is not None else probe
                self._buckets[target] = medicine
                self._count += 1
                return True

            elif self._buckets[probe] == self.DELETED:
                if first_deleted is None:
                    first_deleted = probe

            elif self._buckets[probe].medicine_id == key:
                print(f"  [WARNING] Duplicate key '{key}'. Use edit to update.")
                return False

        if first_deleted is not None:
            self._buckets[first_deleted] = medicine
            self._count += 1
            return True

        print("  [ERROR] Hash table is full (all slots occupied/deleted).")
        return False

    def search(self, medicine_id: str):
        """
        Search for a Medicine by its ID using linear probing.
        Returns (Medicine, probes) or (None, probes) if not found.
        Time complexity: O(1) average, O(n) worst case.
        """
        index  = self._hash(medicine_id)
        probes = 0

        for i in range(self._size):
            probe = (index + i) % self._size
            probes += 1

            if self._buckets[probe] is None:
                return None, probes
            elif self._buckets[probe] == self.DELETED:
                continue
            elif self._buckets[probe].medicine_id == medicine_id:
                return self._buckets[probe], probes

        return None, probes

    def delete(self, medicine_id: str) -> bool:
        """
        Delete a record via lazy deletion (mark bucket as DELETED sentinel).
        Returns True if found and deleted, False otherwise.
        """
        index = self._hash(medicine_id)
        for i in range(self._size):
            probe = (index + i) % self._size
            if self._buckets[probe] is None:
                return False
            elif self._buckets[probe] == self.DELETED:
                continue
            elif self._buckets[probe].medicine_id == medicine_id:
                self._buckets[probe] = self.DELETED
                self._count -= 1
                return True
        return False

    def update(self, medicine_id: str, **kwargs) -> bool:
        """Update fields of an existing Medicine record in-place."""
        record, _ = self.search(medicine_id)
        if record is None:
            return False
        for field, value in kwargs.items():
            if hasattr(record, field) and field != "medicine_id":
                setattr(record, field, value)
        return True

    def get_all_records(self) -> list:
        """Return a list of all active Medicine objects."""
        return [b for b in self._buckets
                if b is not None and b != self.DELETED]

    def display_all(self):
        """Print all active records with their bucket index."""
        print(f"\n  {'Index':>5}  {'Medicine ID':<10}  {'Details'}")
        print("  " + "-" * 95)
        found = False
        for i, bucket in enumerate(self._buckets):
            if bucket is not None and bucket != self.DELETED:
                print(f"  [{i:>2}]  {bucket}")
                found = True
        if not found:
            print("  (No records found)")
        print(f"\n  Total records: {self._count} / {self._size} buckets used  "
              f"(load factor = {self.load_factor:.2f})")

    def display_raw(self):
        """Show every bucket including None and DELETED – useful for debugging."""
        print(f"\n  {'Idx':>4}  {'Status':<10}  {'Content'}")
        print("  " + "-" * 80)
        for i, bucket in enumerate(self._buckets):
            if bucket is None:
                print(f"  [{i:>2}]  {'EMPTY':<10}  ---")
            elif bucket == self.DELETED:
                print(f"  [{i:>2}]  {'DELETED':<10}  ---")
            else:
                print(f"  [{i:>2}]  {'OCCUPIED':<10}  {bucket}")

    # Choose a new prime size large enough to hold all records
    def resize_if_needed(self, extra: int = 10) -> 'HashTable':
        """
        Return a new HashTable with a larger prime size if load factor > 0.75.
        Caller is responsible for replacing the old table reference.
        """
        if self.load_factor <= 0.75:
            return self
        new_size = _next_prime(self._size * 2)
        new_ht   = HashTable(size=new_size)
        for med in self.get_all_records():
            new_ht.insert(med)
        print(f"  [INFO] Hash table resized: {self._size} -> {new_size} buckets.")
        return new_ht

    @property
    def size(self):
        return self._size

    @property
    def count(self):
        return self._count

    @property
    def load_factor(self):
        return self._count / self._size


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def _next_prime(n: int) -> int:
    """Return the smallest prime >= n."""
    while not _is_prime(n):
        n += 1
    return n


# =============================================================================
# SECTION 4: Performance Comparison – Hash Table vs Array
# =============================================================================

def linear_search_array(array: list, medicine_id: str):
    """
    Linear search through a plain Python list.
    Time complexity: O(n).
    Returns (Medicine | None, comparisons_made).
    """
    comparisons = 0
    for item in array:
        comparisons += 1
        if item.medicine_id == medicine_id:
            return item, comparisons
    return None, comparisons


def run_performance_comparison(hash_table: HashTable, array: list,
                                search_keys: list):
    """
    Compare search performance between the Hash Table and a 1-D array.
    Each search is repeated REPEAT times for stable nanosecond timing.
    Tests both existing and non-existing keys.
    """
    REPEAT = 1_000

    print("\n" + "=" * 97)
    print("  PERFORMANCE COMPARISON: Hash Table (Linear Probing)  vs  1-D Array (Linear Search)")
    print("=" * 97)
    print(f"  Dataset size : {hash_table.count} records")
    print(f"  Table size   : {hash_table.size} buckets  |  Load factor = {hash_table.load_factor:.2f}")
    print(f"  Array size   : {len(array)} elements")
    print(f"  Each search repeated {REPEAT:,} times for stable timing.")
    print("-" * 97)

    ht_total_ns  = 0
    arr_total_ns = 0

    print(f"\n  {'Key':<12} {'Exists':<8} {'HT Avg (ns)':>13} {'HT Probes':>11}"
          f" {'Array Avg (ns)':>15} {'Array Cmps':>12}")
    print("  " + "-" * 75)

    for key in search_keys:
        # Hash Table timing
        t0 = time.perf_counter_ns()
        for _ in range(REPEAT):
            result_ht, probes = hash_table.search(key)
        t1 = time.perf_counter_ns()
        ht_ns = (t1 - t0) // REPEAT

        # Array timing
        t2 = time.perf_counter_ns()
        for _ in range(REPEAT):
            result_arr, cmps = linear_search_array(array, key)
        t3 = time.perf_counter_ns()
        arr_ns = (t3 - t2) // REPEAT

        exists = "YES" if result_ht is not None else "NO"
        print(f"  {key:<12} {exists:<8} {ht_ns:>13,} {probes:>11}"
              f" {arr_ns:>15,} {cmps:>12}")

        ht_total_ns  += ht_ns
        arr_total_ns += arr_ns

    n = len(search_keys)
    print("  " + "-" * 75)
    print(f"  {'TOTAL':<20} {ht_total_ns:>13,} {'':>11} {arr_total_ns:>15,}")
    print(f"  {'AVERAGE':<20} {ht_total_ns // n:>13,} {'':>11} {arr_total_ns // n:>15,}")

    if ht_total_ns > 0:
        speedup = arr_total_ns / ht_total_ns
        winner  = "Hash Table" if speedup > 1 else "Array"
        print(f"\n  Speed-up factor (Array time / HT time) = {speedup:.2f}x  →  {winner} is faster overall")

    print("\n  ANALYSIS:")
    print("  ─────────")
    print("  • Hash Table uses a hash function to directly compute the target bucket,")
    print("    achieving O(1) average-case lookup regardless of dataset size.")
    print("  • Linear Probing adds a small overhead on collision, but with a low load")
    print(f"    factor ({hash_table.load_factor:.2f}), the expected number of probes per search stays small.")
    print("  • 1-D Array Linear Search scans from index 0 toward the target — O(n).")
    print("    For NON-EXISTING keys it must traverse every element (worst case).")
    print("  • As dataset grows, the Hash Table advantage widens dramatically:")
    print("    n=100 → array averages 50 comparisons; hash table averages ~1-2 probes.")
    print("  CONCLUSION: Hash Table (Linear Probing) is the superior structure for")
    print("  lookup-heavy workloads, especially as inventory size scales up.")
    print("=" * 97)


# =============================================================================
# SECTION 5: Command-Line Interface
# =============================================================================

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    print("\n" + "=" * 65)
    print("       🏥  PharmaCare – Inventory Management System  🏥")
    print("       Hash Table (Linear Probing) | Data: medicines.txt")
    print("=" * 65)


def menu():
    print("\n  ┌─────────────────────────────────────┐")
    print("  │          MAIN MENU                  │")
    print("  ├─────────────────────────────────────┤")
    print("  │  1. Display All Medicines           │")
    print("  │  2. Insert New Medicine             │")
    print("  │  3. Search Medicine by ID           │")
    print("  │  4. Edit Medicine Record            │")
    print("  │  5. Delete Medicine Record          │")
    print("  │  6. View Raw Hash Table Buckets     │")
    print("  │  7. Performance Comparison          │")
    print("  │  0. Exit                            │")
    print("  └─────────────────────────────────────┘")
    return input("  Enter choice: ").strip()


def prompt_new_medicine() -> Medicine:
    print("\n  --- Add New Medicine ---")
    mid    = input("  Medicine ID  (e.g. MED016): ").strip().upper()
    name   = input("  Name                      : ").strip()
    cat    = input("  Category (Tablet/Syrup/Supplement/Capsule): ").strip().title()
    price  = float(input("  Price (RM)                : "))
    qty    = int(input("  Quantity                  : "))
    expiry = input("  Expiry Date (DD/MM/YYYY)  : ").strip()
    return Medicine(mid, name, cat, price, qty, expiry)


def build_hash_table(medicines: list) -> HashTable:
    """
    Build a hash table sized to a prime at least 2× the record count
    so the load factor starts around 0.5 and there is room for growth.
    """
    min_size = max(17, _next_prime(len(medicines) * 2 + 1))
    ht = HashTable(size=min_size)
    for med in medicines:
        ht.insert(med)
    return ht


def run_cli():
    print_header()

    # ── Load records from file ────────────────────────────────────────
    print(f"\n  Loading records from '{DATA_FILE}'...")
    medicines = load_from_file(DATA_FILE)

    if not medicines:
        print("  (No records loaded. Add medicines via option 2.)")
    else:
        print(f"  {len(medicines)} record(s) loaded successfully.")

    # ── Build hash table ──────────────────────────────────────────────
    ht = build_hash_table(medicines)
    print(f"  Hash table initialised: size={ht.size}, "
          f"records={ht.count}, load={ht.load_factor:.2f}")

    input("\n  Press ENTER to enter the main menu...")

    while True:
        print_header()
        choice = menu()

        # ── 1. Display All ────────────────────────────────────────────
        if choice == "1":
            print_header()
            ht.display_all()
            input("\n  Press ENTER to continue...")

        # ── 2. Insert ─────────────────────────────────────────────────
        elif choice == "2":
            try:
                new_med = prompt_new_medicine()
                if ht.insert(new_med):
                    save_to_file(ht, DATA_FILE)   # persist immediately
                    print(f"\n  ✔ '{new_med.name}' inserted at bucket "
                          f"{ht._hash(new_med.medicine_id)}.")
                    print(f"  ✔ Data file '{DATA_FILE}' updated.")
                    # Resize if load factor gets too high
                    ht = ht.resize_if_needed()
                else:
                    print("  ✘ Insertion failed (duplicate key or table full).")
            except ValueError:
                print("  ✘ Invalid input. Please enter the correct data types.")
            input("\n  Press ENTER to continue...")

        # ── 3. Search ─────────────────────────────────────────────────
        elif choice == "3":
            sid = input("\n  Enter Medicine ID to search: ").strip().upper()
            result, probes = ht.search(sid)
            if result:
                print(f"\n  ✔ Found after {probes} probe(s):")
                print(f"    {result}")
            else:
                print(f"\n  ✘ Medicine ID '{sid}' not found "
                      f"(probed {probes} bucket(s)).")
            input("\n  Press ENTER to continue...")

        # ── 4. Edit ───────────────────────────────────────────────────
        elif choice == "4":
            eid = input("\n  Enter Medicine ID to edit: ").strip().upper()
            rec, _ = ht.search(eid)
            if rec is None:
                print(f"  ✘ Medicine ID '{eid}' not found.")
            else:
                print(f"\n  Current: {rec}")
                print("  Which field to update?")
                print("  [1] Name  [2] Category  [3] Price  "
                      "[4] Quantity  [5] Expiry Date")
                fchoice  = input("  Choice: ").strip()
                field_map = {"1": "name", "2": "category", "3": "price",
                             "4": "quantity", "5": "expiry_date"}
                if fchoice in field_map:
                    field = field_map[fchoice]
                    nval  = input(f"  New value for '{field}': ").strip()
                    if field == "price":
                        nval = float(nval)
                    elif field == "quantity":
                        nval = int(nval)
                    ht.update(eid, **{field: nval})
                    save_to_file(ht, DATA_FILE)   # persist change
                    print(f"  ✔ Record updated and saved to '{DATA_FILE}'.")
                else:
                    print("  ✘ Invalid field choice.")
            input("\n  Press ENTER to continue...")

        # ── 5. Delete ─────────────────────────────────────────────────
        elif choice == "5":
            did = input("\n  Enter Medicine ID to delete: ").strip().upper()
            if ht.delete(did):
                save_to_file(ht, DATA_FILE)   # persist deletion
                print(f"  ✔ Medicine '{did}' deleted.")
                print(f"  ✔ Data file '{DATA_FILE}' updated.")
            else:
                print(f"  ✘ Medicine ID '{did}' not found.")
            input("\n  Press ENTER to continue...")

        # ── 6. Raw Buckets ────────────────────────────────────────────
        elif choice == "6":
            print_header()
            ht.display_raw()
            input("\n  Press ENTER to continue...")

        # ── 7. Performance Comparison ─────────────────────────────────
        elif choice == "7":
            all_ids    = [m.medicine_id for m in ht.get_all_records()]
            # Pick up to 5 existing + 3 non-existing keys
            existing   = all_ids[:5] if len(all_ids) >= 5 else all_ids
            nonexist   = ["MED099", "MED050", "MED020"]
            test_keys  = existing + nonexist
            arr_copy   = ht.get_all_records()          # flat list for comparison
            run_performance_comparison(ht, arr_copy, test_keys)
            input("\n  Press ENTER to continue...")

        # ── 0. Exit ───────────────────────────────────────────────────
        elif choice == "0":
            print(f"\n  All data is stored in '{DATA_FILE}'.")
            print("  Thank you for using PharmaCare. Goodbye! 👋\n")
            break

        else:
            print("  ✘ Invalid choice. Please try again.")
            input("\n  Press ENTER to continue...")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    run_cli()