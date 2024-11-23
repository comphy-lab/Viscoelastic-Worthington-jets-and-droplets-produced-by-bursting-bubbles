/* Title: getting Data from simulation snapshot
# Author: Vatsal Sanjay
# vatsalsanjay@gmail.com
# Physics of Fluids
*/
#include "axi.h"
#include "navier-stokes/centered.h"
#include "fractions.h"
#include "two-phase.h"
#include "log-conform-elastic_v5.h"
#include "curvature.h"

char filename[80], nameTrack[80];
scalar * list = NULL;

int main(int a, char const *arguments[])
{
  sprintf (filename, "%s", arguments[1]);
//   sprintf(nameTrack, "%s", arguments[2]);

  restore (file = filename);
  boundary((scalar *){f, u.x, u.y});

  face vector s[];
  s.x.i = -1;

  scalar kappa[];
  curvature(f, kappa);
  double xcmax = 0.0, ycmax = 0.0;
  double kappamax = -HUGE;
  double D33avg = 0.0;
  // Finding the tip position
  foreach(){
    if (kappa[] != nodata && x < 0. && f[] < 1-1e-6 && y > 0.3 && x > -1.5)
    {   kappa[] = -kappa[];
        if (kappa[] > kappamax)
        {
            kappamax = kappa[];
            xcmax = x;
            ycmax = y;
        }
      //fprintf(ferr, "%f %f %f %f\n", x, y, f[], kappa[]);
    }
  }

  foreach(){
    if (y < ycmax && x == xcmax){
       double D33 = (u.x[1,0] - u.x[-1,0])/(2*Delta);
       D33avg += D33 * 2 * pi * Delta * y;
    }
  }
  

  FILE * fp = ferr;
  fprintf(ferr, "%f %7.6e %7.6e %7.6e\n", t,  xcmax, ycmax, D33avg/(pi*ycmax*ycmax));
  //fprintf(ferr, "%7.6e %7.6e\n", xcmax, ycmax);
  fflush (fp);
  fclose (fp);

}