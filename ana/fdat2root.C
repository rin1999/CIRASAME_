#include <iostream>
#include <fstream>
#include <TFile.h>
#include <TGraph.h>
#include <TCanvas.h>
#include <TKey.h>
#include <TObject.h>

void createTGraphs(const char* directory, const char* outputFileName) {
    TString dirPath(directory);
    TString outputName(outputFileName);

    std::cout << "Creating TGraphs..." << std::endl;

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
            TString fileName = Form("%s/cirasame%03d_%02d.dat", directory, iCIRASAME, iASIC);
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
            
//            int iLine = 0;
            double xVal;
            double yVals[nChannel];
            while (inFile >> xVal) {
               for (int iChannel = 1; iChannel <= nChannel; ++iChannel) {
                  inFile >> yVals[iChannel];
                  std::cout << iChannel << " " << xVal << " " << yVals[iChannel] << std::endl;
//                  graphs[iChannel]->SetPoint(iLine, xVal, yVals[iChannel]);
                  graphs[iChannel]->AddPoint(xVal, yVals[iChannel]);
               }
//               iLine++;
            }
            inFile.close();

/*            Double_t nData =  graphs[5]->GetN();
            Double_t* xx = graphs[5]->GetX();
            Double_t* yy = graphs[5]->GetY();
            for (int i = 0; i < nData; ++i) {
               std::cout << xx[i] << " " << yy[i] << std::endl;
            }
            std::cout << "ndata points " << nData << std::endl;
*/          
            for (int iChannel = 1; iChannel <= nChannel; ++iChannel) {
               graphs[iChannel]->Write();
               delete graphs[iChannel];
            }
        }
    }

    outputFile.Close();
    std::cout << "TGraph creation completed." << std::endl;
}

void plotGraphs(const char* outputFileName) {
    TString outputName(outputFileName);
    std::cout << "Plotting graphs from file: " << outputName << std::endl;

    TFile inputFile(outputName);
    if (!inputFile.IsOpen()) {
        std::cerr << "Error: Could not open input file " << outputName << std::endl;
        return;
    }

    TCanvas canvas("canvas", "Canvas", 800, 600);

    // Loop over TGraphs stored in the input ROOT file and draw them
    int graphIndex = 0;
    TGraph* graph;
    TIter next(inputFile.GetListOfKeys());
    TKey* key;
    while ((key = (TKey*)next())) {
        TObject* obj = key->ReadObj();
        if (obj->InheritsFrom(TGraph::Class())) {
            graph = (TGraph*)obj;
            graph->SetMarkerStyle(20);
            graph->SetMarkerSize(0.8);
            graph->SetLineColor(graphIndex + 2);
            if (graphIndex == 0) {
                graph->Draw("AL");
            } else {
                graph->Draw("PLSAME");
            }
            ++graphIndex;
        }
        delete obj; // Free memory
    }

    TString pdfFileName = outputName.ReplaceAll(".root", "") + ".pdf";
    canvas.SaveAs(pdfFileName);

    inputFile.Close();
    std::cout << "Plotting completed." << std::endl;
}

void fdat2root(const char* directory, const char* outputFileName, bool showPlot) {
    std::cout << "Starting fdat2root macro..." << std::endl;

    createTGraphs(directory, outputFileName);
    if (showPlot) {
        plotGraphs(outputFileName);
    }

    std::cout << "fdat2root macro completed." << std::endl;
}
