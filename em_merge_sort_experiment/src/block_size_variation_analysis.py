import math
import matplotlib.pyplot as plt


def count_read_blocks(number, start, end):
    first_multiple = (start // number) * number
    last_multiple = (end // number) * number
    return ((last_multiple - first_multiple) // number) + 1


def calculate_performance(a, b, storage_block_size):
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


storage_block_size = 4096
a = 1
b = 5 * storage_block_size

block_sizes, performances, gcd_values = calculate_performance(a, b, storage_block_size)

with open("../res/results_gcd_block_size_multiples.txt", "w") as file:
    for block_size, performance in zip(block_sizes, performances):
        file.write(f"{block_size}, {performance}\n")

plt.plot(block_sizes, performances, label="Distinct Read Efficiency")
plt.xlabel("Block Size")
plt.ylabel("Distinct Read Efficiency")
plt.title("Distinct Read Efficiency vs. Block Size")
# in Distinct Storage Blocks Read/Storage Blocks Read
plt.legend()
plt.grid(True)
plt.savefig(
    "../vis_gcd_block_size_multiples/expected_io_performance_analysis.pdf", format="pdf"
)
plt.close()

plt.plot(block_sizes, performances, label="Distinct Read Efficiency")
plt.xlabel("Block Size")
plt.ylabel("Distinct Read Efficiency")
plt.title("Distinct Read Efficiency vs. Block Size")
# in Distinct Storage Blocks Read/Storage Blocks Read
plt.xlim(4 * storage_block_size - 11, 4 * storage_block_size + 10)
plt.ylim(0.79975, 0.80050)
plt.legend()
plt.grid(True)
plt.savefig(
    "../vis_gcd_block_size_multiples/limited_expected_io_performance_analysis.pdf",
    format="pdf",
)
plt.close()

plt.plot(block_sizes, performances, label="Distinct Read Efficiency")
plt.plot(block_sizes, gcd_values, label="GCD efficiency", linestyle="dashed")
# in GCD(Block Size, Storage Block Size)/Storage Block Size
plt.xlabel("Block Size")
plt.ylabel("Value")
plt.title(f"Distinct Read Efficiency and GCD efficiency vs. Block Size")
plt.legend()
plt.grid(True)
plt.savefig(
    "../vis_gcd_block_size_multiples/gcd_vs_io_performance_analysis.pdf", format="pdf"
)
