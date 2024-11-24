#!/bin/bash
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
#SBATCH --job-name=219-260
#SBATCH --error=job.%J.err
#SBATCH --output=job.%J.out

source ~/.bashrc
MAXlevel="11"
Bond="1e-3"
tmax="1.7"


Ec=(" 4.000E-05 "  " 7.678E-05 "  " 1.474E-04 "  " 2.828E-04 "  " 5.429E-04 "  " 1.042E-03 "  " 4.000E-05 "  " 7.678E-05 "  
    " 1.474E-04 "  " 2.828E-04 "  " 5.429E-04 "  " 1.042E-03 "  " 4.000E-05 "  " 7.678E-05 "  " 1.474E-04 "  " 2.828E-04 "
    " 5.429E-04 "  " 1.042E-03 "  " 4.000E-05 "  " 7.678E-05 "  " 1.474E-04 "  " 2.828E-04 "  " 5.429E-04 "  " 1.042E-03 "
    " 4.000E-05 "  " 7.678E-05 "  " 1.474E-04 "  " 2.828E-04 "  " 5.429E-04 "  " 1.042E-03 "  " 4.000E-05 "  " 7.678E-05 "
    " 1.474E-04 "  " 2.828E-04 "  " 5.429E-04 "  " 1.042E-03 "  " 4.000E-05 "  " 7.678E-05 "  " 1.474E-04 "  " 2.828E-04 "
    " 5.429E-04 "  " 1.042E-03 " )

Oh=( " 1.000E-03 "  " 1.000E-03 "  " 1.000E-03 "  " 1.000E-03 "  " 1.000E-03 "  " 1.000E-03 "  " 1.472E-03 "  " 1.472E-03 "
     " 1.472E-03 "  " 1.472E-03 "  " 1.472E-03 "  " 1.472E-03 "  " 2.168E-03 "  " 2.168E-03 "  " 2.168E-03 "  " 2.168E-03 "
     " 2.168E-03 "  " 2.168E-03 "  " 3.192E-03 "  " 3.192E-03 "  " 3.192E-03 "  " 3.192E-03 "  " 3.192E-03 "  " 3.192E-03 "
     " 4.700E-03 "  " 4.700E-03 "  " 4.700E-03 "  " 4.700E-03 "  " 4.700E-03 "  " 4.700E-03 "  " 6.919E-03 "  " 6.919E-03 "
     " 6.919E-03 "  " 6.919E-03 "  " 6.919E-03 "  " 6.919E-03 "  " 1.019E-02 "  " 1.019E-02 "  " 1.019E-02 "  " 1.019E-02 "
     " 1.019E-02 "  " 1.019E-02 " )


#qcc -fopenmp -Wall -O2 burstingBubbleVE_ElasticLimit_v2.c -o burstingBubbleVE_ElasticLimit -lm

# qcc -Wall -O2 burstingBubbleVE_ElasticLimit_v2.c -o burstingBubbleVE_ElasticLimit -lm

start=219

for i in {0..2};
do
cd  $(printf "%03d" $((start+8*i)))
export OMP_NUM_THREADS=8
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+0]} ${Oh[8*i+0]} $Bond $tmax & 

cd ../
cd  $(printf "%03d" $((start+8*i+1)))
export OMP_NUM_THREADS=8
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+1]} ${Oh[8*i+1]} $Bond $tmax & 

cd ../
cd  $(printf "%03d" $((start+8*i+2)))
export OMP_NUM_THREADS=8
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+2]} ${Oh[8*i+2]} $Bond $tmax & 

cd ../
cd  $(printf "%03d" $((start+8*i+3)))
export OMP_NUM_THREADS=8
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+3]} ${Oh[8*i+3]} $Bond $tmax & 

cd ../
cd  $(printf "%03d" $((start+8*i+4)))
export OMP_NUM_THREADS=8
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+4]} ${Oh[8*i+4]} $Bond $tmax & 

cd ../
cd  $(printf "%03d" $((start+8*i+5)))
export OMP_NUM_THREADS=8
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+5]} ${Oh[8*i+5]} $Bond $tmax & 

cd ../
cd  $(printf "%03d" $((start+8*i+6)))
export OMP_NUM_THREADS=8
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+6]} ${Oh[8*i+6]} $Bond $tmax & 

cd ../
cd  $(printf "%03d" $((start+8*i+7)))
export OMP_NUM_THREADS=8
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+7]} ${Oh[8*i+7]} $Bond $tmax & 
wait
cd ../
done
