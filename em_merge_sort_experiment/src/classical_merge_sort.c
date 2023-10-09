#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define DEBUG 0

int classical_merge_sort(int *arr, int n) {
  int merge_rounds = 0;
  int curr_size;
  int left_start;

  for (curr_size = 1; curr_size <= n - 1; curr_size = 2 * curr_size) {
    merge_rounds++;
    for (left_start = 0; left_start < n - 1; left_start += 2 * curr_size) {
      int mid = left_start + curr_size - 1;
      int right_end = (left_start + 2 * curr_size - 1 < n - 1)
                          ? (left_start + 2 * curr_size - 1)
                          : (n - 1);
      mid = (mid > right_end) ? right_end : mid;
      int n1 = mid - left_start + 1;
      int n2 = right_end - mid;
#if DEBUG
      printf("%d %d %d %d %d %d\n", n1, n2, left_start, mid, right_end,
             curr_size);
      while (getchar() != '\n') {
      }
#endif
      int *left = (int *)malloc(n1 * sizeof(int));
      int *right = (int *)malloc(n2 * sizeof(int));

      for (int i = 0; i < n1; i++)
        left[i] = arr[left_start + i];
      for (int i = 0; i < n2; i++)
        right[i] = arr[mid + 1 + i];

      int i = 0, j = 0, k = left_start;
      while (i < n1 && j < n2) {
        if (left[i] <= right[j])
          arr[k++] = left[i++];
        else
          arr[k++] = right[j++];
      }

      while (i < n1)
        arr[k++] = left[i++];
      while (j < n2)
        arr[k++] = right[j++];

      free(left);
      free(right);
    }
  }
  return merge_rounds;
}

void printSortedFile(char *file_path, int n) {
  FILE *file = fopen(file_path, "rb");
  if (file == NULL) {
    perror("Error opening file");
    exit(1);
  }

  int *arr = (int *)malloc(n * sizeof(int));
  fread(arr, sizeof(int), n, file);

  printf("Sorted Array:\n");
  for (int i = 0; i < n; i++) {
    printf("%d ", arr[i]);
  }
  printf("\n");

  fclose(file);
  free(arr);
}

/*
int main()
{


// Specify input sizes and random seed

int input_sizes[] = {10000000};
// int input_sizes[] = {200000000, 1000000000};

// Loop over specified input sizes
for (int i = 0; i < sizeof(input_sizes) / sizeof(int); i++)
{
    int input_size = input_sizes[i];

    // Generate random integers
    srand(input_size);
    int *arr = (int *)malloc(input_size * sizeof(int));
    for (int j = 0; j < input_size; j++)
    {
        arr[j] = rand();
    }

    // Save random integers to binary input file
    char input_file[20];
    sprintf(input_file, "input_%d.bin", input_size / 250000);
    FILE *f_in = fopen(input_file, "wb");
    fwrite(arr, sizeof(int), input_size, f_in);
    fclose(f_in);

    // Perform classical merge sort
    classical_merge_sort(arr, input_size);

    // Save sorted integers to binary output file
    char output_file[20];
    sprintf(output_file, "output_%d.bin", input_size);
    FILE *f_out = fopen(output_file, "wb");
    fwrite(arr, sizeof(int), input_size, f_out);
    fclose(f_out);

#if DEBUG
    // Print sorted file for inspection
    // printSortedFile(output_file, input_size);
#endif
    free(arr);
}

return 0;
}
*/
