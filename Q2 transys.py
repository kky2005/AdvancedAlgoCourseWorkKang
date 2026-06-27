"""
Question 2: Divide and Conquer — Transaction Management System

  - Transaction  : Entity class for a customer transaction
  - SortSearch   : Merge Sort, Binary Search, Linear Search algorithms
  - TranSys      : Driver program / CLI

Data is loaded from and saved to 'transactions.txt'
"""


class Transaction:
    """
    Represents a single customer transaction.

    Attributes:
        transaction_id   (int)  : Unique numeric identifier — primary sort/search key
        customer_name    (str)  : Full name of the customer
        product_name     (str)  : Name of the purchased product
        amount           (float): Total transaction amount in MYR
        transaction_date (str)  : Date of transaction in DD/MM/YYYY format
    """

    def __init__(self, transaction_id: int, customer_name: str,
                 product_name: str, amount: float, transaction_date: str):
        self.transaction_id   = transaction_id    # int   – primary sort/search key
        self.customer_name    = customer_name     # str   – buyer's full name
        self.product_name     = product_name      # str   – item purchased
        self.amount           = amount            # float – total cost in MYR
        self.transaction_date = transaction_date  # str   – DD/MM/YYYY

    def __str__(self):
        return (f"  ID: {self.transaction_id:<6} | "
                f"Customer: {self.customer_name:<18} | "
                f"Product: {self.product_name:<30} | "
                f"Amount: RM{self.amount:>8.2f} | "
                f"Date: {self.transaction_date}")

    def __repr__(self):
        return f"Transaction({self.transaction_id}, {self.customer_name!r})"

    def to_file_line(self) -> str:
        """Serialise to a pipe-delimited line for writing to transactions.txt."""
        return (f"{self.transaction_id}|{self.customer_name}|{self.product_name}|"
                f"{self.amount:.2f}|{self.transaction_date}")

    @staticmethod
    def from_file_line(line: str):
        """
        Parse a pipe-delimited line into a Transaction object.
        Returns None for blank lines, comments, or malformed lines.
        """
        line = line.strip()
        if not line or line.startswith("#"):
            return None
        parts = line.split("|")
        if len(parts) != 5:
            return None
        try:
            tid, cname, pname, amount, date = parts
            return Transaction(int(tid.strip()), cname.strip(), pname.strip(),
                               float(amount), date.strip())
        except ValueError:
            return None


# =============================================================================
# FILE I/O — load from and save to transactions.txt
# =============================================================================

DATA_FILE = "transactions.txt"

FILE_HEADER = (
    "# TranSys Transaction Data File\n"
    "# Format: transaction_id|customer_name|product_name|amount|transaction_date\n"
    "# Lines starting with '#' are comments and will be ignored.\n"
    "# Do NOT edit transaction_id as it is the primary sort/search key.\n"
)


def load_from_file(filepath: str = DATA_FILE) -> list:
    """
    Read all Transaction records from the data file into a 1-D Python list.
    The list in memory is the working data structure for all sort/search ops.
    Skips blank lines and comment lines (starting with '#').
    Returns a list of Transaction objects (preserving file order = unsorted).
    """
    transactions = []
    if not os.path.exists(filepath):
        print(f"  [INFO] '{filepath}' not found. Starting with empty dataset.")
        return transactions
    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            t = Transaction.from_file_line(line)
            if t is not None:
                transactions.append(t)
            elif line.strip() and not line.strip().startswith("#"):
                print(f"  [WARNING] Skipping malformed line {line_no}: {line.strip()!r}")
    return transactions


def save_to_file(transactions: list, filepath: str = DATA_FILE):
    """
    Write all Transaction records from the in-memory list back to the data file.
    Overwrites the file completely to reflect any inserts or edits.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(FILE_HEADER)
        for t in transactions:
            f.write(t.to_file_line() + "\n")


import time

# Global recursive call counter (optional feature — counts Merge Sort recursion depth)
_merge_sort_calls = 0


# =============================================================================
# MERGE SORT — Divide and Conquer
# =============================================================================

def merge_sort(arr: list, key=lambda t: t.transaction_id,
               show_steps: bool = False, depth: int = 0) -> list:
    """
    Merge Sort — Divide and Conquer sorting algorithm.

    ── DIVIDE  : Split array into two halves at the midpoint
    ── CONQUER : Recursively sort each half (base case: length <= 1)
    ── COMBINE : Merge the two sorted halves into one sorted array

    Parameters:
        arr        : List of Transaction objects to sort
        key        : Lambda extracting the comparison value (default: transaction_id)
        show_steps : If True, prints each recursive divide/combine step
        depth      : Current recursion depth (used to indent trace output)

    Time complexity : O(n log n) — best, average, and worst case
    Space complexity: O(n)       — auxiliary arrays created during merging
    """
    global _merge_sort_calls
    _merge_sort_calls += 1

    # ── BASE CASE ─────────────────────────────────────────────────────────────
    # A list of 0 or 1 elements is already sorted — return immediately
    if len(arr) <= 1:
        return arr

    indent = "    " + "  " * depth
    if show_steps:
        ids = [key(t) for t in arr]
        print(f"{indent}[DIVIDE ]  {ids}")

    # ── DIVIDE ────────────────────────────────────────────────────────────────
    mid   = len(arr) // 2
    left  = arr[:mid]   # left half
    right = arr[mid:]   # right half

    # ── CONQUER ───────────────────────────────────────────────────────────────
    left  = merge_sort(left,  key, show_steps, depth + 1)
    right = merge_sort(right, key, show_steps, depth + 1)

    # ── COMBINE ───────────────────────────────────────────────────────────────
    merged = _merge(left, right, key)

    if show_steps:
        ids = [key(t) for t in merged]
        print(f"{indent}[COMBINE]  {ids}")

    return merged


def _merge(left: list, right: list, key) -> list:
    """
    Merge two sorted lists into a single sorted list.
    Compares the front elements of each half using 'key',
    picks the smaller one, then appends any remaining elements.
    Time complexity: O(n)  where n = len(left) + len(right)
    """
    result = []
    i = j  = 0

    # Compare front elements from both halves; pick the smaller
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append any remaining elements (already sorted)
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def reset_call_counter():
    global _merge_sort_calls
    _merge_sort_calls = 0


def get_call_count() -> int:
    return _merge_sort_calls


# =============================================================================
# BINARY SEARCH — Divide and Conquer
# =============================================================================

def binary_search(arr: list, target_id: int) -> tuple:
    """
    Binary Search — Divide and Conquer searching algorithm.

    PRECONDITION: arr must be sorted by transaction_id (ascending).

    ── DIVIDE  : Find the midpoint of the current search range [low..high]
    ── CONQUER : Decide which half the target belongs in and recurse into it
    ── COMBINE : Return result directly (no merging needed for searching)

    Parameters:
        arr       : Sorted list of Transaction objects
        target_id : The transaction_id integer to find

    Returns:
        (Transaction | None, comparisons_made, steps_log)

    Time complexity: O(log n) — average and worst case
    Space complexity: O(1)   — iterative implementation
    """
    low  = 0
    high = len(arr) - 1
    comparisons = 0
    steps_log   = []

    while low <= high:

        # ── DIVIDE ────────────────────────────────────────────────────────────
        mid    = (low + high) // 2
        mid_id = arr[mid].transaction_id
        comparisons += 1

        steps_log.append(
            f"    Step {comparisons}: Range [{low}..{high}]  "
            f"→  mid={mid}  (ID={mid_id})  target={target_id}"
        )

        # ── CONQUER ───────────────────────────────────────────────────────────
        if mid_id == target_id:
            steps_log.append(f"    ✔ Match found at index {mid}!")
            return arr[mid], comparisons, steps_log

        elif target_id < mid_id:
            # Target must be in the LEFT half — discard right half
            steps_log.append(
                f"    → {target_id} < {mid_id}: search LEFT half [{low}..{mid - 1}]"
            )
            high = mid - 1

        else:
            # Target must be in the RIGHT half — discard left half
            steps_log.append(
                f"    → {target_id} > {mid_id}: search RIGHT half [{mid + 1}..{high}]"
            )
            low = mid + 1

    steps_log.append(f"    ✘ Search space exhausted — ID {target_id} not found.")
    return None, comparisons, steps_log


# =============================================================================
# LINEAR SEARCH — for performance comparison
# =============================================================================

def linear_search(arr: list, target_id: int) -> tuple:
    """
    Linear Search — sequential scan from index 0 to n-1.
    Does NOT require the array to be sorted.
    Used to compare performance against Binary Search.

    Time complexity : O(n) — worst and average case
    Space complexity: O(1)

    Returns: (Transaction | None, comparisons_made)
    """
    comparisons = 0
    for item in arr:
        comparisons += 1
        if item.transaction_id == target_id:
            return item, comparisons
    return None, comparisons


# =============================================================================
# PERFORMANCE COMPARISON
# =============================================================================

def compare_performance(transactions: list, sorted_arr: list,
                        test_ids: list, repeat: int = 1000) -> None:
    """
    Compare Binary Search vs Linear Search timing across multiple keys.
    Each search is repeated 'repeat' times for stable nanosecond timing.
    Also benchmarks a single Merge Sort run.
    """
    print(f"\n  n = {len(transactions)} records  |  "
          f"Each search repeated {repeat:,}× for stable timing")

    print(f"\n  {'ID':<10} {'Exists':<8} "
          f"{'Binary Search (ns)':>20} {'Cmps':>6}  "
          f"{'Linear Search (ns)':>20} {'Cmps':>6}")
    print("  " + "─" * 76)

    bs_total = ls_total = 0

    for tid in test_ids:
        # Binary Search timing
        t0 = time.perf_counter_ns()
        for _ in range(repeat):
            res_b, cmp_b, _ = binary_search(sorted_arr, tid)
        t1 = time.perf_counter_ns()
        bs_ns = (t1 - t0) // repeat

        # Linear Search timing
        t2 = time.perf_counter_ns()
        for _ in range(repeat):
            res_l, cmp_l = linear_search(transactions, tid)
        t3 = time.perf_counter_ns()
        ls_ns = (t3 - t2) // repeat

        exists = "YES" if res_b is not None else "NO"
        print(f"  {tid:<10} {exists:<8} "
              f"{bs_ns:>20,} {cmp_b:>6}  "
              f"{ls_ns:>20,} {cmp_l:>6}")

        bs_total += bs_ns
        ls_total += ls_ns

    n_keys = len(test_ids)
    avg_b  = bs_total // n_keys
    avg_l  = ls_total // n_keys

    print("  " + "─" * 76)
    print(f"  {'TOTAL':<18} {bs_total:>20,} {'':>6}  {ls_total:>20,}")
    print(f"  {'AVERAGE':<18} {avg_b:>20,} {'':>6}  {avg_l:>20,}")

    # Merge Sort benchmark
    reset_call_counter()
    t0 = time.perf_counter_ns()
    for _ in range(repeat):
        merge_sort(list(transactions))
    t1 = time.perf_counter_ns()
    ms_ns = (t1 - t0) // repeat

    print(f"\n  ── Algorithm Summary ──────────────────────────────────────────")
    print(f"  Merge Sort (per run, n={len(transactions)})    : {ms_ns:>10,} ns  │  O(n log n)")
    print(f"  Binary Search (avg per search) : {avg_b:>10,} ns  │  O(log n)")
    print(f"  Linear Search (avg per search) : {avg_l:>10,} ns  │  O(n)")

    if avg_b > 0:
        ratio = avg_l / avg_b
        winner = "Binary Search" if avg_b < avg_l else "Linear Search"
        print(f"\n  At n={len(transactions)}: {winner} is faster for search "
              f"(ratio ≈ {ratio:.2f}×)")

    print(f"\n  ── Analysis ───────────────────────────────────────────────────")
    n = len(transactions)
    print(f"  • Binary Search needs at most log₂({n}) ≈ {n.bit_length()} comparisons per search.")
    print(f"  • Linear Search needs up to {n} comparisons for non-existing keys.")
    print(f"  • At small n ({n} records), Python function-call overhead can make Binary")
    print(f"    Search appear slower. Its O(log n) advantage becomes clear at n > 100.")
    print(f"  • Merge Sort is a one-time upfront cost that unlocks Binary Search.")
    print(f"  • Together: Sort once O(n log n), search many times O(log n) each.")


# =============================================================================
# TIME COMPLEXITY TABLE
# =============================================================================

def show_complexity_table(n: int) -> None:
    """Display a formatted time complexity analysis table."""
    import math
    print(f"\n  ┌{'─'*73}┐")
    print(f"  │{'  TIME COMPLEXITY ANALYSIS TABLE':^73}│")
    print(f"  ├{'─'*18}┬{'─'*13}┬{'─'*15}┬{'─'*13}┬{'─'*11}┤")
    print(f"  │{'  Algorithm':<18}│{'  Best':<13}│{'  Average':<15}│{'  Worst':<13}│{'  Space':<11}│")
    print(f"  ├{'─'*18}┼{'─'*13}┼{'─'*15}┼{'─'*13}┼{'─'*11}┤")
    rows = [
        ("  Merge Sort",    "  O(n log n)", "  O(n log n)", "  O(n log n)", "  O(n)"),
        ("  Binary Search", "  O(1)",       "  O(log n)",   "  O(log n)",   "  O(1)"),
        ("  Linear Search", "  O(1)",       "  O(n/2)",     "  O(n)",       "  O(1)"),
        ("  Array Access",  "  O(1)",       "  O(1)",       "  O(1)",       "  O(1)"),
    ]
    for r in rows:
        print(f"  │{r[0]:<18}│{r[1]:<13}│{r[2]:<15}│{r[3]:<13}│{r[4]:<11}│")
    print(f"  └{'─'*18}┴{'─'*13}┴{'─'*15}┴{'─'*13}┴{'─'*11}┘")

    log_n = int(math.log2(n)) if n > 0 else 0
    nlogn = n * log_n
    print(f"\n  For n = {n} records:")
    print(f"    log₂(n)     = {log_n}  → Binary Search needs at most {log_n} comparisons")
    print(f"    n × log₂(n) = {nlogn} → Merge Sort performs ~{nlogn} operations")
    print(f"    n           = {n}  → Linear Search needs up to {n} comparisons")
    print(f"\n  Key Insight:")
    print(f"    Merge Sort is consistently O(n log n) — unlike Quick Sort which")
    print(f"    degrades to O(n²) in the worst case. This predictability makes")
    print(f"    Merge Sort preferable for guaranteed performance.")
    print(f"    Binary Search requires a sorted array but rewards with O(log n)")
    print(f"    lookup — orders of magnitude faster than O(n) at large scale.")


import os


# =============================================================================
# DATASET — loaded from transactions.txt into a 1-D list at startup
# =============================================================================

def load_transactions() -> list:
    """
    Load Transaction records from transactions.txt into a 1-D Python list.
    The file order is preserved (intentionally unsorted) so Merge Sort
    has a meaningful effect when demonstrated.
    """
    return load_from_file(DATA_FILE)


# =============================================================================
# DISPLAY HELPERS
# =============================================================================

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    print("\n" + "=" * 75)
    print("       🛒   TranSys — Customer Transaction Management System   🛒")
    print("            Divide and Conquer  |  Merge Sort  |  Binary Search")
    print("=" * 75)


def print_transactions(arr: list, title: str = "Transactions"):
    print(f"\n  {'─' * 72}")
    print(f"  {title}  ({len(arr)} records)")
    print(f"  {'─' * 72}")
    for t in arr:
        print(t)
    print(f"  {'─' * 72}")


def show_menu() -> str:
    print("\n  ┌──────────────────────────────────────────────────────┐")
    print("  │                     MAIN MENU                        │")
    print("  ├──────────────────────────────────────────────────────┤")
    print("  │  1. Display All Transactions                         │")
    print("  │  2. Sort Transactions (Merge Sort)                   │")
    print("  │  3. Search Transaction (Binary Search)               │")
    print("  │  4. Search Transaction (Linear Search — comparison)  │")
    print("  │  5. Insert New Transaction                           │")
    print("  │  6. Sort by Different Attribute                      │")
    print("  │  7. Performance Comparison                           │")
    print("  │  8. Time Complexity Analysis Table                   │")
    print("  │  0. Exit                                             │")
    print("  └──────────────────────────────────────────────────────┘")
    return input("  Enter your choice: ").strip()


# =============================================================================
# FEATURE 1 — Display All Transactions
# =============================================================================

def feature_display(transactions: list, is_sorted: bool):
    status = "(sorted by Transaction ID)" if is_sorted else "(unsorted — original order)"
    print_transactions(transactions, f"All Transactions {status}")


# =============================================================================
# FEATURE 2 — Sort using Merge Sort
# =============================================================================

def feature_merge_sort(transactions: list) -> list:
    print("\n  ── Merge Sort (Divide and Conquer) " + "─" * 38)

    # Show array BEFORE sorting
    print("\n  BEFORE SORTING:")
    ids_before = [t.transaction_id for t in transactions]
    print(f"  {ids_before}")
    print_transactions(transactions, "Unsorted Transactions")

    # Ask whether to show recursive trace
    show = input("\n  Show recursive call trace? (y/n): ").strip().lower() == 'y'
    if show:
        print("\n  ── Recursive Call Trace ──────────────────────────────────────")

    reset_call_counter()
    import time
    t0 = time.perf_counter_ns()
    sorted_arr = merge_sort(list(transactions), show_steps=show)
    t1 = time.perf_counter_ns()
    elapsed_ns = t1 - t0

    # Show array AFTER sorting
    print("\n  AFTER SORTING (by Transaction ID — ascending):")
    ids_after = [t.transaction_id for t in sorted_arr]
    print(f"  {ids_after}")
    print_transactions(sorted_arr, "Sorted Transactions")

    calls = get_call_count()
    print(f"\n  ── Merge Sort Statistics ─────────────────────────────────────")
    print(f"  Recursive calls made : {calls}")
    print(f"  Time taken           : {elapsed_ns:,} ns  ({elapsed_ns / 1_000_000:.4f} ms)")
    print(f"  Time complexity      : O(n log n)  →  "
          f"n={len(sorted_arr)}, log₂(n)≈{len(sorted_arr).bit_length() - 1}")

    return sorted_arr


# =============================================================================
# FEATURE 3 — Binary Search  (Q2.4b mandatory demonstrations included)
# =============================================================================

def feature_binary_search(sorted_arr: list, is_sorted: bool):
    print("\n  ── Binary Search (Divide and Conquer) " + "─" * 35)

    if not is_sorted or not sorted_arr:
        print("\n  [!] The array has not been sorted yet.")
        print("  Binary Search requires a sorted array.")
        print("  Please use option 2 (Merge Sort) first, then try again.")
        return

    try:
        target = int(input("  Enter Transaction ID to search: ").strip())
    except ValueError:
        print("  ✘ Invalid input. Please enter an integer Transaction ID.")
        return

    import time
    t0 = time.perf_counter_ns()
    result, comparisons, steps = binary_search(sorted_arr, target)
    t1 = time.perf_counter_ns()

    print(f"\n  ── Divide & Conquer Steps ────────────────────────────────────")
    for step in steps:
        print(step)

    print(f"\n  Comparisons made : {comparisons}")
    print(f"  Time taken       : {t1 - t0:,} ns")

    if result:
        print(f"\n  ✔ Transaction FOUND:")
        print(result)
    else:
        print(f"\n  ✘ Transaction ID {target} does NOT exist in the dataset.")


def run_mandatory_search_demo(sorted_arr: list):
    """
    Q2.4b — Automatically demonstrate searching for one existing
    and one non-existing transaction after sorting.
    """
    print("\n  ── Q2.4b Mandatory Search Demonstrations " + "─" * 32)

    exist_id = sorted_arr[len(sorted_arr) // 2].transaction_id

    # Search 1 — Existing
    print(f"\n  [Search 1]  Existing Transaction ID: {exist_id}")
    print(f"  {'─' * 60}")
    result, cmps, steps = binary_search(sorted_arr, exist_id)
    for s in steps:
        print(s)
    print(f"  Total comparisons : {cmps}")
    if result:
        print(f"  ✔ FOUND: {result}")

    # Search 2 — Non-existing
    non_id = 9999
    print(f"\n  [Search 2]  Non-existing Transaction ID: {non_id}")
    print(f"  {'─' * 60}")
    result2, cmps2, steps2 = binary_search(sorted_arr, non_id)
    for s in steps2:
        print(s)
    print(f"  Total comparisons : {cmps2}")
    print(f"  ✘ Transaction ID {non_id} does NOT exist in the dataset.")


# =============================================================================
# FEATURE 4 — Linear Search
# =============================================================================

def feature_linear_search(transactions: list):
    print("\n  ── Linear Search (Sequential Scan — for comparison) " + "─" * 21)
    try:
        target = int(input("  Enter Transaction ID to search: ").strip())
    except ValueError:
        print("  ✘ Invalid input. Please enter an integer Transaction ID.")
        return

    import time
    t0 = time.perf_counter_ns()
    result, comparisons = linear_search(transactions, target)
    t1 = time.perf_counter_ns()

    print(f"\n  Records scanned  : {comparisons} / {len(transactions)}")
    print(f"  Time taken       : {t1 - t0:,} ns")

    if result:
        print(f"\n  ✔ Transaction FOUND:")
        print(result)
    else:
        print(f"\n  ✘ Transaction ID {target} does NOT exist in the dataset.")


# =============================================================================
# OPTIONAL FEATURE 5 — Insert Transaction dynamically
# =============================================================================

def feature_insert(transactions: list, is_sorted: bool) -> tuple:
    print("\n  ── Insert New Transaction " + "─" * 47)
    try:
        tid   = int(input("  Transaction ID   : ").strip())
        cname = input("  Customer Name    : ").strip()
        pname = input("  Product Name     : ").strip()
        amt   = float(input("  Amount (RM)      : ").strip())
        date  = input("  Date (DD/MM/YYYY): ").strip()
    except ValueError:
        print("  ✘ Invalid input. Please check your entries.")
        return transactions, is_sorted

    for t in transactions:
        if t.transaction_id == tid:
            print(f"  ✘ Transaction ID {tid} already exists.")
            return transactions, is_sorted

    transactions.append(Transaction(tid, cname, pname, amt, date))
    save_to_file(transactions)   # persist to transactions.txt immediately
    print(f"\n  ✔ Transaction {tid} added successfully.")
    print(f"  ✔ Saved to '{DATA_FILE}'.")
    print(f"  Note: Array is now unsorted — run Merge Sort (option 2) to re-sort.")
    return transactions, False


# =============================================================================
# OPTIONAL FEATURE 6 — Sort by different attribute
# =============================================================================

def feature_sort_by_attribute(transactions: list) -> list:
    print("\n  ── Sort by Attribute " + "─" * 51)
    print("  [1] Transaction ID   [2] Customer Name   [3] Amount   [4] Date")
    choice = input("  Sort by: ").strip()

    key_map = {
        "1": (lambda t: t.transaction_id,   "Transaction ID"),
        "2": (lambda t: t.customer_name,    "Customer Name"),
        "3": (lambda t: t.amount,           "Amount (RM)"),
        "4": (lambda t: t.transaction_date, "Transaction Date"),
    }

    if choice not in key_map:
        print("  ✘ Invalid choice.")
        return transactions

    key_fn, key_name = key_map[choice]

    reset_call_counter()
    import time
    t0 = time.perf_counter_ns()
    sorted_arr = merge_sort(list(transactions), key=key_fn)
    t1 = time.perf_counter_ns()

    print_transactions(sorted_arr, f"Sorted by: {key_name}")
    print(f"\n  Recursive calls : {get_call_count()}")
    print(f"  Time taken      : {t1 - t0:,} ns")
    return sorted_arr


# =============================================================================
# MAIN DRIVER
# =============================================================================

def main():
    transactions = load_transactions()
    sorted_arr   = []
    is_sorted    = False

    print_header()
    if transactions:
        print(f"\n  Loaded {len(transactions)} transaction records from '{DATA_FILE}'.")
        print(f"  Stored in 1-D list (unsorted — original file order).")
        print(f"  Transaction IDs: {[t.transaction_id for t in transactions]}")
    else:
        print(f"\n  [!] No records found in '{DATA_FILE}'. Use option 5 to add transactions.")
    input("\n  Press ENTER to enter the main menu...")

    while True:
        print_header()
        choice = show_menu()

        # ── 1. Display All ────────────────────────────────────────────
        if choice == "1":
            feature_display(transactions, is_sorted)

        # ── 2. Merge Sort ─────────────────────────────────────────────
        elif choice == "2":
            sorted_arr = feature_merge_sort(transactions)
            is_sorted  = True
            demo = input("\n  Run mandatory search demonstrations (Q2.4b)? (y/n): ").strip().lower()
            if demo == 'y':
                run_mandatory_search_demo(sorted_arr)

        # ── 3. Binary Search ──────────────────────────────────────────
        elif choice == "3":
            feature_binary_search(sorted_arr, is_sorted)

        # ── 4. Linear Search ──────────────────────────────────────────
        elif choice == "4":
            feature_linear_search(transactions)

        # ── 5. Insert ─────────────────────────────────────────────────
        elif choice == "5":
            transactions, is_sorted = feature_insert(transactions, is_sorted)

        # ── 6. Sort by Attribute ──────────────────────────────────────
        elif choice == "6":
            sorted_arr = feature_sort_by_attribute(transactions)
            is_sorted  = True

        # ── 7. Performance Comparison ─────────────────────────────────
        elif choice == "7":
            if not is_sorted:
                print("\n  [!] Please sort the array first (option 2) before running comparison.")
            else:
                test_ids = [
                    transactions[0].transaction_id,
                    transactions[9].transaction_id,
                    transactions[-1].transaction_id,
                    99999,
                    88888,
                ]
                compare_performance(transactions, sorted_arr, test_ids)

        # ── 8. Complexity Table ───────────────────────────────────────
        elif choice == "8":
            show_complexity_table(len(transactions))

        # ── 0. Exit ───────────────────────────────────────────────────
        elif choice == "0":
            print("\n  Thank you for using TranSys. Goodbye! 👋\n")
            break

        else:
            print("  ✘ Invalid choice. Please enter a number from the menu.")

        input("\n  Press ENTER to continue...")


if __name__ == "__main__":
    main()