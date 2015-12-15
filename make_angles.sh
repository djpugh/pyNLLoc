BINPATH="../../bin"
rm getAngles.o
gcc -c -O3 -Wall ran1/ran1.c -o ran1/ran1.o
gcc -c -O3 -Wall alomax_matrix/alomax_matrix.c -o alomax_matrix/alomax_matrix.o
gcc -c -O3 -Wall alomax_matrix/alomax_matrix_svd.c -o alomax_matrix/alomax_matrix_svd.o
gcc -c -O3 -Wall matrix_statistics/matrix_statistics.c -o matrix_statistics/matrix_statistics.o
gcc -c -O3 -Wall octtree/octtree.c -o octtree/octtree.o
gcc -c -O3 -Wall vector/vector.c -o vector/vector.o
gcc -c -O3 -Wall GridLib.c -o GridLib.o
gcc -c -O3 -Wall map_project.c -o map_project.o
gcc -c -O3 -Wall util.c -o util.o
gcc -c -O3 -Wall geo.c -o geo.o
g++ -c -O3 getAngles.cpp
g++ -o $BINPATH/GetNLLOCScatterAngles getAngles.o GridLib.o util.o geo.o map_project.o ran1/ran1.o alomax_matrix/alomax_matrix.o alomax_matrix/alomax_matrix_svd.o matrix_statistics/matrix_statistics.o octtree/octtree.o vector/vector.o

