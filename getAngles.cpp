#include <string>
#include <vector>
#include <fstream>
#include <iostream>
#include <stdio.h>
#include <sstream>
extern "C" {
    #include "GridLib.h"
}
using namespace std;
class Stations{
    public:
        vector<string >filenames;
        vector<string >names;
        vector<int> dimension;
        vector<SourceDesc> srce;
};
vector<vector<string > > getAngles(double x, double y, double z,double p,Stations sta) {
    int narr;
	int iSwapBytesOnInput=0;
   
    /* loop over arrivals */
    vector<vector<string > > stationAngles;
    ::SetConstants();
    //cout<<x<<','<<y<<","<<z<<"\tP:"<<p<<"|\n";
    for (narr = 0; narr < sta.filenames.size(); narr++) {
        vector<string > angles;        
        std::ostringstream sstream;
        // if (_3D) {
            /* 3D grid */
        double ray_azim=10.0;
        double ray_dip=10.0;
        int ray_qual=0;
        double azimuth=0.0;
        double distance=0.0;
		//convert angle filename to c string
		char * filename=new char[sta.filenames[narr].size()+1];
        copy(sta.filenames[narr].begin(),sta.filenames[narr].end(),filename);
		filename[sta.filenames[narr].size()]='\0';
        if (sta.dimension[narr] == 2) {
            distance = ::GetEpiDist(&(sta.srce[narr]), x, y);
            azimuth = ::GetEpiAzim(&(sta.srce[narr]), x, y);
            if (GeometryMode == MODE_GLOBAL){distance = KM2DEG*distance;}
            // cout <<" B 2D "<<distance<< " "<<azimuth<<endl; 
            ::ReadTakeOffAnglesFile(filename,0.0,distance, z,&ray_azim,&ray_dip,&ray_qual, azimuth, iSwapBytesOnInput);
        }else{
            ::ReadTakeOffAnglesFile(filename,x, y, z,&ray_azim,&ray_dip,&ray_qual, -1.0, iSwapBytesOnInput);
        
        }
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
    return stationAngles;
    }
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
class Scatter{
    public:
		vector<xyzNode > nodes;
		void addNode(float x, float y, float z, float p)
		{
			nodes.push_back(xyzNode(x,y,z,p));
		}
};
class Angles{
    public:
		vector<angleNode > nodes;
		void addNode(vector<vector<string> > angles, double P)
		{
			nodes.push_back(angleNode(angles,P));
		}
		Angles(Stations sta,Scatter scatter){
			int i;
			for (i=0;i<scatter.nodes.size();i++)
            // for (i=0;i<100;i++)
			{
                if (i % 100 ==0)
                {
                    cout<<"Retrieved Sample:"<<i<<" of "<<scatter.nodes.size()<<endl;
                }
                vector<vector <string> >stationAngles=getAngles(scatter.nodes[i].x,scatter.nodes[i].y,scatter.nodes[i].z,scatter.nodes[i].p,sta);
				this->addNode(stationAngles,scatter.nodes[i].p);
			}
		}
};
Stations readStationFile(string filename){
	ifstream file;
	file.open(filename.c_str());
	Stations stations;
	int i,j;
	string line;
	if (file.is_open())
	{
		while ( file.good() )
		{
			string stationName;
			string angleFile;
            string fn_hdr;
            string hdr(".hdr");
			getline (file,line);
			i=line.find_first_of(":");
			j=line.find_first_of(";");
			angleFile=line.substr(i+1,j-i-1);
			stationName=line.substr(0,i);
            if (stationName.length()>0)
            {
            
                //CHECK 2D VS 3D
                FILE * fp_hdr;
                ::GridDesc gdesc;
                ::SourceDesc srce;
                fn_hdr=angleFile;
                fn_hdr+=hdr;
                fp_hdr=fopen(fn_hdr.c_str(),"r");
                if (fp_hdr == NULL) {
                    cout <<"WARNING: cannot open grid header file: "<<fn_hdr<<endl;
                }else{
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
                    stations.filenames.push_back(angleFile);
                    stations.names.push_back(stationName);
                    stations.srce.push_back(srce);
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
	file.close();
	return stations;
}
Scatter readScatterFile(string filename){
	ifstream file;
    cout<<filename<<endl;
	file.open(filename.c_str(),ios::in|ios::binary);
	char buffer[128];
	float xf;
	float yf;
	float zf;
	float pf;
	int nSamples; 
    float d;
    int i;
	Scatter scatter;
	file.read((char*)&nSamples,sizeof(int));
    cout <<"Samples: "<<nSamples<<'\n'<<endl;
	file.read((char*)&d,sizeof(float));
	file.read((char*)&d,sizeof(float));
	file.read((char*)&d,sizeof(float));
    for (i=0;i<nSamples;i++)
	{
		file.read((char*)&xf,sizeof(float));
		file.read((char*)&yf,sizeof(float));
		file.read((char*)&zf,sizeof(float));
		file.read((char*)&pf,sizeof(float));
        //cout<<xf<<'\t'<<yf<<'\t'<<zf<<'\t'<<pf<<endl;
		scatter.addNode(xf,yf,zf,pf);
	}
	file.close();
	return scatter;
}
int saveAngles(Angles angles,string filename,int gridSampling)
{
	ofstream file;
    cout<<"Saving results"<<endl;
	filename.append("angle");
	file.open(filename.c_str());
	if (file.is_open())
	{
		int i;
		for (i=0;i<angles.nodes.size();i++)
		{
            if gridSampling>0{
    			file<<angles.nodes[i].p<<'\n';
            }
            else{
                file<<'1'<'\n';

            }
			int j;
			for (j=0;j<angles.nodes[i].stationAngles.size();j++)
			{
				file <<angles.nodes[i].stationAngles[j][0]<<'\t'<<angles.nodes[i].stationAngles[j][1]<<'\n';
			}
			file <<'\n';

		}
		file.close();
	}
	return 1;
}
int main(int argc,char **argv)
{
	string scatterFilename=string(argv[1]);
	string stationFilename=string(argv[2]);
    int gridSampling=int(argv[3]);
	Stations stations;
	stations=readStationFile(stationFilename);
	Scatter scatter;
	scatter=readScatterFile(scatterFilename);
	Angles angles(stations,scatter);
	saveAngles(angles,scatterFilename,gridSampling);
	return 0;
}
