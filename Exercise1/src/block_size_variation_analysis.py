"""The math module is used to calculate the greatest common divisor."""
import math

import matplotlib.pyplot as plt


def count_read_blocks(number, start, end):
    """
    This function calculates to be expected read accesses when reading
    from start to end and the number as the underlying system storage block size
    """
    first_multiple = (start // number) * number
    last_multiple = (end // number) * number
    return ((last_multiple - first_multiple) // number) + 1


def calculate_performances(a, b, storage_block_size):
    """
    This functions calculates the to be expected efficiencies due to to be expected
    read access patterns for a range of possible block sizes. It assumes a start
    and a stop index and the underlying system's storage block size and returns
    the block sizes, efficiences, and greatest common divisors of block size and
    storage block size for later analysis of gcd efficiency in relation to expected
    read efficiency.
    """
    performances = []
    gcd_values = []

    block_sizes = range(a, b + 1)

    for block_size in block_sizes:
        index = 0
        reads = 0
        while index % storage_block_size != 0 or reads == 0:
            reads += count_read_blocks(
                storage_block_size, index, index + block_size - 1
            )
            index += block_size
        storage_blocks_read = index // storage_block_size
        performance = storage_blocks_read / reads
        performances.append(performance)

        gcd_value = math.gcd(block_size, storage_block_size) / storage_block_size
        gcd_values.append(gcd_value)

    return block_sizes, performances, gcd_values


SIZE_STORAGE_BLOCK = 4096
A = 1
B = 5 * SIZE_STORAGE_BLOCK

sizes_blocks, efficiencies, gcds = calculate_performances(A, B, SIZE_STORAGE_BLOCK)

with open("../res/distinct_read_efficiencies.txt", "w", encoding="utf8") as file:
    for blocksize, efficiency in zip(sizes_blocks, efficiencies):
        file.write(f"{blocksize}, {efficiency}\n")

plt.plot(sizes_blocks, efficiencies, label="Distinct Read Efficiency")
plt.xlabel("Block Size")
plt.ylabel("Distinct Read Efficiency")
plt.title("Distinct Read Efficiency vs. Block Size")
# in Distinct Storage Blocks Read/Storage Blocks Read
plt.legend()
plt.grid(True)
plt.savefig(
    "../vis_gcd_block_size_multiples/expected_io_performance_analysis.pdf",
    format="pdf",
)
plt.close()

plt.plot(sizes_blocks, efficiencies, label="Distinct Read Efficiency")
plt.xlabel("Block Size")
plt.ylabel("Distinct Read Efficiency")
plt.title("Distinct Read Efficiency vs. Block Size")
# in Distinct Storage Blocks Read/Storage Blocks Read
plt.xlim(4 * SIZE_STORAGE_BLOCK - 11, 4 * SIZE_STORAGE_BLOCK + 10)
plt.ylim(0.79975, 0.80050)
plt.legend()
plt.grid(True)
plt.savefig(
    "../vis_gcd_block_size_multiples/limited_expected_io_performance_analysis.pdf",
    format="pdf",
)
plt.close()

plt.plot(sizes_blocks, efficiencies, label="Distinct Read Efficiency")
plt.plot(sizes_blocks, gcds, label="GCD efficiency", linestyle="dashed")
# in GCD(Block Size, Storage Block Size)/Storage Block Size
plt.xlabel("Block Size")
plt.ylabel("Value")
plt.title("Distinct Read Efficiency and GCD efficiency vs. Block Size")
plt.legend()
plt.grid(True)
plt.savefig(
    "../vis_gcd_block_size_multiples/gcd_vs_io_performance_analysis.pdf",
    format="pdf",
)
