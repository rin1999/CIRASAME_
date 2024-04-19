#include <iostream>
#include <fstream>
#include <TFile.h>
#include <TGraph.h>
#include <TCanvas.h>
#include <TKey.h>
#include <TObject.h>
#include <TObjString.h>

void createTGraphs(TString pathName, TString dirName) {
    std::cout << "Creating TGraphs..." << std::endl;
    TString outputName = "~/cirasame/calib/ana/root/" + dirName + ".root";
    TFile outputFile(outputName, "RECREATE");
    if (!outputFile.IsOpen()) {
        std::cerr << "Error: Could not open output file " << outputName << std::endl;
        return;
    }
    int nCIRASAME = 18;
    int nASIC = 4;
    int nChannel = 32;
    // Loop over files in the directory
    for (int iCIRASAME = 1; iCIRASAME <= nCIRASAME; ++iCIRASAME) {
        for (int iASIC = 1; iASIC <= nASIC; ++iASIC) {
           TString fileName = Form("%s/cirasame%03d_%02d.dat", pathName.Data(), iCIRASAME, iASIC);
            std::cout << "Processing file: " << fileName << std::endl;

            ifstream inFile(fileName.Data());
            if (!inFile.is_open()) {
                std::cerr << "Error: Could not open file " << fileName << std::endl;
                continue;
            }

            TGraph* graphs[nChannel];
            for (int iChannel = 1; iChannel <= nChannel; ++iChannel) {
               TString graphName = Form("g%03d_%02d_%02d", iCIRASAME, iASIC, iChannel);
               graphs[iChannel] = new TGraph();
               graphs[iChannel]->SetName(graphName);
            }
            
            double xVal;
            double yVals[nChannel];
            while (inFile >> xVal) {
               for (int iChannel = 1; iChannel <= nChannel; ++iChannel) {
                  inFile >> yVals[iChannel];
                  graphs[iChannel]->AddPoint(xVal, yVals[iChannel]);
               }
            }
            inFile.close();

            for (int iChannel = 1; iChannel <= nChannel; ++iChannel) {
               graphs[iChannel]->Write();
               delete graphs[iChannel];
            }
        }
    }

    outputFile.Close();
    std::cout << "TGraph creation completed." << std::endl;
}

void fdat2root(TString pathName) {
    std::cout << "Starting fdat2root macro..." << std::endl;

    TObjArray *tokens = pathName.Tokenize("/");
    TString dirName = ((TObjString *)(tokens->Last()))->GetString();
    createTGraphs(pathName, dirName);
    delete tokens;    
    std::cout << "fdat2root macro completed." << std::endl;
}
