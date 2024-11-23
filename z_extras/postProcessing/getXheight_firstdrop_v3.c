/* Title: Calculating the jet height
# Authors: Vatsal Sanjay & Ayush Dixit
# vatsalsanjay@gmail.com
# Physics of Fluids
*/
#include "axi.h"
#include "navier-stokes/centered.h"
#include "vof.h"
#include "tag.h"
#include "heights.h"
#include "curvature.h"

// #include "droplet_stat.h"


char filename[80], nameTrack[80];
scalar f[], * interfaces = {f};

// First argument should be filename.
int main(int a, char const *arguments[])
{
  sprintf (filename, "%s", arguments[1]);
  sprintf(nameTrack, "%s", arguments[2]);

  restore (file = filename);
  boundary((scalar *){f, u.x, u.y});

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
  // tag all liquid parts ends

    // n is number of droplets
    // Volume and position of each droplet
    double v[n];
    coord b[n];
    for (int j = 0; j < n; j++)
        v[j] = b[j].x = b[j].y = b[j].z = 0.;

    foreach (serial)
        if (d[] > 0)
        {
            int j = d[] - 1;
            double vtemp;
            coord p = {x, y, z};
            vtemp = 2 * pi * p.y * Delta * Delta * f[];
            v[j] += vtemp; //v[j] += dv() * f[];
            foreach_dimension()
                b[j].x +=  vtemp * p.x;
        }
#if _MPI
    MPI_Allreduce(MPI_IN_PLACE, v, n, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
    MPI_Allreduce(MPI_IN_PLACE, b, 3 * n, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
#endif

    // Number of droplets above x = 0 is nn
    int nn = 0;   
      for (int i = 0; i < n; i++)
    {
      if (b[i].x/v[i]>0 && v[i]>3e-4) nn++;
    }
  
  face vector s[];
  s.x.i = -1;
  double yMin = 0.2;
  double vTip, xTP = -30;
  double yTP = 0;
  scalar kappa[];
  curvature(f, kappa);
  double xcmax = 0.0, ycmax = 0.0;
  double kappamax = -HUGE;

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

    if (f[] > 1e-6 && f[] < 1. - 1e-6 && d[] == MainPhase) {
      coord n1 = facet_normal (point, f, s);
      double alpha1 = plane_alpha (f[], n1);
      coord segment1[2];
      if (facets (n1, alpha1, segment1) == 2){
        double x1 = x + (segment1[0].x+segment1[1].x)*Delta/2.;
        double y1 = y + (segment1[0].y+segment1[1].y)*Delta/2.;
        if (y1 < yMin && x1 > xTP){
          yTP = y1;
          xTP = x1;
          vTip = u.y[];
        }
      }
    }
  }

  

  FILE * fp = ferr;
  fprintf(ferr, "%f %7.6e %7.6e %7.6e %7.6e %7.6e %d\n", t, xTP, yTP, vTip, xcmax, ycmax, nn);
  //fprintf(ferr, "%7.6e %7.6e\n", xcmax, ycmax);
  fflush (fp);
  fclose (fp);

  FILE *fp2;
  fp2 = fopen (nameTrack, "a");
  //fprintf(fp2, "%f %7.6e %7.6e %7.6e\n", t, xTP, yMin, vTip);
  fclose(fp2);

}
