// Author: Björn Dahlgren
// You are free to use the code without restrictions.

void vb_lcg(long n, int seed);
int main(int argc, char *argv[]);

#include <stdlib.h>
#include <stdio.h>

void vb_lcg(long n, int seed){
  int *data = malloc(n*sizeof(int));
  int i;
  data[0] = seed;
  for (i = 1; i<n; i++){
    data[i]=(1140671485*data[i-1] + 12820163) % 16777216;
  }
  for (i = n-10; i<n; i++){
    printf("%i ", data[i]);
  }
  free(data);
}

int main(int argc, char *argv[]){
  long n; int seed;
  printf("lcg: ");
  if (argc == 3){
    n    = atol(argv[1]);
    seed = atoi(argv[2]);
    printf("Generating pseduo numbers...\n");
    vb_lcg(n, seed);
  }
  else {
    do {
      printf("Enter how many pseudo random numbers you need:\n");
      scanf("%l", &n);
    } while(n != 0);
    printf("Enter a seed:\n");
    scanf("%i", &seed);
    printf("Generating pseduo numbers...\n");
    vb_lcg(n, seed);
  }
  printf("\n");
  return 0;
}
