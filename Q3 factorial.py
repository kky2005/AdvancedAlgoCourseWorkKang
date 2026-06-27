"""
Question 3: Concurrent Process — Factorial with Multithreading
===============================================================
Calculates 50!, 100!, and 200! using:
  - Multithreading (3 separate threads, one per factorial)
  - Sequential processing (no threads, for comparison)

Timing formula (from diagram):
    T = t2 - t1
    t1 = start time of the thread that was FIRST executed
    t2 = end time of the thread that COMPLETED LAST

Runs 10 rounds for each experiment and reports T per round + average T.
"""

import threading
import time
import os


# =============================================================================
# SECTION 1: Factorial Function
# =============================================================================

def factorial(n: int) -> int:
    """
    Calculate n! iteratively.

    Primitive operation count (for Big-O derivation):
      - 1 assignment : result = 1              → 1 operation
      - Loop runs n times (i = 1, 2, ..., n):
            * 1 multiplication : result = result * i   → n operations
            * 1 assignment     : result = ...          → n operations
            * 1 comparison     : i <= n (loop check)   → n operations
            * 1 increment      : i += 1                → n operations
      Total primitive operations = 1 + 4n

    Big-O:
      T(n) = 1 + 4n
      As n → ∞, the constant 1 and coefficient 4 are dropped.
      Therefore, Big-O = O(n)

    Time complexity explanation:
      The function performs exactly n multiplications — one per integer
      from 1 to n. There is no nested loop or recursion. The time
      taken grows LINEARLY with n, so the time complexity is O(n).
    """
    result = 1                  # 1 assignment
    for i in range(1, n + 1):  # loop runs n times
        result = result * i     # 1 multiplication + 1 assignment per iteration
    return result


# =============================================================================
# SECTION 2: Thread Worker
# =============================================================================

class FactorialThread(threading.Thread):
    """
    A Thread subclass that computes factorial(n) and records:
        start_ns  : time.time_ns() just before computation begins
        end_ns    : time.time_ns() just after computation completes
        result    : the computed factorial value
    """

    def __init__(self, n: int, thread_name: str):
        super().__init__(name=thread_name)
        self.n         = n           # the number to compute factorial for
        self.result    = None        # will hold n!
        self.start_ns  = None        # nanosecond timestamp when thread starts work
        self.end_ns    = None        # nanosecond timestamp when thread finishes

    def run(self):
        """
        Thread entry point. Records start time, computes factorial,
        records end time.
        """
        self.start_ns = time.time_ns()    # t1 candidate — when THIS thread starts
        self.result   = factorial(self.n)
        self.end_ns   = time.time_ns()    # t2 candidate — when THIS thread ends


# =============================================================================
# SECTION 3: Multithreading Experiment — 10 Rounds
# =============================================================================

def run_multithreaded_experiment(rounds: int = 10) -> list:
    """
    Runs the multithreaded factorial experiment for the given number of rounds.

    Each round:
      1. Creates 3 FactorialThread objects (for 50!, 100!, 200!)
      2. Starts all 3 threads
      3. Joins (waits for) all 3 threads to complete
      4. Computes T = t2 - t1 using the diagram formula:
             t1 = min(thread.start_ns) for all threads  [first to start]
             t2 = max(thread.end_ns)   for all threads  [last to finish]
             T  = t2 - t1              [total elapsed nanoseconds]

    Returns a list of T values (one per round) in nanoseconds.
    """
    t_values = []

    print("\n  ── Multithreading Experiment (3 Threads) ────────────────────────────────")
    print(f"  {'Round':<8} {'t1 (start of 1st thread)':<30} {'t2 (end of last thread)':<30} {'T = t2 - t1 (ns)'}")
    print("  " + "─" * 95)

    for r in range(1, rounds + 1):
        # Create one thread per factorial
        thread_50  = FactorialThread(50,  "Thread-50!")
        thread_100 = FactorialThread(100, "Thread-100!")
        thread_200 = FactorialThread(200, "Thread-200!")
        threads    = [thread_50, thread_100, thread_200]

        # Start all 3 threads
        for t in threads:
            t.start()

        # Wait for all 3 threads to complete
        for t in threads:
            t.join()

        # Apply the timing formula from the diagram:
        # t1 = start time of the thread that was FIRST executed
        # t2 = end time of the thread that COMPLETED LAST
        t1 = min(t.start_ns for t in threads)   # earliest start
        t2 = max(t.end_ns   for t in threads)   # latest finish
        T  = t2 - t1                             # total elapsed time

        t_values.append(T)
        print(f"  {r:<8} {t1:<30,} {t2:<30,} {T:>15,}")

    avg_T = max(1, sum(t_values) // rounds)   # max(1,...) prevents ZeroDivisionError
    print("  " + "─" * 95)
    print(f"  {'Average T':>69} {avg_T:>15,} ns")
    print(f"  {'':>69} {avg_T / 1_000_000:.4f} ms")

    return t_values


# =============================================================================
# SECTION 4: Sequential (No Multithreading) Experiment — 10 Rounds
# =============================================================================

def run_sequential_experiment(rounds: int = 10) -> list:
    """
    Runs the same 3 factorial computations (50!, 100!, 200!) sequentially
    (no threads) for the given number of rounds.

    Each round:
      1. Records start time t1 (before first computation)
      2. Computes 50!, 100!, 200! one after another
      3. Records end time t2 (after last computation)
      4. T = t2 - t1

    Returns a list of T values in nanoseconds.
    """
    t_values = []

    print("\n  ── Sequential Experiment (No Multithreading) ────────────────────────────")
    print(f"  {'Round':<8} {'t1 (start)':<30} {'t2 (end)':<30} {'T = t2 - t1 (ns)'}")
    print("  " + "─" * 95)

    for r in range(1, rounds + 1):
        t1 = time.time_ns()        # start before first computation
        factorial(50)
        factorial(100)
        factorial(200)
        t2 = time.time_ns()        # end after last computation
        T  = t2 - t1

        t_values.append(T)
        print(f"  {r:<8} {t1:<30,} {t2:<30,} {T:>15,}")

    avg_T = max(1, sum(t_values) // rounds)   # max(1,...) prevents ZeroDivisionError
    print("  " + "─" * 95)
    print(f"  {'Average T':>69} {avg_T:>15,} ns")
    print(f"  {'':>69} {avg_T / 1_000_000:.4f} ms")

    return t_values


# =============================================================================
# SECTION 5: Results Comparison
# =============================================================================

def print_comparison(mt_values: list, seq_values: list):
    """Print a side-by-side comparison of multithreaded vs sequential results."""
    rounds = len(mt_values)
    print("\n  ── Results Comparison ───────────────────────────────────────────────────")
    print(f"  {'Round':<8} {'Multithreaded T (ns)':>22} {'Sequential T (ns)':>22} {'Difference (ns)':>20}")
    print("  " + "─" * 76)
    for i in range(rounds):
        diff = seq_values[i] - mt_values[i]
        faster = "MT faster" if diff > 0 else "SEQ faster"
        print(f"  {i+1:<8} {mt_values[i]:>22,} {seq_values[i]:>22,} {diff:>18,}  ({faster})")

    avg_mt  = max(1, sum(mt_values)  // rounds)   # max(1,...) prevents ZeroDivisionError
    avg_seq = max(1, sum(seq_values) // rounds)   # if times round to 0, treat as 1 ns
    avg_diff = avg_seq - avg_mt

    print("  " + "─" * 76)
    print(f"  {'Average':<8} {avg_mt:>22,} {avg_seq:>22,} {avg_diff:>20,}")
    print(f"\n  Average Multithreaded T : {avg_mt:,} ns  ({avg_mt / 1_000_000:.4f} ms)")
    print(f"  Average Sequential T    : {avg_seq:,} ns  ({avg_seq / 1_000_000:.4f} ms)")

    if avg_mt < avg_seq:
        ratio = avg_seq / avg_mt
        print(f"\n  ✔ Multithreading was FASTER by a factor of {ratio:.2f}x on average.")
    elif avg_mt > avg_seq:
        ratio = avg_mt / avg_seq
        print(f"\n  ✘ Multithreading was SLOWER by a factor of {ratio:.2f}x on average.")
    else:
        print(f"\n  Both methods took approximately the same time.")

    print(f"\n  ANALYSIS:")
    print(f"  ─────────")
    print(f"  In Python, the Global Interpreter Lock (GIL) prevents true parallel")
    print(f"  execution of threads. Even with 3 threads, only ONE thread can execute")
    print(f"  Python bytecode at any given moment. The other threads must wait for")
    print(f"  the GIL to be released.")
    print(f"")
    print(f"  For CPU-bound tasks like factorial computation (pure arithmetic),")
    print(f"  multithreading adds overhead (thread creation, context switching,")
    print(f"  GIL contention) WITHOUT gaining true parallelism. This is why")
    print(f"  multithreaded results are often similar to or SLOWER than sequential.")
    print(f"")
    print(f"  Multithreading DOES improve performance for I/O-bound tasks, such as:")
    print(f"  downloading files, reading from disk, or making network requests,")
    print(f"  because threads can overlap their waiting time (the GIL is released")
    print(f"  during I/O operations).")
    print(f"")
    print(f"  For true CPU-bound parallelism in Python, multiprocessing should be")
    print(f"  used instead, as each process has its own GIL and Python interpreter.")








# =============================================================================
# SECTION 6: Main Program
# =============================================================================

def print_header():
    print("\n" + "=" * 75)
    print("     🔢  FactorialThreader — Concurrent Process Experiment  🔢")
    print("     Multithreading vs Sequential  |  50!  100!  200!")
    print("=" * 75)


def main():
    print_header()

    # Verify factorial results are correct
    print("\n  ── Factorial Verification ───────────────────────────────────────────────")
    for n in [50, 100, 200]:
        result = factorial(n)
        digits = len(str(result))
        print(f"  {n}! = {str(result)[:40]}...  ({digits} digits)")

    input("\n  Press ENTER to run the 10-round multithreading experiment...")

    # Q3.3 — Multithreaded experiment (10 rounds)
    mt_values = run_multithreaded_experiment(rounds=10)

    input("\n  Press ENTER to run the 10-round sequential experiment...")

    # Q3.4 — Sequential experiment (10 rounds)
    seq_values = run_sequential_experiment(rounds=10)

    # Comparison + analysis
    print_comparison(mt_values, seq_values)

    print("\n" + "=" * 75)
    print("  Experiment complete.")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()