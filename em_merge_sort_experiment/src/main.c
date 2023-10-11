#include "classical_merge_sort.h"
#include <math.h>
#include <stdbool.h> // For testing file equality
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h> // For run time performance metric
#include <time.h>     // For run time performance metric
#include <unistd.h>   // For acquiring the host name

#define BREAKPOINT 0
#define DEBUG 0
#define INFO 0
#define RESULT 0
#define GLOBAL_STEP 0
#define BREAKPOINT_FAILED 1
#define NUM_THREADS 4

int compare_ints(const void *a, const void *b) {
  int int_a = *((int *)a);
  int int_b = *((int *)b);

  if (int_a == int_b)
    return 0;
  return int_a < int_b ? -1 : 1;
}

int compare_binary(const void *a, const void *b) {
  const int *int_a = (const int *)a;
  const int *int_b = (const int *)b;

  if (*int_a < *int_b)
    return -1;
  else if (*int_a > *int_b)
    return 1;
  else
    return 0;
}

void merge_round(char *input_file, char *output_file, long input_size,
                 long stream_block_size, int block_size) {
  long i = 0, i_1 = i, j = stream_block_size, j_1 = j;
  int *buffer_1 = (int *)malloc(block_size * sizeof(int));
  int *buffer_2 = (int *)malloc(block_size * sizeof(int));
  int *output_buffer = (int *)malloc(block_size * sizeof(int));

  if (buffer_1 == NULL || buffer_2 == NULL || output_buffer == NULL) {
    printf("Memory allocation failure");
  }

  int k = 0;

  FILE *input_fp = fopen(input_file, "rb");
  FILE *output_fp = fopen(output_file, "ab");

  if (input_fp == NULL || output_fp == NULL) {
    printf("Error opening files.\n");
    return;
  }

  if (input_size == 0) {
    printf("Input size is 0. Nothing to merge.\n");
    fclose(input_fp);
    fclose(output_fp);
    return;
  }

  long max_i = (input_size % stream_block_size == 0)
                   ? input_size - stream_block_size
                   : input_size - (input_size % stream_block_size);
  while (i < max_i && j < input_size) {

    long i_glob = (long)(i + stream_block_size) / (2 * stream_block_size);
    long j_glob = (long)j / (2 * stream_block_size);

    /// SPECIAL (Get rid of disbalance) {
    if (i_glob != j_glob) {
      if (i_glob < j_glob) {
        // Process first streamblock until i_glob == j_glob
        while (i_glob < j_glob) {
#if DEBUG
          printf("SPECIAL (one-sided): i: %d, i_1: %d\n", i, i_1);
#endif

          if (i == i_1) {
            if (i + block_size < j) {
              i_1 = (i + block_size < input_size) ? i + block_size : input_size;
            } else {
              i_1 = j;
            }
          }

#if DEBUG
          printf("SPECIAL (one-sided): i: %d, i_1: %d\n", i, i_1);
#endif

          fseek(input_fp, (i - (i % block_size)) * sizeof(int), SEEK_SET);
          fread(buffer_1, sizeof(int), i_1 - i + (i % block_size), input_fp);

#if DEBUG
          printf("SPECIAL (one-sided): Buffer 1: ");
          for (int b = 0; b < block_size; b++) {
            printf("%d ", buffer_1[b]);
          }
          printf("\n");
#endif

          while (i < i_1) {
            output_buffer[k % block_size] = buffer_1[i % block_size];

#if DEBUG
            printf("SPECIAL (one-sided): i\t%d\t", i);
            printf("j\t%d\t", j);
            printf("k\t%d\t", k);
            printf("el\t%d\t", buffer_1[i % block_size]);
            printf("\n");
#endif
            i++;

            k++;

#if BREAKPOINT
            while (getchar() != '\n') {
            }
#endif

            if (k % block_size == 0) {
              fwrite(output_buffer, sizeof(int), block_size, output_fp);
#if DEBUG
              printf("SPECIAL (one-sided): Wrote to output file\n");
              printf("SPECIAL (one-sided): Output Buffer: ");
              for (int b = 0; b < block_size; b++) {
                printf("%d ", output_buffer[b]);
              }
              printf("\n");
#endif
              k = 0;
            }
#if BREAKPOINT
            while (getchar() != '\n') {
            }
#endif
            i_glob = (long)(i + stream_block_size) / (2 * stream_block_size);
            j_glob = (long)j / (2 * stream_block_size);
          }
        }
#if DEBUG
        printf("SPECIAL (one-sided): Write remaining data in output_buffer\n");
#endif
        // Write remaining data in output_buffer if k is not a multiple of
        // block_size
        if (k % block_size != 0) {
          fwrite(output_buffer, sizeof(int), k % block_size, output_fp);
#if DEBUG
          printf("SPECIAL (one-sided): Wrote remaining to output file\n");
          printf("SPECIAL (one-sided): Output Buffer: ");
          for (int b = 0; b < k % block_size; b++) {
            printf("%d ", output_buffer[b]);
          }
          printf("\n");
#endif
          k = 0;
        }

#if BREAKPOINT
        while (getchar() != '\n') {
        }
#endif
      }

      if (j_glob < i_glob) {
        // Process second stream block until j_glob = i_glob
        while (j_glob < i_glob) {

#if DEBUG
          printf("SPECIAL (one-sided): j: %d, j_1: %d\n", j, j_1);
#endif
          if (j == j_1) {
            j_1 = (j + block_size < input_size) ? j + block_size : input_size;
          }

#if DEBUG
          printf("SPECIAL (one-sided): j: %d, j_1: %d\n", j, j_1);
#endif
          fseek(input_fp, (j - (j % block_size)) * sizeof(int), SEEK_SET);
          fread(buffer_2, sizeof(int), j_1 - j + (j % block_size), input_fp);

#if DEBUG
          printf("SPECIAL (one-sided): Buffer 2: ");
          for (int b = 0; b < block_size; b++) {
            printf("%d ", buffer_2[b]);
          }
          printf("\n");
#endif

          while (j < j_1) {
            output_buffer[k % block_size] = buffer_2[j % block_size];

#if DEBUG
            printf("SPECIAL (one-sided): i\t%d\t", i);
            printf("j\t%d\t", j);
            printf("k\t%d\t", k);
            printf("el\t%d\t", buffer_2[j % block_size]);
            printf("\n");
#endif
            j++;

            k++;

#if BREAKPOINT
            while (getchar() != '\n') {
            }
#endif

            if (k % block_size == 0) {
              fwrite(output_buffer, sizeof(int), block_size, output_fp);
#if DEBUG
              printf("SPECIAL (one-sided): Wrote to output file\n");
              printf("SPECIAL (one-sided): Output Buffer: ");
              for (int b = 0; b < block_size; b++) {
                printf("%d ", output_buffer[b]);
              }
              printf("\n");
#endif
              k = 0;
            }
#if BREAKPOINT
            while (getchar() != '\n') {
            }
#endif
            i_glob = (long)(i + stream_block_size) / (2 * stream_block_size);
            j_glob = (long)j / (2 * stream_block_size);
          }
        }

#if DEBUG
        printf("SPECIAL (one-sided): Write remaining data in output_buffer\n");
#endif
        // Write remaining data in output_buffer if k is not a multiple of
        // block_size
        if (k % block_size != 0) {
          fwrite(output_buffer, sizeof(int), k % block_size, output_fp);
#if DEBUG
          printf("SPECIAL (one-sided): Wrote remaining to output file\n");
          printf("SPECIAL (one-sided): Output Buffer: ");
          for (int b = 0; b < k % block_size; b++) {
            printf("%d ", output_buffer[b]);
          }
          printf("\n");
#endif
          k = 0;
        }
#if BREAKPOINT
        while (getchar() != '\n') {
        }
#endif
      }

      // Continue with next set of blocks
      if (i % stream_block_size == 0 && j % stream_block_size == 0 &&
          j == j_1 && i == i_1) {
        i += stream_block_size;
        i_1 += stream_block_size;
        j += stream_block_size;
        j_1 += stream_block_size;
      }

    } /// SPECIAL }
    /// NORMAL {
    {

#if DEBUG
      printf("i: %d, i_1: %d\n", i, i_1);
#endif
      if (i == i_1) {
        if (i + block_size < j) {
          i_1 = (i + block_size < input_size) ? i + block_size : input_size;
        } else {
          i_1 = j;
        }
      }
#if DEBUG
      printf("i: %d, i_1: %d\n", i, i_1);
#endif
      fseek(input_fp, (i - (i % block_size)) * sizeof(int), SEEK_SET);
      fread(buffer_1, sizeof(int), i_1 - i + (i % block_size), input_fp);
#if DEBUG
      printf("j: %d, j_1: %d\n", j, j_1);
#endif
      if (j == j_1) {
        j_1 = (j + block_size < input_size) ? j + block_size : input_size;
      }
#if DEBUG
      printf("j: %d, j_1: %d\n", j, j_1);
#endif

      fseek(input_fp, (j - (j % block_size)) * sizeof(int), SEEK_SET);
      fread(buffer_2, sizeof(int), j_1 - j + (j % block_size), input_fp);
#if DEBUG
      printf("Buffer 1: ");
      for (int b = 0; b < block_size; b++) {
        printf("%d ", buffer_1[b]);
      }
      printf("\n");

      printf("Buffer 2: ");
      for (int b = 0; b < block_size; b++) {
        printf("%d ", buffer_2[b]);
      }
      printf("\n");
#endif

      while (i < i_1 && j < j_1) {
        if (buffer_1[i % block_size] < buffer_2[j % block_size]) {
          output_buffer[k % block_size] = buffer_1[i % block_size];
#if DEBUG
          printf("i\t%d\t", i);
          printf("j\t%d\t", j);
          printf("k\t%d\t", k);
          printf("el\t%d\t", buffer_1[i % block_size]);
          printf("\n");
#endif
          i++;
        } else {
          output_buffer[k % block_size] = buffer_2[j % block_size];
#if DEBUG
          printf("i\t%d\t", i);
          printf("j\t%d\t", j);
          printf("k\t%d\t", k);
          printf("el\t%d\t", buffer_2[j % block_size]);
          printf("\n");
#endif
          j++;
        }

        k++;

        if (k % block_size == 0) {
          fwrite(output_buffer, sizeof(int), block_size, output_fp);
#if DEBUG
          printf("Wrote to output file\n");
          printf("Output Buffer: ");
          for (int b = 0; b < block_size; b++) {
            printf("%d ", output_buffer[b]);
          }
          printf("\n");
#endif
          k = 0;
        }
      }

#if DEBUG
      printf("%d %d", i, i_1);
#endif

      long stop = (long)(i) / (2 * stream_block_size) >=
                  (long)input_size / (2 * stream_block_size);
#if BREAKPOINT
      if (stop)
        while (getchar() != '\n') {
        };
#endif

      // Continue with the next set of blocks
      if (i % stream_block_size == 0 && j % stream_block_size == 0 && !stop &&
          j == j_1 && i == i_1) {
        i += stream_block_size;
        i_1 += stream_block_size;
        j += stream_block_size;
        j_1 += stream_block_size;
      }
    } /// NORMAL }
  }

  if (!(i % stream_block_size != 0 && j == input_size)) {
    max_i = j > input_size ? input_size : i_1;
    max_i =
        j == input_size ? input_size - (input_size % stream_block_size) : max_i;
  }
  while (i < max_i) {
#if DEBUG
    printf("i=%d i_1=%d\n", i, i_1);
#endif
    if (!(i % stream_block_size != 0 && j == input_size)) {
      max_i = j > input_size ? input_size : i_1;
      max_i = j == input_size ? input_size - (input_size % stream_block_size)
                              : max_i;
    }

#if DEBUG
    printf("max_i=%d", max_i);
#endif
#if BREAKPOINT
    while (getchar() != '\n') {
    };
#endif

    if (i == i_1) {
      if (i + block_size < input_size) {
        i_1 = (i + block_size < input_size) ? i + block_size : input_size;
      } else {
        i_1 = j < input_size ? j : input_size;
      }
    }
#if DEBUG
    printf("i: %d, i_1: %d\n", i, i_1);
#endif
    fseek(input_fp, (i - (i % block_size)) * sizeof(int), SEEK_SET);
    fread(buffer_1, sizeof(int), i_1 - i + (i % block_size), input_fp);
#if DEBUG
    printf("j: %d, j_1: %d\n", j, j_1);
#endif
    while (i < i_1) {
      output_buffer[k % block_size] = buffer_1[i % block_size];
      i++;
      k++;
      if (k % block_size == 0) {
        fwrite(output_buffer, sizeof(int), block_size, output_fp);
#if DEBUG
        printf("Wrote remaining to output file\n");
        printf("Output Buffer: ");
        for (int b = 0; b < block_size; b++) {
          printf("%d ", output_buffer[b]);
        }
        printf("\n");
#endif
        k = 0;
      }
    }
#if DEBUG
    printf("i: %d, i_1: %d\n", i, i_1);
#endif
  }
#if DEBUG
  printf("j=%d j_1=%d\n", j, j_1);
#endif
#if BREAKPOINT
  if (i == max_i)
    while (getchar() != '\n') {
    };
#endif
  while (j < input_size) {

#if DEBUG
    printf("j=%d j_1=%d\n", j, j_1);
#endif
#if BREAKPOINT
    while (getchar() != '\n') {
    };
#endif

    while (j < j_1) {
      output_buffer[k % block_size] = buffer_2[j % block_size];
      j++;
      k++;
      if (k % block_size == 0) {
        fwrite(output_buffer, sizeof(int), block_size, output_fp);
#if DEBUG
        printf("Wrote remaining to output file\n");
        printf("Output Buffer: ");
        for (int b = 0; b < block_size; b++) {
          printf("%d ", output_buffer[b]);
        }
        printf("\n");
#endif
      }
    }
#if DEBUG
    printf("j: %d, j_1: %d\n", j, j_1);
#endif
    if (j == j_1) {
      j_1 = (j + block_size < input_size) ? j + block_size : input_size;
    }
#if DEBUG
    printf("j: %d, j_1: %d\n", j, j_1);
#endif
    fseek(input_fp, (j - (j % block_size)) * sizeof(int), SEEK_SET);
    fread(buffer_2, sizeof(int), j_1 - j + (j % block_size), input_fp);
#if DEBUG
    printf("j: %d, j_1: %d\n", j, j_1);
#endif
  }
#if DEBUG
  printf("\n");
  printf("i\t%d\t", i);
  printf("j\t%d\t", j);
  printf("k\t%d\t", k);
  printf("\n");
  printf("i: %d, i_1: %d\n", i, i_1);
  printf("\n");
  printf("j: %d, j_1: %d\n", j, j_1);
  printf("\n");
  printf("Buffer 1: ");
  for (int b = 0; b < block_size; b++) {
    printf("%d ", buffer_1[b]);
  }
  printf("\n");

  printf("Buffer 2: ");
  for (int b = 0; b < block_size; b++) {
    printf("%d ", buffer_2[b]);
  }
  printf("\n");
  printf("Output Buffer: ");
  for (int b = 0; b < block_size; b++) {
    printf("%d ", output_buffer[b]);
  }
  printf("\n");
#endif

#if DEBUG
  printf("Write remaining data in output_buffer\n");
#endif
  // Write remaining data in output_buffer if k is not a multiple of block_size
  if (k % block_size != 0) {
    fwrite(output_buffer, sizeof(int), k % block_size, output_fp);
#if DEBUG
    printf("Wrote remaining to output file\n");
    printf("Output Buffer: ");
    for (int b = 0; b < k % block_size; b++) {
      printf("%d ", output_buffer[b]);
    }
    printf("\n");
#endif
  }

  fclose(input_fp);
  fclose(output_fp);
  free(buffer_1);
  free(buffer_2);
  free(output_buffer);
}

int initial_partition(char *input_file, char *output_file, int block_size,
                      int blocks_in_memory,
                      long input_size /* TODO: remove argument from function */,
                      int internal_sort_option) {
  FILE *f_in = fopen(input_file, "rb");
  FILE *f_out = fopen(output_file, "wb");

  int *buffer =
      (int *)calloc((size_t)block_size * (size_t)blocks_in_memory, sizeof(int));
  if (buffer == NULL) {
    printf("Memory allocation failure");
  }
  int merge_rounds = 0;
  size_t size;
  while ((size = fread(buffer, sizeof(int), block_size * blocks_in_memory,
                       f_in)) > 0) {
    if (internal_sort_option == 0) {
      merge_rounds = classical_merge_sort(buffer, (int)size);
    } else if (internal_sort_option == 1) {
      qsort(buffer, size, sizeof(int), compare_ints);
    } else if (internal_sort_option == 2) {
      qsort(buffer, size, sizeof(int), compare_binary);
    }
    fwrite(buffer, sizeof(int), size, f_out);
  }

  free(buffer);

  fclose(f_in);
  fclose(f_out);

  return merge_rounds;
}

void clear_file(char *filename) {
  FILE *file = fopen(filename, "w");
  if (file != NULL) {
    fclose(file);
  } else {
    printf("Error opening file for clearing.\n");
  }
}

bool are_files_equal(const char *filename1, const char *filename2) {
  FILE *file1 = fopen(filename1, "rb");
  FILE *file2 = fopen(filename2, "rb");

  if (file1 == NULL || file2 == NULL) {
    printf("Error opening files for reading.\n");
    return false;
  }

  int num1, num2;

  while (fread(&num1, sizeof(int), 1, file1) == 1 &&
         fread(&num2, sizeof(int), 1, file2) == 1) {
    if (num1 != num2) {
      fclose(file1);
      fclose(file2);
      return false;
    }
  }

  // If we reach here, both files have been read completely and are equal
  fclose(file1);
  fclose(file2);
  return true;
}

void print_file(char *filename) {
  FILE *f = fopen(filename, "rb");
  int num;
  while (fread(&num, sizeof(int), 1, f) == 1) {
    printf("%d ", num);
  }
  printf("\n");
  fclose(f);
}

int compare(const void *a, const void *b) { return (*(int *)a - *(int *)b); }

void test_merge_round() {
  FILE *input_fp = fopen("../bin/input.bin", "wb");
  if (input_fp == NULL) {
    printf("Error opening input file.\n");
    return;
  }

  srand(42);

  int blocks_in_memory = 3;

  int input_sizes[] = {30001, 30000, 20000, 12800, 10000, 6400, 3200, 1600, 800,
                       600,   450,   400,   201,   100,   55,   54,   53,   52,
                       51,    50,    49,    48,    47,    46,   45,   44,   43,
                       42,    41,    40,    39,    38,    37,   36,   35,   34,
                       33,    32,    31,    30,    29,    28,   27,   13,   12,
                       11,    10,    9,     8,     7,     6,    5,    4,    3};
  int block_sizes[] = {13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3};

  for (int i = 0; i < sizeof(input_sizes) / sizeof(input_sizes[0]); i++) {
    for (int j = 0; j < sizeof(block_sizes) / sizeof(block_sizes[0]); j++) {
      // Create input
      FILE *input_fp = fopen("../bin/input.bin", "wb");
      if (input_fp == NULL) {
        printf("Error opening input file.\n");
        return;
      }

      int input_size = input_sizes[i];
      int block_size = block_sizes[j];
      int stream_block_size = blocks_in_memory * block_size;
      srand(0);
      // Create input file {
      for (long long i = 0; i < input_size; i++) {
        int random_number = rand();
        fwrite(&random_number, sizeof(int), 1, input_fp);
      }
      fclose(input_fp);
      // Create input file }

      char *input_file = "../bin/input.bin";
      char *output_file = "../bin/output.bin";

      // Create extra sorted file
      FILE *input_fp_sort = fopen(input_file, "rb");
      if (input_fp_sort == NULL) {
        printf("Error opening input file for sorting.\n");
        return;
      }

      int *sorted_input = malloc(input_size * sizeof(int));
      if (sorted_input == NULL) {
        printf("Memory allocation error.\n");
        fclose(input_fp_sort);
        return;
      }

      for (int k = 0; k < input_size; k++) {
        fread(&sorted_input[k], sizeof(int), 1, input_fp_sort);
      }

      fclose(input_fp_sort);

      qsort(sorted_input, input_size, sizeof(int), compare);

      FILE *extra_sorted_fpp = fopen("../bin/extra_sorted.bin", "wb");
      if (extra_sorted_fpp == NULL) {
        printf("Error opening extra sorted file.\n");
        free(sorted_input);
        return;
      }

      for (int k = 0; k < input_size; k++) {
        fwrite(&sorted_input[k], sizeof(int), 1, extra_sorted_fpp);
      }

      fclose(extra_sorted_fpp);

      free(sorted_input);

      initial_partition(input_file, output_file, block_size, blocks_in_memory,
                        input_size, 0);

#if INFO
      // Print contents of input file after initial partition
      FILE *input_fp_after_partition = fopen("../bin/output.bin", "rb");
      if (input_fp_after_partition == NULL) {
        printf("Error opening file after initial partition.\n");
        return;
      }
      printf("Contents of input file after initial partition:\n");
      int num;
      while (fread(&num, sizeof(int), 1, input_fp_after_partition) == 1) {
        printf("%d ", num);
      }
      printf("\n");

      fclose(input_fp_after_partition);
#endif

      clear_file(input_file);

      // Switch roles of input_file and output_file
      char *temp_fp = input_file;
      input_file = output_file;
      output_file = temp_fp;

      while (stream_block_size < input_size) {
        merge_round(input_file, output_file, input_size, stream_block_size,
                    block_size);

#if INFO
        printf("Merge round completed with stream_block_size = %d.\n",
               stream_block_size);
#endif

        // Clear contents of the first parameter file
        FILE *input_fp = fopen(input_file, "wb");
        if (input_fp == NULL) {
          printf("Error opening input file.\n");
          return;
        }
        fclose(input_fp);

#if INFO
        // Print contents of the second parameter file
        FILE *output_fp = fopen(output_file, "rb");
        if (output_fp == NULL) {
          printf("Error opening output file.\n");
          return;
        }
        printf("Output file after merge round:\n");
        print_file(output_file);
        fclose(output_fp);
#endif

        // Switch roles of input_file and output_file
        char *temp_fp = input_file;
        input_file = output_file;
        output_file = temp_fp;

        stream_block_size *= 2;
      }

      // Compare merge process output file with extra sorted file
      FILE *output_fp = fopen(input_file, "rb");
      FILE *extra_sorted_fp = fopen("../bin/extra_sorted.bin", "rb");

#if RESULT
      char *extraa = "../bin/extra_sorted.bin";
      printf("Sorted reference file:\n");
      print_file(extraa);
#endif

      if (output_fp == NULL || extra_sorted_fp == NULL) {
        printf("Error opening files for comparison.\n");
        return;
      }

#if RESULT
      // Print contents of the result of the merging process
      printf("Output file after merge round:\n");
      print_file(input_file);
#endif

      fseek(output_fp, 0, SEEK_END);
      fseek(extra_sorted_fp, 0, SEEK_END);

      long output_size = ftell(output_fp);
      long extra_sorted_size = ftell(extra_sorted_fp);

      if (output_size != extra_sorted_size) {
        printf("input_size = %d, block_size = %d", input_size, block_size);
        printf("Files have different lengths %ld, %ld.\n", output_size,
               extra_sorted_size);
        fclose(output_fp);
        fclose(extra_sorted_fp);
      }

      rewind(output_fp);
      rewind(extra_sorted_fp);

      int result = 0;
      char *buf_output = malloc(output_size);
      char *buf_extra_sorted = malloc(extra_sorted_size);

      if (buf_output == NULL || buf_extra_sorted == NULL) {
        printf("Memory allocation error.\n");
        fclose(output_fp);
        fclose(extra_sorted_fp);
        return;
      }

      fread(buf_output, 1, output_size, output_fp);
      fread(buf_extra_sorted, 1, extra_sorted_size, extra_sorted_fp);

      if (memcmp(buf_output, buf_extra_sorted, output_size) != 0) {
        result = 1;
      }

      fclose(output_fp);
      fclose(extra_sorted_fp);
      free(buf_output);
      free(buf_extra_sorted);

      // Clean up extra sorted file
      remove("../bin/extra_sorted.bin");

#if INFO
      printf("Merging process complete.\n");
#endif

      if (result == 0) {
        printf("Test passed.\t");
      } else {
        printf("Test failed!\t");
#if BREAKPOINT_FAILED
        while (getchar() != '\n') {
        }
#endif
      }
      // Finish printing line
      printf("(input_size = %d,\tblock_size = %d).\n", input_size, block_size);
    }
  }
}

void perform_analysis() {
  /**
   * These are some relevant input sizes
   * 10000000 = 40 MB
   * 100000000 = 400 MB
   * 200000000 = 800 MB = 0.1 * RAM_SIZE
   * 500000000 = 2GB = maximum block_size (3 * block_size = 6GB < RAM_SIZE
   * hardware limit) 1000000000 = 4 GB = 0.5 * RAM_SIZE 2000000000 = 8 GB =
   * RAM_SIZE 20000000000 = 80 GB = 10 * RAM_SIZE
   */

  // Set for the block_size multiple of system storage block size analysis
  /*
  int num_different_files = 100;
  int num_runs_on_file = 40;
  long input_sizes[] = {1000000};
  int block_sizes[] = {4096 * 4 - 1, 4096 * 4, 4096 * 4 + 1};
  int max_classical = 10000000;
  int internal_sort_options[] = {1};
  */

  // Set for the long analysis: 0.4GB, 2GB, 4GB, 40GB (RAM 4GB on ThinkPad
  // Remote)
  /*
  int num_different_files = 1;
  int num_runs_on_file = 1;
  long input_sizes[] = {10000000000, 1000000000, 500000000, 100000000};
  // 1GB block_size -> at least 3GB allocated for the three buffers
  int block_sizes[] = {250000000};
  int max_classical = 500000000;
  int internal_sort_options[] = {1};
  */

  // Set for the scaling start analysis for the goodness-of-fit-test

  int num_different_files = 1;
  int num_runs_on_file = 1;
  long input_sizes[] = {
      100000000, 97500000, 95000000, 92500000, 90000000, 87500000, 85000000,
      82500000,  80000000, 77500000, 75000000, 72500000, 70000000, 67500000,
      65000000,  62500000, 60000000, 57500000, 55000000, 52500000, 50000000,
      47500000,  45000000, 42500000, 40000000, 37500000, 35000000, 32500000,
      30000000,  27500000, 25000000, 22500000, 20000000, 17500000, 15000000,
      12500000,  10000000, 7500000,  5000000,  2500000};
  int block_sizes[] = {10000, 100000, 1000000, 10000000};
  int max_classical = 500000000;
  int internal_sort_options[] = {1};

  // Set for the distribution/blocksizes internal sort comparison
  // and comparison function comparison analysis for testing
  /*
  int num_different_files = 60;  // or 1 for distribution over one file
  int num_runs_on_file = 1;  // or 40 for distribution over one file
  long input_sizes[] = {10000, 100000, 1000000, 10000000};
  int block_sizes[] = {10000, 100000, 1000000, 10000000};
  int max_classical = 10000000;
  // Toggle for the internal sorting phase of the External Memory Merge Sort
  algorithm
  // 0 means use Classical Merge Sort
  // 1 means use qsort with naive integer comparison
  // 2 means use qsort with binary integer comparison
  int internal_sort_options[] = {0};  // 0, 1, 2
  */

  // We can and need to fit three blocks in our memory. We will use this to
  // speed up the initial partition (phase 1).
  int blocks_in_memory = 3;

  // clear_file("../res/results.txt");

  printf("%15s %15s %15s %18s %18s %15s %15s %15s %15s %15s %15s %15s %25s\n\n",
         "File_Seed", "Input_Size", "Block_Size", "Input_MB", "Block_MB",
         "Elapsed_Wall", "Elapsed_CPU", "Classical_Wall", "Classical_CPU",
         "Merge_Rounds", "Classical_Rounds", "Sort_Option", "Host_Name");
  // Append to result file (disabled for LogStash configuration format)
  /*
  FILE *file;
  file = fopen("../res/results.txt", "a");
  if (file == NULL) {
    printf("Error opening file.\n");
    exit(1);
  }
  fprintf(
      file,
      "%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %25s\n\n",
      "File_Seed", "Input_Size", "Block_Size", "Input_MB", "Block_MB",
      "Elapsed_Wall", "Elapsed_CPU", "Classical_Wall", "Classical_CPU",
      "Merge_Rounds", "Classical_Rounds", "Sort_Option", "Host_Name");
  fclose(file);
  */

  for (int c = 0;
       c < sizeof(internal_sort_options) / sizeof(internal_sort_options[0]);
       c++) {
    int internal_sort_option = internal_sort_options[c];
    for (int file_count = 0; file_count < num_different_files; file_count++) {
      for (int i = 0; i < sizeof(input_sizes) / sizeof(input_sizes[0]); i++) {
        long input_size = input_sizes[i];
        for (int j = 0; j < sizeof(block_sizes) / sizeof(block_sizes[0]); j++) {
          int block_size = block_sizes[j];
          /*
          if (block_size > input_size)
          {
              continue;
          }
          */
          for (int run = 0; run < num_runs_on_file; run++) {
            // Set random seed for current input file
            srand(file_count);

            // Create input file
            FILE *input_fp = fopen("../bin/input.bin", "wb");
            if (input_fp == NULL) {
              printf("Error opening input file.\n");
              return;
            }

            long stream_block_size = blocks_in_memory * block_size;

            // Create input file {
            for (long long i = 0; i < input_size; i++) {
              int random_number = rand();
              fwrite(&random_number, sizeof(int), 1, input_fp);
            }
            fclose(input_fp);
            // Create input file }

            char *input_file = "../bin/input.bin";
            char *output_file = "../bin/output.bin";

            struct timeval start_wall, end_wall, classical_start_wall,
                classical_end_wall;
            clock_t start_cpu, end_cpu, classical_start_cpu, classical_end_cpu;
            long seconds, useconds, classical_seconds, classical_useconds;
            double elapsed_wall, elapsed_cpu, classical_elapsed_wall,
                classical_elapsed_cpu;

            // Run classical merge sort if the input file is small enough
            int classical_merge_rounds = 0;
            if (input_size <= max_classical) {
              // Measure time
              gettimeofday(&classical_start_wall, NULL);
              classical_start_cpu = clock();
              classical_merge_rounds =
                  initial_partition(input_file, output_file, input_size,
                                    1 /* block(s) in memory */, input_size, 0);
              // Measure time
              classical_end_cpu = clock();
              gettimeofday(&classical_end_wall, NULL);
              classical_seconds =
                  classical_end_wall.tv_sec - classical_start_wall.tv_sec;
              classical_useconds =
                  classical_end_wall.tv_usec - classical_start_wall.tv_usec;
              classical_elapsed_wall =
                  classical_seconds + classical_useconds / 1000000.0;
              classical_elapsed_cpu =
                  ((double)(classical_end_cpu - classical_start_cpu)) /
                  CLOCKS_PER_SEC;
            } else {
              classical_elapsed_wall = nan("0");
              classical_elapsed_cpu = nan("0");
            }

            // Measure time
            gettimeofday(&start_wall, NULL);
            start_cpu = clock();

            // Perform phase 1
            initial_partition(input_file, output_file, block_size,
                              blocks_in_memory, input_size,
                              internal_sort_option);

            clear_file(input_file);

            // Switch roles of input_file and output_file
            char *temp_fp = input_file;
            input_file = output_file;
            output_file = temp_fp;

            int merge_rounds = 0;

            // Perform phase 2
            while (stream_block_size < input_size) {
              merge_rounds++;
              merge_round(input_file, output_file, input_size,
                          stream_block_size, block_size);

              // Clear contents of the first parameter file
              FILE *input_fp = fopen(input_file, "wb");
              if (input_fp == NULL) {
                printf("Error opening input file.\n");
                return;
              }
              fclose(input_fp);

              // Switch roles of input_file and output_file
              char *temp_fp = input_file;
              input_file = output_file;
              output_file = temp_fp;

              stream_block_size *= 2;
            }

            // Measure time
            end_cpu = clock();
            gettimeofday(&end_wall, NULL);
            seconds = end_wall.tv_sec - start_wall.tv_sec;
            useconds = end_wall.tv_usec - start_wall.tv_usec;
            elapsed_wall = seconds + useconds / 1000000.0;
            elapsed_cpu = ((double)(end_cpu - start_cpu)) / CLOCKS_PER_SEC;

            // Get host name
            char hostname[256];
            if (gethostname(hostname, sizeof(hostname)) != 0) {
              perror("Error getting hostname");
              exit(1);
            }

            printf("%15d,%15ld,%15ld,%15.2f MB,%15.2f "
                   "MB,%15.6f,%15.6f,%15.6f,%15.6f,%15d,%15d,%15d,%25s\n",
                   file_count, (long)input_size, (long)block_size,
                   input_size / 250000.0, block_size / 250000.0, elapsed_wall,
                   elapsed_cpu, classical_elapsed_wall, classical_elapsed_cpu,
                   merge_rounds, classical_merge_rounds, internal_sort_option,
                   hostname);

            // Append to result file
            FILE *file;
            file = fopen("../res/results.txt", "a");
            if (file == NULL) {
              printf("Error opening file.\n");
              exit(1);
            }
            fprintf(file,
                    "%15d,%15ld,%15ld,%15.2f MB,%15.2f "
                    "MB,%15.6f,%15.6f,%15.6f,%15.6f,%15d,%15d,%15d,%25s\n",
                    file_count, (long)input_size, (long)block_size,
                    input_size / 250000.0, block_size / 250000.0, elapsed_wall,
                    elapsed_cpu, classical_elapsed_wall, classical_elapsed_cpu,
                    merge_rounds, classical_merge_rounds, internal_sort_option,
                    hostname);
            fclose(file);
#if GLOBAL_STEP
            while (getchar() != '\n') {
            }
#endif
          }
        }
      }
    }
  }
}

int main() {
  int do_test = 0;
  do_test ? test_merge_round() : perform_analysis();
  return 0;
}
