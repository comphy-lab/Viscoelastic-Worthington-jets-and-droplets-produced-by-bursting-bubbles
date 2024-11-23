// Get total number of cells

#include "navier-stokes/centered.h"
#include "fractions.h"

scalar f[];
char filename[80];
int main(int a, char const *arguments[])
{
  sprintf (filename, "%s", arguments[1]);
  restore (file = filename);
  #if TREE
    f.prolongation = fraction_refine;
  #endif
  boundary((scalar *){f});

  int cellcount = 0;
  double vol = 0.0;
  foreach(){
    cellcount++;
    vol += Delta*Delta;
  }

  fprintf(ferr, "%d %g\n", cellcount, vol);
}
