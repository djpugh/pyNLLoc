BINPATH="./"
NLLOC_PATH="NLLoc_code"
rm GetAngles.o
gcc -c -O3 -Wall $NLLOC_PATH/ran1/ran1.c -o $NLLOC_PATH/ran1/ran1.o
gcc -c -O3 -Wall $NLLOC_PATH/alomax_matrix/alomax_matrix.c -o $NLLOC_PATH/alomax_matrix/alomax_matrix.o
gcc -c -O3 -Wall $NLLOC_PATH/alomax_matrix/alomax_matrix_svd.c -o $NLLOC_PATH/alomax_matrix/alomax_matrix_svd.o
gcc -c -O3 -Wall $NLLOC_PATH/matrix_statistics/matrix_statistics.c -o $NLLOC_PATH/matrix_statistics/matrix_statistics.o
gcc -c -O3 -Wall $NLLOC_PATH/octtree/octtree.c -o $NLLOC_PATH/octtree/octtree.o
gcc -c -O3 -Wall $NLLOC_PATH/vector/vector.c -o $NLLOC_PATH/vector/vector.o
gcc -c -O3 -Wall $NLLOC_PATH/GridLib.c -o $NLLOC_PATH/GridLib.o
gcc -c -O3 -Wall $NLLOC_PATH/map_project.c -o $NLLOC_PATH/map_project.o
gcc -c -O3 -Wall $NLLOC_PATH/util.c -o $NLLOC_PATH/util.o
gcc -c -O3 -Wall $NLLOC_PATH/geo.c -o $NLLOC_PATH/geo.o
g++ -c -O3 -I $NLLOC_PATH GetAngles.cpp
g++ -o $BINPATH/GetNLLOCScatterAngles GetAngles.o $NLLOC_PATH/GridLib.o $NLLOC_PATH/util.o $NLLOC_PATH/geo.o $NLLOC_PATH/map_project.o $NLLOC_PATH/ran1/ran1.o $NLLOC_PATH/alomax_matrix/alomax_matrix.o $NLLOC_PATH/alomax_matrix/alomax_matrix_svd.o $NLLOC_PATH/matrix_statistics/matrix_statistics.o $NLLOC_PATH/octtree/octtree.o $NLLOC_PATH/vector/vector.o

