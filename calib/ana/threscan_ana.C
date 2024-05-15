#include <iostream>
#include <fstream>
#include <cmath>
#include <regex>
#include <utility> // for std::pair
#include <tuple>   // for std::tie
#include <TFile.h>
#include <TGraph.h>
#include <TGraphErrors.h>
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

std::tuple<double, double, double, double> analyzeRootFile(const char* fileName, Int_t canvasDimensionX, Int_t canvasDimensionY,
                                          int iCIRASAME, int iASIC, int iChannel, TFile* file, TString outputPDFFileName) {
    TString messagestring;
    messagestring.Form("Start analysing CIRASAME %i ASIC %i Channel %i", iCIRASAME, iASIC, iChannel);
    std::cout << messagestring << std::endl;
    // Retrieve the TGraph from the file
    TGraph* graph = dynamic_cast<TGraph*>(file->Get(Form("g%03d_%02d_%02d", iCIRASAME, iASIC, iChannel)));
    if (!graph) {
        std::cerr << "Error: TGraph " << Form("g%03d_%02d_%02d", iCIRASAME, iASIC, iChannel) << " not found in file." << std::endl;
        return std::make_tuple(0.0, 0.0, 0.0, 0.0);
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
    double fitRangeMin = 3.0; // Set the minimum value for fitting region
    double fitRangeMax = 8.0;  // Set the maximum value for fitting region
    fitFunc->SetRange(fitRangeMin, fitRangeMax);    

    // Set initial parameters for the first Gaussian
    fitFunc->SetParameter(0, 4.0);        // Amplitude Initial Value
    fitFunc->SetParameter(1, 7.2);        // Mean Initial Value
    fitFunc->SetParameter(2, 0.1);        // Sigma Initial Value
    fitFunc->SetParLimits(0, 2, 8);       // Amplitude Range
    fitFunc->SetParLimits(1, 5.0, 8);     // Mean Range
    fitFunc->SetParLimits(2, 0.05, 0.2);  // Sigma Range

    // Set initial parameters for the second Gaussian
    fitFunc->SetParameter(3, 10.0);        // Amplitude
    fitFunc->SetParameter(4, 5.5);        // Mean
    fitFunc->SetParameter(5, 0.1);        // Sigma
    fitFunc->SetParLimits(3, 3.0, 30.0);       // Amplitude Range
    fitFunc->SetParLimits(4, 5.0, 6.5);     // Mean Range
    fitFunc->SetParLimits(5, 0.1, 0.2);   // Sigma Range

    // Set initial parameters for the third Gaussian
    fitFunc->SetParameter(6, 10.0);        // Amplitude
    fitFunc->SetParameter(7, 4.7);        // Mean
    fitFunc->SetParameter(8, 0.1);        // Sigma
    fitFunc->SetParLimits(6, 2.0, 20.0);     // Amplitude Range
    fitFunc->SetParLimits(7, 4.0, 5.0);     // Mean Range
    fitFunc->SetParLimits(8, 0.1, 0.15);   // Sigma Range

    // Set initial parameters for the constant background
    fitFunc->SetParameter(9, 0.1);        // Constant Initial Value
    fitFunc->SetParLimits(9, 0.01, 0.1);  // Constant Range

    // Display the histogram
    TCanvas* canvas = new TCanvas("canvas", "Analysis Canvas", canvasDimensionX, canvasDimensionY);
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
    // Get the count rates of 0 p.e., 1 p.e., and 2 p.e.
    double countRate0peLog10Amp = fitFunc->GetParameter(0);
    double countRate1peLog10Amp = fitFunc->GetParameter(3);
    double countRate2peLog10Amp = fitFunc->GetParameter(6);
    double countRate0peLog10 = fitFunc->GetParameter(1);
    double countRate1peLog10 = fitFunc->GetParameter(4);
    double countRate2peLog10 = fitFunc->GetParameter(7);
    double countRate0peLog10Sigma = fitFunc->GetParameter(2);
    double countRate1peLog10Sigma = fitFunc->GetParameter(5);
    double countRate2peLog10Sigma = fitFunc->GetParameter(8);
    messagestring.Form("The first 3 flat count rates (in log10) detected: %f±%f %f±%f  %f±%f",
                       countRate0peLog10, countRate0peLog10Sigma, 
                       countRate1peLog10, countRate1peLog10Sigma,
                       countRate2peLog10, countRate2peLog10Sigma);
    std::cout << messagestring << std::endl;

    TLatex* textFitResult0pe = new TLatex(0.5, hMaximum*0.95,
                                          Form("0pe peak %4.3f %4.3f %4.3f", countRate0peLog10Amp, countRate0peLog10, countRate0peLog10Sigma));
    textFitResult0pe->Draw();
    TLatex* textFitResult1pe = new TLatex(0.5, hMaximum*0.85,
                                          Form("1pe peak %4.3f %4.3f %4.3f", countRate1peLog10Amp, countRate1peLog10, countRate1peLog10Sigma));
    textFitResult1pe->Draw();
    TLatex* textFitResult2pe = new TLatex(0.5, hMaximum*0.75,
                                          Form("2pe peak %4.3f %4.3f %4.3f", countRate2peLog10Amp, countRate2peLog10, countRate2peLog10Sigma));
    textFitResult2pe->Draw();
    
    
    canvas->cd(2);
    canvas->Draw();
    
    
    // Threshold-vs-CountRate plot Analysis
    int numPoints = graph->GetN();
    bool is0pefound = false;
    bool is1pefound = false;
    bool is2pefound = false;
    bool is2peEdgefound = false;
    double TransitionEdge0pe1pe = 0.;
    double TransitionEdge1pe2pe = 0.;
    double TransitionEdge2pe3pe = 0.;
    int Ninterval01 = 0;
    int Ninterval12 = 0;
    double DACMin = 0;
    double DACMax = 1100;
    double reception_factor = 2.0;  // expanding the blue regions in the graph, which prevents from excluding large(small)-counted points in the flat area.

    std::ofstream logFile;
    if (DEBUG==2) {
       TString logFileName = Form("threscan_ana-%03i-%02i-%03i.log", iCIRASAME, iASIC, iChannel);
       logFile.open(logFileName);
       if (!logFile.is_open()) {
          std::cout << "Error: Unable to open file " << logFileName << std::endl;
       }
    }
    
    if (DEBUG) {
       std::cout << "Threshold-vs-CountRate Raw Data" << std::endl;
    }


    double carrier_last0pe = 0.0;
    double carrier_last1pe = 0.0;
    bool is_first_1pe = true;
    bool is_first_2pe = true;

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

        if (TMath::Abs(log10y-countRate0peLog10) < 1.5*reception_factor*countRate0peLog10Sigma) {
           is0pefound = true;
           carrier_last0pe = x;
           messagestring.Form("   belongs to the 0 photon-equivalent");
//           std::cout << messagestring << std::endl;
           if (DEBUG==2) logFile << messagestring;
        } else if ((TMath::Abs(log10y-countRate0peLog10) >= reception_factor*countRate0peLog10Sigma) &&
                   (is0pefound == true) && (TMath::Abs(log10y-countRate1peLog10) >= 0.2) &&
                   (is1pefound == false)) {
           TransitionEdge0pe1pe += x;
           Ninterval01++;
           messagestring.Form("   Transition edge between 0pe and 1pe");
//           std::cout << messagestring << std::endl;
           if (DEBUG==2) logFile << messagestring;
        } else if ((TMath::Abs(log10y-countRate1peLog10) < reception_factor*countRate1peLog10Sigma) && (is0pefound == true)) {
            if(Ninterval01==0){
               std::cout << "No point between 0pe and 1pe. Taking average between last 0pe and 1pe points." << std::endl;
               TransitionEdge0pe1pe += carrier_last0pe;
               TransitionEdge0pe1pe += x;
               Ninterval01 = 2;
            }
           is1pefound = true;
           carrier_last1pe=x;
           messagestring.Form("   belongs to the 1 photon-equivalent");
//           std::cout << messagestring << std::endl;
           if (DEBUG==2) logFile << messagestring;
        } else if ((TMath::Abs(log10y-countRate1peLog10) >= reception_factor*countRate1peLog10Sigma) && (is1pefound == true) &&
                   (TMath::Abs(log10y-countRate2peLog10) >= reception_factor*countRate2peLog10Sigma) && (is2pefound == false)) {
           TransitionEdge1pe2pe += x;
           Ninterval12++;
           messagestring.Form("   Transition edge between 1pe and 2pe");
//           std::cout << messagestring << std::endl;
           if (DEBUG==2) logFile << messagestring;
        } else if ((TMath::Abs(log10y-countRate2peLog10) < reception_factor*countRate2peLog10Sigma) && (is1pefound == true)) {
            if(Ninterval12==0){
               TransitionEdge1pe2pe += carrier_last1pe;
               TransitionEdge1pe2pe += x;
               Ninterval12 = 2;
            }
           is2pefound = true;
           messagestring.Form("   belongs to the 2 photon-equivalent");
           if (DEBUG==2) logFile << messagestring;
//           std::cout << messagestring << std::endl;
        } else if ((log10y < countRate2peLog10 + reception_factor*countRate2peLog10Sigma) && (is2pefound == true) && (is2peEdgefound == false)) {
           is2peEdgefound = true;
           TransitionEdge2pe3pe = x;
        }
        if (DEBUG==2) logFile << std::endl;
    }
    Double_t gainDAC = 0.0;
    double Threshold05pe = 0.0;

    if (std::isnan(TransitionEdge0pe1pe) || std::isnan(TransitionEdge1pe2pe)) {
       messagestring.Form("Warning:: Likely TransitionEdge0pe1pe or TransitionEdge1pe2pe detection failed. CIRASAME, ASIC, Channel = %i, %i, %i", iCIRASAME, iASIC, iChannel);
       std::cout << messagestring << std::endl;
    } else {
       messagestring.Form("Endorsingg:: Likely TransitionEdge0pe1pe or TransitionEdge1pe2pe detection succeeded. CIRASAME, ASIC, Channel = %i, %i, %i", iCIRASAME, iASIC, iChannel);
       std::cout << messagestring << std::endl;
       std::cout << "Ninterval (01 : 12) " << Ninterval01 << " : " << Ninterval12 << std::endl;
       std::cout << "TransitionEdge (01 : 12) " << TransitionEdge0pe1pe << " : " << TransitionEdge1pe2pe << std::endl;
       TransitionEdge0pe1pe/=Ninterval01;
       std::cout << "TransitionEdge0pe1pe will be : " << TransitionEdge0pe1pe << std::endl;
       TransitionEdge1pe2pe/=Ninterval12;
       gainDAC = TransitionEdge1pe2pe - TransitionEdge0pe1pe;
       double magicFactor = -0.1;   // An emprical factor to incorporate the fact that the pulse height per p.e. seems to increase as pe increase. 
       double magicFactor_threshold05 = 0.8;
       double thres_pe = 3.5;
       TransitionEdge2pe3pe = TransitionEdge1pe2pe + (1.0+magicFactor)*(thres_pe-1.0)*gainDAC;
       Threshold05pe = TransitionEdge0pe1pe - 0.5*magicFactor_threshold05*gainDAC;
       
       
       // Displaying the fit result in the panel
       messagestring.Form("TE(0pe-1pe)DAC = %f,  TE(1pe-2pe)DAC = %f, TE(2pe-3pe)DAC = %f, Gain = %f",
                          TransitionEdge0pe1pe, TransitionEdge1pe2pe, TransitionEdge2pe3pe,  gainDAC);
       std::cout << messagestring << std::endl;
       canvas->cd(1);
       TLine* lineTE0pe1pe = new TLine(TransitionEdge0pe1pe, 0, TransitionEdge0pe1pe, graphYMax);
       TLine* lineTE1pe2pe = new TLine(TransitionEdge1pe2pe, 0, TransitionEdge1pe2pe, graphYMax);
       TLine* lineTE2pe3pe = new TLine(TransitionEdge2pe3pe, 0, TransitionEdge2pe3pe, graphYMax);
       TLine* lineCR0pe = new TLine(DACMin, TMath::Power(10, countRate0peLog10), DACMax, TMath::Power(10, countRate0peLog10));
       TLine* lineCR1pe = new TLine(DACMin, TMath::Power(10, countRate1peLog10), DACMax, TMath::Power(10, countRate1peLog10));
       TLine* lineCR2pe = new TLine(DACMin, TMath::Power(10, countRate2peLog10), DACMax, TMath::Power(10, countRate2peLog10));
       TLine* lineThreshold05pe = new TLine(Threshold05pe, 0, Threshold05pe, graphYMax);
       lineTE0pe1pe->SetLineColor(kRed);
       lineTE0pe1pe->Draw();    
       lineTE1pe2pe->SetLineColor(kRed);
       lineTE1pe2pe->Draw();
       lineTE2pe3pe->SetLineColor(kRed);
       lineTE2pe3pe->SetLineStyle(2);
       lineTE2pe3pe->Draw();
       lineCR0pe->SetLineColor(kBlue);
       lineCR0pe->Draw();
       lineCR1pe->SetLineColor(kBlue);
       lineCR1pe->Draw();
       lineCR2pe->SetLineColor(kBlue);
       lineCR2pe->Draw();
       lineThreshold05pe->SetLineColor(kRed);
       lineThreshold05pe->SetLineStyle(2);
       lineThreshold05pe->Draw();

       Double_t CR0peTorelanceLow = TMath::Power(10, countRate0peLog10-reception_factor*countRate0peLog10Sigma);
       Double_t CR0peTorelanceHigh = TMath::Power(10, countRate0peLog10+reception_factor*countRate0peLog10Sigma);
       TBox *boxCR0pe = new TBox(0, CR0peTorelanceLow, DACMax, CR0peTorelanceHigh);
       boxCR0pe->SetFillColorAlpha(kBlue, 0.3); // Set fill color and transparency
       boxCR0pe->SetLineColor(kBlue);
       boxCR0pe->SetLineWidth(2);
       boxCR0pe->Draw();
       Double_t CR1peTorelanceLow = TMath::Power(10, countRate1peLog10-reception_factor*countRate1peLog10Sigma);
       Double_t CR1peTorelanceHigh = TMath::Power(10, countRate1peLog10+reception_factor*countRate1peLog10Sigma);
       TBox *boxCR1pe = new TBox(0, CR1peTorelanceLow, DACMax, CR1peTorelanceHigh);
       boxCR1pe->SetFillColorAlpha(kBlue, 0.3); // Set fill color and transparency
       boxCR1pe->SetLineColor(kBlue);
       boxCR1pe->SetLineWidth(2);
       boxCR1pe->Draw();
       Double_t CR2peTorelanceLow = TMath::Power(10, countRate2peLog10-reception_factor*countRate2peLog10Sigma);
       Double_t CR2peTorelanceHigh = TMath::Power(10, countRate2peLog10+reception_factor*countRate2peLog10Sigma);
       TBox *boxCR2pe = new TBox(0, CR2peTorelanceLow, DACMax, CR2peTorelanceHigh);
       boxCR2pe->SetFillColorAlpha(kBlue, 0.3); // Set fill color and transparency
       boxCR2pe->SetLineColor(kBlue);
       boxCR2pe->SetLineWidth(2);
       boxCR2pe->Draw();
       
       TLatex* textGain = new TLatex(280, 3e7, Form("Gain(DAC)[%03i %02i %02i] = %4.2f", iCIRASAME, iASIC, iChannel, gainDAC));
       textGain->Draw();
    }
    graph->SetTitle("Threshold Scan Scaler Count Rates");
    graph->GetXaxis()->SetLimits(0.0, DACMax);
    graph->GetHistogram()->SetMinimum(1.0);
    graph->GetHistogram()->SetMaximum(1e8);
    graph->GetXaxis()->SetTitle("Threshold (DAC)");
    graph->GetYaxis()->SetTitle("Counts");
    canvas->Print(outputPDFFileName);
    std::cout << std::endl;  // put a empty line between channels in stdout.

    logFile.close();
    delete canvas;
    delete graph;
    delete hist;
    
    return std::make_tuple(gainDAC, TransitionEdge0pe1pe, TransitionEdge2pe3pe, Threshold05pe);
}

void threscan_ana(TString fileName) {
   TFile* inputFile = TFile::Open(fileName);
//    TRegexp re("[0-9]{8}_[0-9]{4}");
   TRegexp re("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]");
   Ssiz_t pos = fileName.Index(re);
   TString matchedPart, outputOutFileName, outputPDFFileName, outputPDFDir, outputOutDir;
   TString outputOutFileName2, outputOutFileName3;
   Double_t gainDAC = 0.0;
   Double_t TransitionEdge2pe3pe = 0.0;
   std::ofstream outputFile, outputFile2, outputFile3;
   Int_t canvasDimensionX = 1000;
   Int_t canvasDimensionY = 1000;
   TString messagestring;
//   gMinuit->SetPrintLevel(0);
   
   outputOutDir = "~/cirasame/calib/ana/out";
   outputPDFDir = "~/cirasame/calib/ana/pic";
   
   if (pos != kNPOS) {
      matchedPart = fileName(pos, 13); // 8 digits + "_" + 4 digits = 13 characters
   } else {
      std::cout << "Pattern not found in the input string." << std::endl;
   }
   outputOutFileName = "threscan_ana_chan_" + matchedPart + ".out";  // channel-wise output
   outputOutFileName2 = "threscan_ana_asic_" + matchedPart + ".out"; // asic-wise output
   outputOutFileName3 = "threscan_ana_crsm_" + matchedPart + ".out"; // cirasame-wise output
   outputPDFFileName = outputPDFDir + "/threscan_ana_" + matchedPart + ".pdf";
   
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
   outputFile2.open(outputOutFileName2);
   if (!outputFile2.is_open()) {
      std::cout << "Error: Unable to open file " << outputOutFileName2 << std::endl;
   }
   outputFile3.open(outputOutFileName3);
   if (!outputFile3.is_open()) {
      std::cout << "Error: Unable to open file " << outputOutFileName3 << std::endl;
   }
   
   TCanvas* canvas2 = new TCanvas("canvas2", "Summary", canvasDimensionX, canvasDimensionY);
   TCanvas *dummyCanvas = new TCanvas("dummyCanvas", "Dummy Canvas", canvasDimensionX, canvasDimensionY);
   dummyCanvas->Print(outputPDFFileName+"[");
   delete dummyCanvas;
   
   TH1F* h_gain = new TH1F("h_gain", "Gain distribution", 50, 0, 100);
   TH1F* h_baseline_total = new TH1F("h_baseline", "Baseline distribution", 101, 150, 250);
   TH1F* h_baseline_citiroc[nCIRASAME*nASIC];
   TGraph* g_idgain = new TGraph(); // 0, 2304, 0, 70;
   TGraphErrors* g_idbaseline_odd = new TGraphErrors(); // 0, 2304, 0, 70;
   TGraphErrors* g_idbaseline_even = new TGraphErrors(); // 0, 2304, 0, 70;
   TGraphErrors* g_cirasamegain = new TGraphErrors();
   h_gain->GetXaxis()->SetTitle("Gain in DAC value");
   h_gain->GetYaxis()->SetTitle("Count");
   g_idgain->GetXaxis()->SetTitle("Global Channel");
   g_idgain->GetYaxis()->SetTitle("Gain (DAC)");
   g_idbaseline_odd->GetXaxis()->SetTitle("Global CITIROC Channel");
   g_idbaseline_odd->GetYaxis()->SetTitle("Baseline+offset (DAC)");
   g_idbaseline_even->GetXaxis()->SetTitle("Global CITIROC Channel");
   g_idbaseline_even->GetYaxis()->SetTitle("Baseline+offset (DAC)");
   g_cirasamegain->GetXaxis()->SetTitle("CIRASAME Number");
   g_cirasamegain->GetYaxis()->SetTitle("Averaged Gain (DAC)");
   int nIdBaselineEven = 0;
   int nIdBaselineOdd = 0;
   double cirasame_gain[nCIRASAME];
   for(int iCIRASAME=1; iCIRASAME<=nCIRASAME; iCIRASAME++){
     double this_cirasame_gain = 0;
     int ch_count_cirasame_gain = 0;
      for(int iASIC=1; iASIC<=nASIC; iASIC++){
         
         Int_t gCITIROCChannel = 4*(iCIRASAME-1) + iASIC-1;
         TString baseline_citiroc_string = Form("Baseline+C distribution CIRASAME%2i CITIROC%1i", iCIRASAME, iASIC);
         h_baseline_citiroc[gCITIROCChannel] = new TH1F("h_baseline_citiroc", baseline_citiroc_string, 101, 150, 250);
         double TransitionEdge2pe3peASIC = 0.;
         double Threshold05peASIC = 0.;
         int channelCount = 0;
         double T = 0.;
         
         for(int iChannel=1; iChannel<=nChannel; ++iChannel){
            
            Int_t gChannel = 128*(iCIRASAME-1) + 32*(iASIC-1) + iChannel;

            auto result = analyzeRootFile(fileName, canvasDimensionX, canvasDimensionY,
                                          iCIRASAME, iASIC, iChannel, inputFile, outputPDFFileName);
            double gainDAC = std::get<0>(result);
            double TransitionEdge0pe1pe = std::get<1>(result);
            double TransitionEdge2pe3pe = std::get<2>(result);
            double Threshold05pe = std::get<3>(result);
            
            h_gain->Fill(gainDAC);
            g_idgain->SetPoint(gChannel, gChannel, gainDAC);
            h_baseline_total->Fill(TransitionEdge0pe1pe);
            h_baseline_citiroc[gCITIROCChannel]->Fill(TransitionEdge0pe1pe);
            messagestring.Form("%5i %5i %5i %5i %8f %8f %f", gChannel, iCIRASAME, iASIC, iChannel, gainDAC, TransitionEdge2pe3pe, Threshold05pe);
            outputFile << messagestring << std::endl;
            TransitionEdge2pe3peASIC+=TransitionEdge2pe3pe;
            Threshold05peASIC+=Threshold05pe;

            if ((!std::isinf(gainDAC)) && (!std::isnan(gainDAC)) && (gainDAC>0.0)){
               this_cirasame_gain += gainDAC;
               ch_count_cirasame_gain++;
            }
            //this_cirasame_gain += gainDAC;

            channelCount++;

         }
         TransitionEdge2pe3peASIC/= (double)channelCount;
         Threshold05peASIC/=(double)channelCount;
         double baseline_citiroc_mean = h_baseline_citiroc[gCITIROCChannel]->GetMean();
         double baseline_citiroc_rms = h_baseline_citiroc[gCITIROCChannel]->GetRMS();
         messagestring.Form("%i %f %f %f %f", gCITIROCChannel, baseline_citiroc_mean, baseline_citiroc_rms, TransitionEdge2pe3peASIC, Threshold05peASIC);
         outputFile2 << messagestring << std::endl;

         
         
         if (TMath::Even(iCIRASAME)) {
            g_idbaseline_even->SetPoint(nIdBaselineEven, gCITIROCChannel, baseline_citiroc_mean);
            g_idbaseline_even->SetPointError(nIdBaselineEven, 0, baseline_citiroc_rms);
            nIdBaselineEven++;
         } else {
            g_idbaseline_odd->SetPoint(nIdBaselineOdd, gCITIROCChannel, baseline_citiroc_mean);
            g_idbaseline_odd->SetPointError(nIdBaselineOdd, 0, baseline_citiroc_rms);
            nIdBaselineOdd++;
         }
 
      }
      //this_cirasame_gain/=(nChannel*nASIC);
      this_cirasame_gain/=ch_count_cirasame_gain;
      cirasame_gain[iCIRASAME] = this_cirasame_gain;
      g_cirasamegain->SetPoint(iCIRASAME, iCIRASAME, this_cirasame_gain);
      g_cirasamegain->SetPointError(iCIRASAME, 0, 0);
      messagestring.Form("%i %f", iCIRASAME, this_cirasame_gain);
      outputFile3 << messagestring << std::endl;

   }
   h_gain->Draw("");  // Gain Histogram
   canvas2->Print(outputPDFFileName);
   canvas2->Clear();
   double range_g_id_gain = 100.0;
   double yMax_g_id_gain = h_gain->GetMean() + 0.5*range_g_id_gain;
   double yMin_g_id_gain = h_gain->GetMean() - 0.5*range_g_id_gain;
   if (yMin_g_id_gain < 0){
     yMax_g_id_gain = range_g_id_gain;
     yMin_g_id_gain = 0.0;
   }
   g_idgain->GetYaxis()->SetRangeUser(yMin_g_id_gain, yMax_g_id_gain);
   g_idgain->Draw("AP"); // Gain vs ID
   canvas2->Print(outputPDFFileName);
   canvas2->Clear();
   g_cirasamegain->SetMarkerSize(2);
   g_cirasamegain->SetMarkerStyle(20); // Set marker style to a filled circle
   g_cirasamegain->Draw("AP");
   canvas2->Print(outputPDFFileName);
   
   h_baseline_total->Draw(""); // Baseline Total
   canvas2->Print(outputPDFFileName);
   canvas2->Clear();
   for (int i_gCITIROC = 0; i_gCITIROC < nCIRASAME*nASIC; i_gCITIROC++){
      h_baseline_citiroc[i_gCITIROC]->Draw(""); // Baseline CITIROC
      canvas2->Print(outputPDFFileName);
      canvas2->Clear();
   }
   g_idbaseline_even->SetMarkerSize(2);
   g_idbaseline_even->SetMarkerStyle(20); // Set marker style to a filled circle
   g_idbaseline_odd->SetMarkerSize(2);
   g_idbaseline_odd->SetMarkerStyle(24);  // Set marker style to a open circle
   g_idbaseline_odd->Draw("AP");          // Axis Point
//   g_idbaseline_odd->GetYaxis()->SetRange(160., 200.);
   g_idbaseline_even->Draw("P same");     // Point Same
   canvas2->Print(outputPDFFileName);
   canvas2->Clear();
   
   // Close the PDF file
   TCanvas *finalCanvas = new TCanvas("finalCanvas", "Final Canvas", canvasDimensionX, canvasDimensionY);
   finalCanvas->Print(outputPDFFileName+"]");
   delete finalCanvas;
   
   inputFile->Close();
   outputFile.close();
   outputFile2.close();
   outputFile3.close();
   
}
