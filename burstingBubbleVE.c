/**
 * @file burstingBubbleVE.c
 * @brief This file contains the simulation code for the bursting bubble in viscoelastic media.
 * @author Vatsal Sanjay and Ayush Dixit
 * @version 1.0
 * @date Nov 23, 2024
*/

#include "axi.h"
#include "navier-stokes/centered.h"

/*
see: V. Sanjay, Zenodo, DOI: 10.5281/zenodo.14210635 (2024) for details
*/
#if !_SCALAR
#include "src-local/log-conform-viscoelastic.h" 
#else 
#include "src-local/log-conform-viscoelastic-scalar-2D.h"
#endif

#define FILTERED // Smear density and viscosity jumps
#include "src-local/two-phaseVE.h"
#include "navier-stokes/conserving.h"
#include "tension.h"

#if !_MPI
#include "distance.h"
#endif

#define tsnap (1e-2) // 0.001 only for some cases. 
// Error tolerancs
#define fErr (1e-3)                                 // error tolerance in f1 VOF
#define KErr (1e-6)                                 // error tolerance in VoF curvature calculated using heigh function method (see adapt event)
#define VelErr (1e-3)                               // error tolerances in velocity -- Use 1e-2 for low Oh and 1e-3 to 5e-3 for high Oh/moderate to high J
#define AErr (1e-3)                             // error tolerances in conformation inside the liquid

// Numbers!
#define Ldomain 8

// boundary conditions - outflow on the right boundary
u.n[right] = neumann(0.);
p[right] = dirichlet(0.);

int MAXlevel;
// Oh -> Solvent Ohnesorge number
// Oha -> air Ohnesorge number
// De -> Deborah number
// Ec -> Elasto-capillary number

double Oh, Oha, De, Ec, Bond, tmax;
char nameOut[80], dumpFile[80];
scalar Gpd[]; scalar lambdad[];

int  main(int argc, char const *argv[]) {
  dtmax = 1e-5; //  BEWARE of this for stability issues. 

  L0 = Ldomain;
  origin (-L0/2., 0.);
  
  // Values taken from the terminal
  MAXlevel = atoi(argv[1]);
  De = atof(argv[2]); // Use a value of 1e30 to simulate the De \to \infty limit. 
  Ec = atof(argv[3]);
  Oh = atof(argv[4]);
  Bond = atof(argv[5]);
  tmax = atof(argv[6]);

  // Ensure that all the variables were transferred properly from the terminal or job script.
  if (argc < 7){
    fprintf(ferr, "Lack of command line arguments. Check! Need %d more arguments\n", 7-argc);
    return 1;
  }
  init_grid (1 << 5);
  // Create a folder named intermediate where all the simulation snapshots are stored.
  char comm[80];
  sprintf (comm, "mkdir -p intermediate");
  system(comm);
  // Name of the restart file. See writingFiles event.
  sprintf (dumpFile, "dump");


  rho1 = 1., rho2 = 1e-3;
  Oha = 2e-2 * Oh;
  mu1 = Oh, mu2 = Oha;
  lambda1 = De; lambda2 = 0.;
  G1 = Ec; G2 = 0.;

  f.sigma = 1.0;

  // polymers
  Gp = Gpd;
  lambda = lambdad;

  run();
}

event init (t = 0) {
#if _MPI // this is for supercomputers without OpenMP support
  if (!restore (file = dumpFile)){
    fprintf(ferr, "Cannot restored from a dump file!\n");
  }
#else
  if (!restore (file = dumpFile)){
      char filename[60];
      sprintf(filename,"Bo%5.4f.dat",Bond);
      FILE * fp = fopen(filename,"rb");
      if (fp == NULL){
        fprintf(ferr, "There is no file named %s\n", filename);
        return 1;
      }
      coord* InitialShape;
      InitialShape = input_xy(fp);
      fclose (fp);
      scalar d[];
      distance (d, InitialShape);

      while (adapt_wavelet ((scalar *){f, d}, (double[]){1e-8, 1e-8}, MAXlevel).nf);
      
    // The distance function is defined at the center of each cell, we have
    // to calculate the value of this function at each vertex. 
      vertex scalar phi[];
      foreach_vertex(){
        phi[] = -(d[] + d[-1] + d[0,-1] + d[-1,-1])/4.;
      }
      
    // We can now initialize the volume fraction of the domain. 
      fractions (phi, f);
    }
  // return 1;
#endif
}

/**
## Adaptive Mesh Refinement
*/
event adapt(i++){
  scalar KAPPA[];
  curvature(f, KAPPA);

  #if !_SCALAR
   adapt_wavelet ((scalar *){f, u.x, u.y, conform_p.x.x, conform_p.y.y, conform_p.y.x, conform_qq, KAPPA},
      (double[]){fErr, VelErr, VelErr, AErr, AErr, AErr, AErr, KErr},
      MAXlevel, MAXlevel-6);
  #else
   adapt_wavelet ((scalar *){f, u.x, u.y, A11, A22, A12, AThTh, KAPPA},
      (double[]){fErr, VelErr, VelErr, AErr, AErr, AErr, AErr, KErr},
      MAXlevel, MAXlevel-6);
  #endif
}

/**
## Dumping snapshots
*/
event writingFiles (t = 0; t += tsnap; t <= tmax) {
  dump (file = dumpFile);
  sprintf (nameOut, "intermediate/snapshot-%5.4f", t);
  dump(file=nameOut);
}

/**
## Ending Simulation
*/
event end (t = end) {
  if (pid() == 0)
    fprintf(ferr, "Level %d, De %2.1e, Ec %2.1e, Oh %2.1e, Oha %2.1e, Bo %4.3f\n", MAXlevel, De, Ec, Oh, Oha, Bond);
}

/**
## Log writing
*/
event logWriting (i++) {

  double ke = 0.;
  foreach (reduction(+:ke)){
    ke += (2*pi*y)*(0.5*rho(f[])*(sq(u.x[]) + sq(u.y[])))*sq(Delta);
  }
  if (pid() == 0) {
    static FILE * fp;
    if (i == 0) {
      fprintf(ferr, "Level %d, De %2.1e, Ec %2.1e, Oh %2.1e, Oha %2.1e, Bo %4.3f\n", MAXlevel, De, Ec, Oh, Oha, Bond);
      fprintf (ferr, "De Ec Oh i dt t ke\n");
      fp = fopen ("log", "w");
      fprintf(fp, "Level %d, De %2.1e, Ec %2.1e, Oh %2.1e, Oha %2.1e, Bo %4.3f\n", MAXlevel, De, Ec, Oh, Oha, Bond);
      fprintf (fp, "i dt t ke\n");
      fprintf (fp, "%d %g %g %g\n", i, dt, t, ke);
      fclose(fp);
    } else {
      fp = fopen ("log", "a");
      fprintf (fp, "%g %g %g %d %g %g %g\n", De, Ec, Oh, i, dt, t, ke);
      fclose(fp);
    }
    fprintf (ferr, "%g %g %g %d %g %g %g\n", De, Ec, Oh, i, dt, t, ke);

  assert(ke > -1e-10);

  if (ke > 1e2 && i > 1e1){
    if (pid() == 0){
      fprintf(ferr, "The kinetic energy blew up. Stopping simulation\n");
      fp = fopen ("log", "a");
      fprintf(fp, "The kinetic energy blew up. Stopping simulation\n");
      fclose(fp);
      dump(file=dumpFile);
      return 1;
    }
  }
  assert(ke < 1e2);
  
  if (ke < 1e-6 && i > 1e1){
    if (pid() == 0){
      fprintf(ferr, "kinetic energy too small now! Stopping!\n");
      dump(file=dumpFile);
      fp = fopen ("log", "a");
      fprintf(fp, "kinetic energy too small now! Stopping!\n");
      fclose(fp);
      return 1;
    }
  }
  }
}
