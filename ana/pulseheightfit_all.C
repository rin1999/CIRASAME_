#include <iostream>
#include <fstream>
#include <cmath>
#include <regex>
#include <TFile.h>
#include <TGraph.h>
#include <TH1F.h>
#include <TF1.h>
#include <TCanvas.h>
#include <TLine.h>
#include <TBox.h>
#include <TLatex.h>
#include <TPDF.h>
#include <TRegexp.h>
#include <TMinuit.h>

#define DEBUG 0

double analyzeRootFile(const char* fileName, Int_t canvasDimentionX, Int_t canvasDimentionY,
                       int iCIRASAME, int iASIC, int iChannel, TFile* file,
                       TString outputPDFFileName) {
    TString messagestring;
    messagestring.Form("Start analysing CIRASAME %i ASIC %i Channel %i", iCIRASAME, iASIC, iChannel);
    std::cout << messagestring << std::endl;
    // Retrieve the TGraph from the file
    TGraph* graph = dynamic_cast<TGraph*>(file->Get(Form("g%03d_%02d_%02d", iCIRASAME, iASIC, iChannel)));
    if (!graph) {
        std::cerr << "Error: TGraph " << Form("g%03d_%02d_%02d", iCIRASAME, iASIC, iChannel) << " not found in file." << std::endl;
        return -1;
    }

    // Dump row values to stdout
    if (DEBUG) {
       std::cout << "Raw Values:" << std::endl;
       for (int i = 0; i < graph->GetN(); ++i) {
          messagestring.Form("   %2i  %03i   %9i  %5f",
                             i, int(graph->GetX()[i]), int(graph->GetY()[i]), TMath::Log10(graph->GetY()[i]));
          std::cout << messagestring << std::endl;
       }
    }
    double graphYMax = 1e8;

    // Determining the flat part of the Threshold-vs-CountRate plot
    std::cout << "Start determining the flat part of the Threshold-vs-CountRate plot." << std::endl;
    // Create a histogram to store the log-transformed y values
    Double_t xRangeMax = TMath::Log10(graph->GetYaxis()->GetXmax())+0.5;
    xRangeMax = 8.0;
    TH1F* hist = new TH1F("hist", "Log Transformed Y Values Histogram", 50, 0, xRangeMax);

    // Fill the histogram with the log-transformed y values of the TGraph
    if (DEBUG) {
       std::cout << "Filling a count-rate log10 histogram." << std::endl;
    }
    for (int i = 0; i < graph->GetN(); ++i) {
        double y_value = graph->GetY()[i];
        if (y_value <= 0) continue; // Skip non-positive values
        double log_y = TMath::Log10(y_value);
        if (DEBUG) {
           std::cout << "    " << log_y << std::endl;
        }
        hist->Fill(log_y);
    }

    TF1* fitFunc = new TF1("fitFunc", "gaus(0) + gaus(3) + gaus(6) + [9]", hist->GetXaxis()->GetXmin(), hist->GetXaxis()->GetXmax());

    // Set the fitting range (e.g., from -1 to 1 in log scale)
    double fitRangeMin = 2.0; // Set the minimum value for fitting region
    double fitRangeMax = 8.0;  // Set the maximum value for fitting region
    fitFunc->SetRange(fitRangeMin, fitRangeMax);    

    // Set initial parameters for the first Gaussian
    fitFunc->SetParameter(0, 4.0);        // Amplitude Initial Value
    fitFunc->SetParameter(1, 7.2);        // Mean Initial Value
    fitFunc->SetParameter(2, 0.1);        // Sigma Initial Value
    fitFunc->SetParLimits(0, 2, 8);       // Amplitude Range
    fitFunc->SetParLimits(1, 5.0, 8);     // Mean Range
    fitFunc->SetParLimits(2, 0.03, 0.2);  // Sigma Range

    // Set initial parameters for the second Gaussian
    fitFunc->SetParameter(3, 4.0);        // Amplitude
    fitFunc->SetParameter(4, 5.0);        // Mean
    fitFunc->SetParameter(5, 0.1);        // Sigma
    fitFunc->SetParLimits(3, 2, 8);       // Amplitude Range
    fitFunc->SetParLimits(4, 4.5, 6);     // Mean Range
    fitFunc->SetParLimits(5, 0.1, 0.4);   // Sigma Range

    // Set initial parameters for the third Gaussian
    fitFunc->SetParameter(6, 3.0);        // Amplitude
    fitFunc->SetParameter(7, 3.5);        // Mean
    fitFunc->SetParameter(8, 0.2);        // Sigma
    fitFunc->SetParLimits(6, 1.5, 8);     // Amplitude Range
    fitFunc->SetParLimits(7, 2.5, 4);     // Mean Range
    fitFunc->SetParLimits(8, 0.1, 0.5);   // Sigma Range

    // Set initial parameters for the constant background
    fitFunc->SetParameter(9, 0.1);        // Constant Initial Value
    fitFunc->SetParLimits(9, 0.01, 0.1);  // Constant Range

    // Display the histogram
    TCanvas* canvas = new TCanvas("canvas", "Analysis Canvas", 1000, 1000);
    canvas->Divide(1, 2);
    canvas->SetLogy();
    canvas->cd(1);
    gPad->SetLogy();
    graph->Draw();
    canvas->cd(2);
    Double_t hMaximum = hist->GetMaximum();
    hist->GetXaxis()->SetTitle("Log10 Count Rate");
    hist->GetYaxis()->SetTitle("Count");
    hist->Draw();
    //hist->Fit(fitFunc, "R", fitRangeMin, fitRangeMax);
    hist->Fit(fitFunc, "LR");
    // Get the count rates of 1 p.e., 2 p.e., and 3 p.e.
    double countRate1peLog10Amp = fitFunc->GetParameter(0);
    double countRate2peLog10Amp = fitFunc->GetParameter(3);
    double countRate3peLog10Amp = fitFunc->GetParameter(6);
    double countRate1peLog10 = fitFunc->GetParameter(1);
    double countRate2peLog10 = fitFunc->GetParameter(4);
    double countRate3peLog10 = fitFunc->GetParameter(7);
    double countRate1peLog10Sigma = fitFunc->GetParameter(2);
    double countRate2peLog10Sigma = fitFunc->GetParameter(5);
    double countRate3peLog10Sigma = fitFunc->GetParameter(8);
    messagestring.Form("The first 3 flat count rates (in log10) detected: %f±%f %f±%f  %f±%f",
                       countRate1peLog10, countRate1peLog10Sigma, 
                       countRate2peLog10, countRate2peLog10Sigma,
                       countRate3peLog10, countRate3peLog10Sigma);
    std::cout << messagestring << std::endl;

    TLatex* textFitResult1pe = new TLatex(0.5, hMaximum-0.2,
                                          Form("1pe peak %4.3f %4.3f %4.3f", countRate1peLog10Amp, countRate1peLog10, countRate1peLog10Sigma));
    textFitResult1pe->Draw();
    TLatex* textFitResult2pe = new TLatex(0.5, hMaximum-0.9,
                                          Form("2pe peak %4.3f %4.3f %4.3f", countRate2peLog10Amp, countRate2peLog10, countRate2peLog10Sigma));
    textFitResult2pe->Draw();
    TLatex* textFitResult3pe = new TLatex(0.5, hMaximum-1.6,
                                          Form("3pe peak %4.3f %4.3f %4.3f", countRate3peLog10Amp, countRate3peLog10, countRate3peLog10Sigma));
    textFitResult3pe->Draw();
    
    
    canvas->cd(2);
    canvas->Draw();
    
    
    // Threshold-vs-CountRate plot Analysis
    int numPoints = graph->GetN();
    bool is1pefound = false;
    bool is2pefound = false;
    bool is3pefound = false;
    double TransitionEdge1pe2pe = 0.;
    double TransitionEdge2pe3pe = 0.;
    int Ninterval12 = 0;
    int Ninterval23 = 0;
    double DACMin = 0;
    double DACMax = 500;

    std::ofstream logFile;
    if (DEBUG==2) {
       TString logFileName = Form("pulseheightfit_all-%03i-%02i-%03i.log", iCIRASAME, iASIC, iChannel);
       logFile.open(logFileName);
       if (!logFile.is_open()) {
          std::cout << "Error: Unable to open file " << logFileName << std::endl;
       }
    }
    
    if (DEBUG) {
       std::cout << "Threshold-vs-CountRate Raw Data" << std::endl;
    }
    for (int i = 0; i < numPoints; ++i) {
       double x, y, log10y;
        graph->GetPoint(i, x, y);
        if (y == 0) {
           log10y = 0;
        } else {
           log10y = TMath::Log10(y);
        }
        messagestring.Form(" %8i     %8i    %8.3f", int(x), int(y), log10y);
        if (DEBUG==1) std::cout << messagestring << std::endl;
        if (DEBUG==2) logFile << messagestring;

        if (TMath::Abs(log10y-countRate1peLog10) < countRate1peLog10Sigma) {
           is1pefound = true;
           messagestring.Form("   belongs to the 1 photon-equivalent");
//           std::cout << messagestring << std::endl;
           if (DEBUG==2) logFile << messagestring;
        } else if ((TMath::Abs(log10y-countRate1peLog10) >= countRate1peLog10Sigma) &&
                   (is1pefound == true) && (TMath::Abs(log10y-countRate2peLog10) >= 0.2) &&
                   (is2pefound == false)) {
           TransitionEdge1pe2pe += x;
           Ninterval12++;
           messagestring.Form("   Transition edge between 1pe and 2pe");
//           std::cout << messagestring << std::endl;
           if (DEBUG==2) logFile << messagestring;
        } else if ((TMath::Abs(log10y-countRate2peLog10) < countRate2peLog10Sigma) && (is1pefound == true)) {
           is2pefound = true;
           messagestring.Form("   belongs to the 2 photon-equivalent");
//           std::cout << messagestring << std::endl;
           if (DEBUG==2) logFile << messagestring;
        } else if ((TMath::Abs(log10y-countRate2peLog10) >= countRate2peLog10Sigma) && (is2pefound == true) &&
                   (TMath::Abs(log10y-countRate3peLog10) >= countRate3peLog10Sigma) && (is3pefound == false)) {
           TransitionEdge2pe3pe += x;
           Ninterval23++;
           messagestring.Form("   Transition edge between 2pe and 3pe");
//           std::cout << messagestring << std::endl;
           if (DEBUG==2) logFile << messagestring;
        } else if ((TMath::Abs(log10y-countRate3peLog10) < countRate3peLog10Sigma) && (is2pefound == true)) {
           is3pefound = true;
           messagestring.Form("   belongs to the 3 photon-equivalent");
           if (DEBUG==2) logFile << messagestring;
//           std::cout << messagestring << std::endl;
        }
        if (DEBUG==2) logFile << std::endl;
    }
    Double_t gain = 0.0;
    if (std::isnan(TransitionEdge1pe2pe) || std::isnan(TransitionEdge2pe3pe)) {
       messagestring.Form("Warning:: Likely TransitionEdge1pe2pe or TransitionEdge2pe3pe detection failed. CIRASAME, ASIC, Channel = %i, %i, %i", iCIRASAME, iASIC, iChannel);
       std::cout << messagestring << std::endl;
    } else {
       messagestring.Form("Endorsingg:: Likely TransitionEdge1pe2pe or TransitionEdge2pe3pe detection succeeded. CIRASAME, ASIC, Channel = %i, %i, %i", iCIRASAME, iASIC, iChannel);
       std::cout << messagestring << std::endl;
       TransitionEdge1pe2pe/=Ninterval12;
       TransitionEdge2pe3pe/=Ninterval23;
       gain = TransitionEdge2pe3pe - TransitionEdge1pe2pe;
       
       // Displaying the fit result in the panel
       messagestring.Form("DAC 1pe = %f,  DAC 2pe = %f, Gain = %f", TransitionEdge1pe2pe, TransitionEdge2pe3pe, gain);
       std::cout << messagestring << std::endl;
       canvas->cd(1);
       TLine* lineTE1pe2pe = new TLine(TransitionEdge1pe2pe, 0, TransitionEdge1pe2pe, graphYMax);
       TLine* lineTE2pe3pe = new TLine(TransitionEdge2pe3pe, 0, TransitionEdge2pe3pe, graphYMax);
       TLine* lineCR1pe = new TLine(DACMin, TMath::Power(10, countRate1peLog10), DACMax, TMath::Power(10, countRate1peLog10));
       TLine* lineCR2pe = new TLine(DACMin, TMath::Power(10, countRate2peLog10), DACMax, TMath::Power(10, countRate2peLog10));
       TLine* lineCR3pe = new TLine(DACMin, TMath::Power(10, countRate3peLog10), DACMax, TMath::Power(10, countRate3peLog10));
       lineTE1pe2pe->SetLineColor(kRed);
       lineTE1pe2pe->Draw();    
       lineTE2pe3pe->SetLineColor(kRed);
       lineTE2pe3pe->Draw();

       Double_t CR1peTorelanceLow = TMath::Power(10, countRate1peLog10-countRate1peLog10Sigma);
       Double_t CR1peTorelanceHigh = TMath::Power(10, countRate1peLog10+countRate1peLog10Sigma);
       TBox *boxCR1pe = new TBox(0, CR1peTorelanceLow, 500, CR1peTorelanceHigh);
       boxCR1pe->SetFillColorAlpha(kBlue, 0.3); // Set fill color and transparency
       boxCR1pe->SetLineColor(kBlue);
       boxCR1pe->SetLineWidth(2);
       boxCR1pe->Draw();
       Double_t CR2peTorelanceLow = TMath::Power(10, countRate2peLog10-countRate2peLog10Sigma);
       Double_t CR2peTorelanceHigh = TMath::Power(10, countRate2peLog10+countRate2peLog10Sigma);
       TBox *boxCR2pe = new TBox(0, CR2peTorelanceLow, 500, CR2peTorelanceHigh);
       boxCR2pe->SetFillColorAlpha(kBlue, 0.3); // Set fill color and transparency
       boxCR2pe->SetLineColor(kBlue);
       boxCR2pe->SetLineWidth(2);
       boxCR2pe->Draw();
       Double_t CR3peTorelanceLow = TMath::Power(10, countRate3peLog10-countRate3peLog10Sigma);
       Double_t CR3peTorelanceHigh = TMath::Power(10, countRate3peLog10+countRate3peLog10Sigma);
       TBox *boxCR3pe = new TBox(0, CR3peTorelanceLow, 500, CR3peTorelanceHigh);
       boxCR3pe->SetFillColorAlpha(kBlue, 0.3); // Set fill color and transparency
       boxCR3pe->SetLineColor(kBlue);
       boxCR3pe->SetLineWidth(2);
       boxCR3pe->Draw();
       
       lineCR1pe->SetLineColor(kBlue);
       lineCR1pe->Draw();
       lineCR2pe->SetLineColor(kBlue);
       lineCR2pe->Draw();
       lineCR3pe->SetLineColor(kBlue);
       lineCR3pe->Draw();
       TLatex* textGain = new TLatex(200, 1e6, Form("Gain(%03i %02i %02i) = %4.2f", iCIRASAME, iASIC, iChannel, gain));
       textGain->Draw();
    }
    graph->SetTitle("Threshold Scan Scaler Count Rates");
    graph->GetXaxis()->SetLimits(0.0, 500.0);
    graph->GetHistogram()->SetMinimum(1.0);
    graph->GetHistogram()->SetMaximum(1e8);
    graph->GetXaxis()->SetTitle("Threshold (DAC)");
    graph->GetYaxis()->SetTitle("Counts");
    canvas->Print(outputPDFFileName);
    std::cout << std::endl;

    logFile.close();
    delete canvas;
    delete graph;
    delete hist;
    
    return gain;
}

void pulseheightfit_all(TString fileName) {
   TFile* inputFile = TFile::Open(fileName);
//    TRegexp re("[0-9]{8}_[0-9]{4}");
   TRegexp re("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]");
   Ssiz_t pos = fileName.Index(re);
   TString matchedPart, outputOutFileName, outputPDFFileName, outputPDFDir, outputOutDir;
   Double_t gain;
   std::ofstream outputFile;
   Int_t canvasDimentionX = 1000;
   Int_t canvasDimentionY = 1000;
//   gMinuit->SetPrintLevel(0);
   
   outputOutDir = "~/cirasame/calib/ana/out";
   outputPDFDir = "~/cirasame/calib/ana/pic";
   
   if (pos != kNPOS) {
      matchedPart = fileName(pos, 13); // 8 digits + "_" + 4 digits = 13 characters
   } else {
      std::cout << "Pattern not found in the input string." << std::endl;
   }
//   outputOutFileName = outputOutDir + "/pulseheightfit_all_" + matchedPart + ".out";
   outputOutFileName = "pulseheightfit_all_" + matchedPart + ".out";
   outputPDFFileName = outputPDFDir + "/pulseheightfit_all_" + matchedPart + ".pdf";
   
   Int_t nCIRASAME = 18;
   Int_t nASIC = 4;
   Int_t nChannel = 32;
   
   if (!inputFile || inputFile->IsZombie()) {
      std::cerr << "Error: Unable to open file " << fileName << std::endl;
   }
   outputFile.open(outputOutFileName);
   if (!outputFile.is_open()) {
      std::cout << "Error: Unable to open file " << outputOutFileName << std::endl;
   }
   
   TCanvas* canvas2 = new TCanvas("canvas2", "Summary", canvasDimentionX, canvasDimentionY);
   TCanvas *dummyCanvas = new TCanvas("dummyCanvas", "Dummy Canvas", canvasDimentionX, canvasDimentionY);
   dummyCanvas->Print(outputPDFFileName+"[");
   delete dummyCanvas;
   
   TH1F* h_gain = new TH1F("h_gain", "Gain distribution", 50, 0, 100);
   TGraph* g_idgain = new TGraph(); // 0, 2304, 0, 70;
   h_gain->GetXaxis()->SetTitle("Gain in ADC value");
   h_gain->GetYaxis()->SetTitle("Count");
   g_idgain->GetXaxis()->SetTitle("Global Channel");
   g_idgain->GetYaxis()->SetTitle("Gain (ADC)");
   for(int iCIRASAME=1; iCIRASAME<=nCIRASAME; ++iCIRASAME){
      for(int iASIC=1; iASIC<=nASIC; ++iASIC){
         for(int iChannel=1; iChannel<=nChannel; ++iChannel){
            gain = analyzeRootFile(fileName, canvasDimentionX, canvasDimentionY,
                                    iCIRASAME, iASIC, iChannel, inputFile, outputPDFFileName);
            h_gain->Fill(gain);
            Int_t gChannel = 128*(iCIRASAME-1) + 32*(iASIC-1) + iChannel;
            g_idgain->AddPoint(gChannel, gain);
            outputFile << gChannel << " " << iCIRASAME << " " << iASIC << " " << iChannel << " " << gain << std::endl;
         }
      }
   }
   h_gain->Draw();
   canvas2->Print(outputPDFFileName);
   canvas2->Clear();
   g_idgain->Draw();
   canvas2->Print(outputPDFFileName);
   
   // Close the PDF file
   TCanvas *finalCanvas = new TCanvas("finalCanvas", "Final Canvas", canvasDimentionX, canvasDimentionY);
   finalCanvas->Print(outputPDFFileName+"]");
   delete finalCanvas;
   
   inputFile->Close();
   outputFile.close();
   
}
