#C++ compiler
CPP=g++
#C compiler
CC=gcc
#Compiler flags
CFLAGS=-c -O3 -Wall
#Path to NLLoc source - default is to use code included with the distribution, but newer versions may be available
NLLOC_PATH=NLLoc_code

all: GetNLLOCScatterAngles

GetNLLOCScatterAngles: ran1.o alomax_matrix.o alomax_matrix_svd.o matrix_statistics.o octtree.o vector.o GridLib.o map_project.o util.o geo.o GetAngles.o

	$(CPP) -o GetNLLOCScatterAngles GetAngles.o GridLib.o util.o geo.o map_project.o ran1.o alomax_matrix.o alomax_matrix_svd.o matrix_statistics.o octtree.o vector.o

GetAngles.o: GetAngles.cpp

	$(CPP) $(CFLAGS) -I $(NLLOC_PATH) GetAngles.cpp -o GetAngles.o

ran1.o: ran1.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/ran1/ran1.c -o ran1.o

alomax_matrix.o: alomax_matrix.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/alomax_matrix/alomax_matrix.c -o alomax_matrix.o

alomax_matrix_svd.o: alomax_matrix_svd.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/alomax_matrix/alomax_matrix_svd.c -o alomax_matrix_svd.o

matrix_statistics.o: matrix_statistics.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/matrix_statistics/matrix_statistics.c -o matrix_statistics.o

octtree.o: octtree.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/octtree/octtree.c -o octtree.o

vector.o: vector.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/vector/vector.c -o vector.o

GridLib.o: GridLib.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/GridLib.c -o GridLib.o

map_project.o: map_project.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/map_project.c -o map_project.o

util.o: util.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/util.c -o util.o

geo.o: geo.c
	
	$(CC) $(CFLAGS) $(NLLOC_PATH)/geo.c -o geo.o