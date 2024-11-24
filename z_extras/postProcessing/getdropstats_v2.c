// Getting Droplet statistics

#include "axi.h"
#include "navier-stokes/centered.h"
#include "fractions.h"
#include "tag.h"

scalar f[], *interfaces = {f};
char filename[80];

int main(int a, char const *arguments[])
{
    sprintf(filename, "%s", arguments[1]);
    restore(file = filename);
    f.prolongation = fraction_refine;
    boundary((scalar *){f, u.x, u.y});

    scalar m[];
    foreach ()
        m[] = f[] > 1e-3;

    int n = tag(m);

    // n is number of droplets
    // Volume and position of each droplet
    double v[n];
    coord b[n];
    for (int j = 0; j < n; j++)
        v[j] = b[j].x = b[j].y = b[j].z = 0.;

    foreach (serial)
        if (m[] > 0)
        {
            int j = m[] - 1;
            double vtemp;
            coord p = {x, y, z};
            vtemp = 2 * pi * p.y * Delta * Delta * f[];
            v[j] += vtemp; //v[j] += dv() * f[];
            foreach_dimension()
                b[j].x +=  vtemp * p.x;
        }

// Get volumes and positions which span multiple processors
#if _MPI
    MPI_Allreduce(MPI_IN_PLACE, v, n, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
    MPI_Allreduce(MPI_IN_PLACE, b, 3 * n, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
#endif
    int droptag = 0;

    for (int i = 0; i < n; i++)
    {
        if (b[i].x / v[i] > b[droptag].x / v[droptag])
        {
            droptag = i;
        }
    }

    FILE *fp = fout;

    // for (int j = 0; j < n; j++)
    // {
    //     fprintf(ferr, "%g %d %g %g %g\n", t, j, v[j], b[j].x / v[j], b[j].y / v[j]);
    // }
     if (n > 1 && b[droptag].x / v[droptag] > -0.5 && v[droptag] > 3e-5)
     {
         int j = droptag;
         fprintf(ferr, "%g %d %g %g %g\n", t, j, v[j], b[j].x / v[j], b[j].y / v[j]);
     }
     //    }
    // fprintf all zero values
    else
    {
        int j = 0;
        fprintf(ferr, "%g %d %g %g %g\n", t, j, 0., 0., 0.);
    }
    fflush(fp);
    fclose(fp);
}
