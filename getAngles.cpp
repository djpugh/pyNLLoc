/*
 * Copyright (C) 2015 David J Pugh <david.j.pugh@cantab.net>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU GPL as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU GPL
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.

 */
/* 
        
        GetAngles.cpp - convert scatter location distribution to angle distribution

 */

/*-----------------------------------------------------------------------
David J Pugh
david.j.pugh@cantab.net
-------------------------------------------------------------------------*/
#include <string>
#include <vector>
#include <fstream>
#include <iostream>
#include <stdio.h>
#include <sstream>
//External C GridLib header from NonLinLoc
extern "C" {
    #include "GridLib.h"
}
using namespace std;
//Stations class - list of station objects and filenames and grid dimensions
class Stations{
    public:
        vector<string >filenames; //Filenames of the grids corresponding to each station
        vector<string >names;//Names of each station
        vector<int> dimension;//Dimension of the grid file (2D or 3D)
        vector<SourceDesc> srce;//NLLoc source object
};
//Class to handle an x,y,z point
class xyzNode{
public:
	double x;
	double y;
	double z;
	double p;
	xyzNode(float xf, float yf, float zf, float pf){
		this->x=xf;
		this->y=yf;
		this->z=zf;
		this->p=pf;
	}
};
//Class to handle a point with angles
class angleNode{
public:
	vector<vector<string> >stationAngles;
	double p;
	angleNode(vector<vector<string> >angles, double P)
	{
		this->stationAngles=angles;
		this->p=P;
	}
};
//Class to handle scatter files
class Scatter{
    public:
		vector<xyzNode > nodes;
		void addNode(float x, float y, float z, float p)
		{
			nodes.push_back(xyzNode(x,y,z,p));
		}
};
//Class to handle angle scatter file
class Angles{
    public:
		vector<angleNode > nodes;
		void addNode(vector<vector<string> > angles, double P)
		{
			nodes.push_back(angleNode(angles,P));
		}
		Angles(Stations sta,Scatter scatter){
            //Get angles for the recievers and scatter distribution
			int i;
			for (i=0;i<scatter.nodes.size();i++)
			{
                if (i % 100 ==0)
                {
                    cout<<"Retrieved Sample:"<<i<<" of "<<scatter.nodes.size()<<endl;//Print to terminal 
                }
                //Vector of resultant angles for each scatter point
                vector<vector <string> >stationAngles=getAngles(scatter.nodes[i].x,scatter.nodes[i].y,scatter.nodes[i].z,scatter.nodes[i].p,sta);
				this->addNode(stationAngles,scatter.nodes[i].p);
			}
		}
};
//Function for getting the angles for a given x,y,z point 
vector<vector<string > > getAngles(double x, double y, double z,double p,Stations sta) {
    int narr;
    int iSwapBytesOnInput=0;
   
    /* loop over arrivals */
    vector<vector<string > > stationAngles;
    ::SetConstants();//Set the constant values (NLLoc Gridlib fn)
    for (narr = 0; narr < sta.filenames.size(); narr++) {
        vector<string > angles;        
        std::ostringstream sstream;
        //Default values
        double ray_azim=10.0;
        double ray_dip=10.0;
        int ray_qual=0;
        double azimuth=0.0;
        double distance=0.0;
        //convert angle filename to c string
        char * filename=new char[sta.filenames[narr].size()+1];
        //Copy the filename into the station filenames object.
        copy(sta.filenames[narr].begin(),sta.filenames[narr].end(),filename);
        filename[sta.filenames[narr].size()]='\0';//Null terminate
        //Check station dimension
        if (sta.dimension[narr] == 2) {
            //2D so need to get distance and azimuth
            distance = ::GetEpiDist(&(sta.srce[narr]), x, y);
            azimuth = ::GetEpiAzim(&(sta.srce[narr]), x, y);//Receiver azimuth is calculated here not in the grid file (grid only contains take-off angles)
            if (GeometryMode == MODE_GLOBAL){distance = KM2DEG*distance;}//Convert Distance to degrees for global grids
            // cout <<" B 2D "<<distance<< " "<<azimuth<<endl; 
            //Read the angle for the distance and depth
            ::ReadTakeOffAnglesFile(filename,0.0,distance, z,&ray_azim,&ray_dip,&ray_qual, azimuth, iSwapBytesOnInput);
        }else{
            //3D
            //Read the angles for the x,y, and z values
            ::ReadTakeOffAnglesFile(filename,x, y, z,&ray_azim,&ray_dip,&ray_qual, -1.0, iSwapBytesOnInput);
        
        }
        //Add  angles name to output vector
        angles.push_back(sta.names[narr]);       
        ray_azim/=1.0;//Azim is in range 0-3600 in tenths of a degree      
        ray_dip/=1.0;//Dip is in range 0-1800 in tenths of a degree - 1800 is up
        //cout<<ray_dip<<"\t"<<ray_azim<<endl;
        sstream << ray_azim;
        sstream<<"\t";
        sstream << ray_dip;
        angles.push_back(sstream.str());
        stationAngles.push_back(angles);
        }
    //Return the station angles output
    return stationAngles;
    }
//Read stations
Stations readStationFile(string filename){
    //Read station files and return the a Stations object
	ifstream file;
	file.open(filename.c_str());
	Stations stations;
	int i,j;
	string line;
	if (file.is_open())
	{
		while ( file.good() )
		{
            //Loop over open and good data
			string stationName;
			string angleFile;
            string fn_hdr;
            string hdr(".hdr");
            //Get line from file
			getline (file,line);
            //i index of name and file name split
			i=line.find_first_of(":");
            //j index of end of file name
			j=line.find_first_of(";");
            //Get angle file and station name
			angleFile=line.substr(i+1,j-i-1);
			stationName=line.substr(0,i);
            if (stationName.length()>0)
            {
                //If the station name exists            
                //check 2D v. 3D
                //Using approach from NLLoc GridLib.c
                FILE * fp_hdr;
                ::GridDesc gdesc;
                ::SourceDesc srce;
                fn_hdr=angleFile;
                fn_hdr+=hdr;
                //Open grid header file
                fp_hdr=fopen(fn_hdr.c_str(),"r");
                if (fp_hdr == NULL) {
                    cout <<"WARNING: cannot open grid header file: "<<fn_hdr<<endl;
                }else{
                    //Check grid header file and read parameters
                    fscanf(fp_hdr, "%d %d %d  %lf %lf %lf  %lf %lf %lf %s %s",
                        &(gdesc.numx), &(gdesc.numy), &(gdesc.numz),
                        &(gdesc.origx), &(gdesc.origy), &(gdesc.origz),
                        &(gdesc.dx), &(gdesc.dy), &(gdesc.dz), gdesc.chr_type, gdesc.float_type);
                    fscanf(fp_hdr, "%s %lf %lf %lf\n",srce.label, &(srce.x), &(srce.y), &(srce.z));
                    fclose(fp_hdr);
                    
                    // make sure that dx for 2D grids is non-zero
                    if (gdesc.numx == 1){
                        gdesc.dx = 1.0;
                    }
                    convert_grid_type(&gdesc, 1);
                    //Add stations data to Stations object
                    stations.filenames.push_back(angleFile);
                    stations.names.push_back(stationName);
                    stations.srce.push_back(srce);
                    //Check grid description results
                    if (gdesc.type == GRID_ANGLE_2D) {
                        stations.dimension.push_back(2);
                        cout<<"Station|"<<stationName<<"| : Angle File Root|"<<angleFile <<"| 2D "<< endl;
                    }else{
                        stations.dimension.push_back(3);
                        cout<<"Station|"<<stationName<<"| : Angle File Root|"<<angleFile <<"| 3D "<< endl;
                    }
                }
            }
        }
	}
    //Close file
	file.close();
    //Return Station object
	return stations;
}
//Read scatter
Scatter readScatterFile(string filename){
    //Read scatter file and returns Scatter object
	ifstream file;
    //Print filename to std out
    cout<<filename<<endl;
    //Open binary file
	file.open(filename.c_str(),ios::in|ios::binary);
	char buffer[128];
    //Temporary values
	float xf;
	float yf;
	float zf;
	float pf;
	int nSamples; 
    float d;
    int i;
	Scatter scatter;
    //Read number of samples (as integer)
	file.read((char*)&nSamples,sizeof(int));
    cout <<"Samples: "<<nSamples<<'\n'<<endl;
    //Null values
	file.read((char*)&d,sizeof(float));
	file.read((char*)&d,sizeof(float));
	file.read((char*)&d,sizeof(float));
    //Loop over samples
    for (i=0;i<nSamples;i++)
	{
        //Read x,y,z and p values for each sample
		file.read((char*)&xf,sizeof(float));
		file.read((char*)&yf,sizeof(float));
		file.read((char*)&zf,sizeof(float));
		file.read((char*)&pf,sizeof(float));
        //Add scatter node
		scatter.addNode(xf,yf,zf,pf);
	}
    //Close file
	file.close();
    //Return Scatter object
	return scatter;
}
//Save results
int saveAngles(Angles angles,string filename,int gridSampling){
    //save the resultant angles
	ofstream file;
    cout<<"Saving results"<<endl;
    //Make file extension scatangle
	filename.append("angle");
    //open filename
	file.open(filename.c_str());
	if (file.is_open())
	{
        //Loop over samples
		int i;
		for (i=0;i<angles.nodes.size();i++)
		{
            if gridSampling>0{
                //output probability if grid sampling is set
    			file<<angles.nodes[i].p<<'\n';
            }
            else{
                //Otherwise output 1 when samples are drawn directly from the location distribution
                file<<'1'<'\n';

            }
			int j;
            //Output angles for each station.
			for (j=0;j<angles.nodes[i].stationAngles.size();j++)
			{
				file <<angles.nodes[i].stationAngles[j][0]<<'\t'<<angles.nodes[i].stationAngles[j][1]<<'\n';
			}
			file <<'\n';
		}
        //Close file
		file.close();
	}
	return 0;
}
//Main Function
int main(int argc,char **argv){
    //Main function
    //Get command line arguments (fn scatterFilename stationFilename gridSampling(integer) )
	string scatterFilename=string(argv[1]);
	string stationFilename=string(argv[2]);
    int gridSampling=int(argv[3]);
	Stations stations;
    //read stations
	stations=readStationFile(stationFilename);
	Scatter scatter;
    //Read scatter
	scatter=readScatterFile(scatterFilename);
    //Get angles
	Angles angles(stations,scatter);
    //Save results
	saveAngles(angles,scatterFilename,gridSampling);
	return 0;
}
