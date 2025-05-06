/**
# Simulation Data Extraction and Processing

This program extracts and processes data from fluid dynamics simulation
snapshots, specifically designed for viscoelastic fluid simulations with
conformation tensor analysis. It computes important derived quantities
including deformation rate tensor components, velocity magnitude, and
conformation tensor trace.

The program interpolates these quantities onto a regular grid and outputs
the results for further analysis or visualization.

## Physics Background

This code handles viscoelastic fluid simulation data where the fluid
stress tensor includes both a viscous component (proportional to the
deformation rate) and an elastic component (represented by the conformation
tensor). The trace of the conformation tensor provides a measure of
polymer stretching in the fluid.
*/

#include "utils.h"
#include "output.h"

scalar f[];            // Volume fraction field
vector u[];            // Velocity field
scalar A11[], A12[], A22[]; // Conformation tensor components
scalar conform_qq[];   // Additional conformation tensor component

char filename[80];     // Input file name
int nx, ny, len;       // Grid dimensions and field count
double xmin, ymin, xmax, ymax, Deltax, Deltay; // Domain boundaries and grid spacing

/** 
### Derived Fields

- D2c: Log10 of squared deformation rate tensor weighted by volume fraction
- vel: Magnitude of velocity
- trA: Log10 of excess trace of conformation tensor
*/
scalar D2c[], vel[], trA[];
scalar * list = NULL;  // List to store output fields

/**
### Main Function

Processes simulation data and computes derived quantities

- Arguments:
  - arguments[1]: Input filename
  - arguments[2-5]: Domain boundaries (xmin, ymin, xmax, ymax)
  - arguments[6]: Number of grid points in y-direction (ny)

- Returns:
  - 0 on successful execution
*/
int main(int a, char const *arguments[])
{
  sprintf(filename, "%s", arguments[1]);
  xmin = atof(arguments[2]); ymin = atof(arguments[3]);
  xmax = atof(arguments[4]); ymax = atof(arguments[5]);
  ny = atoi(arguments[6]);

  // Initialize list of fields to output
  list = list_add(list, D2c);
  list = list_add(list, vel);
  list = list_add(list, trA);

  /**
## Data Processing Workflow

1. Restore simulation state from snapshot file
2. Compute derived quantities at each grid point
3. Interpolate fields onto regular grid
4. Output data to file
*/
  restore(file = filename);

  /**
### Field Computation

For each cell, compute:
- Components of the deformation rate tensor D
- Squared magnitude of D weighted by volume fraction
- Velocity magnitude
- Excess trace of the conformation tensor
*/
  foreach() {
    // Compute deformation rate tensor components
    double D11 = (u.y[0, 1] - u.y[0, -1]) / (2 * Delta);
    double D22 = (u.y[] / y);
    double D33 = (u.x[1, 0] - u.x[-1, 0]) / (2 * Delta);
    double D13 = 0.5 * ((u.y[1, 0] - u.y[-1, 0] + u.x[0, 1] - u.x[0, -1]) / 
                        (2 * Delta));
    double D2 = (sq(D11) + sq(D22) + sq(D33) + 2.0 * sq(D13));
    D2c[] = f[] * D2;
    
    // Take log10 of D2c for better visualization
    if (D2c[] > 0.) {
      D2c[] = log(D2c[]) / log(10);
    } else {
      D2c[] = -10;
    }

    // Compute velocity magnitude
    vel[] = sqrt(sq(u.x[]) + sq(u.y[]));

    // Compute excess trace of conformation tensor
    trA[] = (A11[] + A22[] + conform_qq[]) / 3.0 - 1.0;

    // Take log10 of trA for better visualization
    if (trA[] > 0.) {
      trA[] = log(trA[]) / log(10);
    } else {
      trA[] = -10;
    }
  }

  /**
### Grid Interpolation and Output

1. Calculate grid spacing based on domain size and ny
2. Allocate memory for interpolated field values
3. Interpolate field values onto regular grid
4. Output grid coordinates and field values
*/
  FILE * fp = ferr;
  Deltay = (double)((ymax - ymin) / (ny));
  nx = (int)((xmax - xmin) / Deltay);
  Deltax = (double)((xmax - xmin) / (nx));
  len = list_len(list);
  
  // Allocate memory for field values
  double ** field = (double **) matrix_new(nx, ny + 1, len * sizeof(double));
  
  // Interpolate field values onto regular grid
  for (int i = 0; i < nx; i++) {
    double x = Deltax * (i + 1./2) + xmin;
    for (int j = 0; j < ny; j++) {
      double y = Deltay * (j + 1./2) + ymin;
      int k = 0;
      for (scalar s in list) {
        field[i][len * j + k++] = interpolate(s, x, y);
      }
    }
  }

  // Output grid coordinates and field values
  for (int i = 0; i < nx; i++) {
    double x = Deltax * (i + 1./2) + xmin;
    for (int j = 0; j < ny; j++) {
      double y = Deltay * (j + 1./2) + ymin;
      fprintf(fp, "%g %g", x, y);
      int k = 0;
      for (scalar s in list) {
        fprintf(fp, " %g", field[i][len * j + k++]);
      }
      fputc('\n', fp);
    }
  }
  
  // Clean up
  fflush(fp);
  fclose(fp);
  matrix_free(field);
  
  return 0;
}