// getting base properties, curvature radius, D33_average(delw/delz) and sigma_33_average

#include "axi.h"
#include "navier-stokes/centered.h"
#include "fractions.h"
#include "two-phase.h"
#include "log-conform-elastic_v5.h"
#include "curvature.h"
#include "tag.h"

char filename[80], nameTrack[80];
scalar * list = NULL;

int main(int a, char const *arguments[])
{
  sprintf (filename, "%s", arguments[1]);

  restore (file = filename);
  boundary((scalar *){f, u.x, u.y});

  face vector s[];
  s.x.i = -1;

  scalar kappa[];
  curvature(f, kappa);
  double xmax = -HUGE;
  double utip;
  double momavg = 0., keavg = 0.;
  // Finding the tip position
  
  // tag all liquid parts starts
  // to tag all the liquid parts
  scalar d[];
  double threshold = 1e-4;
  // d array stores if the liquid is higher than threshold
  foreach(){
    d[] = (f[] > threshold);
  }

  // Any connected region for f > threshold is given a unique tag from 0 to n-1
  int n = tag (d), size[n];
  for (int i = 0; i < n; i++){
    size[i] = 0;
  }

  // size array stores the size of each connected region
  foreach_leaf(){
    if (d[] > 0){
      size[((int) d[]) - 1]++;
    }
  }

  // MainPhase is the tag of the largest connected region
  int MaxSize = 0;
  int MainPhase = 0;
  for (int i = 0; i < n; i++){
     // fprintf(ferr, "%d %d\n",i, size[i]);
    if (size[i] > MaxSize){
      MaxSize = size[i];
      MainPhase = i+1;
    }
  }

  foreach(){
    if (y < 0.01 && x > xmax && f[] > 1-1e-3 && d[] == MainPhase)
      {
        xmax = x;
        utip = u.x[];
      }

      
        momavg += (2 * pi * y) * rho(f[]) * u.x[] * sq(Delta);
        keavg += (2 * pi * y) * (0.5*rho(f[])*(sq(u.x[]) + sq(u.y[])))*sq(Delta);
      

  }

  FILE * fp = ferr;
  fprintf(ferr, "%f %7.6e %7.6e %7.6e %7.6e\n", t,  xmax, utip, momavg, keavg);
  fflush (fp);
  fclose (fp);

}
