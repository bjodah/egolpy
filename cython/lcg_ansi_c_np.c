// Author: Björn Dahlgren
// You are free to use the code without restrictions.

void vb_lcg(long n, int seed);
int main(int argc, char *argv[]);

#include <stdlib.h>
#include <stdio.h>

void vb_lcg(long n, int seed){
  int i;
  for (i = 1; i<n; i++){
    seed=(1140671485*seed + 12820163) % 16777216;
  }
  printf("%i", seed);
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
