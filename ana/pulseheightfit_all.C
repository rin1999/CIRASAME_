#include <iostream>
#include <TFile.h>
#include <TGraph.h>
#include <TH1F.h>
#include <TF1.h>
#include <TCanvas.h>

void analyzeRootFile(const char* fileName,int iCIRASAME,int iASIC,int iChannel) {
    // Open the ROOT file
    TFile* file = TFile::Open(fileName);
    if (!file || file->IsZombie()) {
        std::cerr << "Error: Unable to open file " << fileName << std::endl;
        return;
    }

    // Retrieve the TGraph from the file
    TGraph* graph = dynamic_cast<TGraph*>(file->Get(Form("g%03d_%02d_%02d", iCIRASAME, iASIC, iChannel)));
    if (!graph) {
        std::cerr << "Error: TGraph " << Form("g%03d_%02d_%02d", iCIRASAME, iASIC, iChannel) << " not found in file." << std::endl;
        file->Close();
        return;
    }

    // Dump row values to stdout
    std::cout << "Row Values:" << std::endl;
    for (int i = 0; i < graph->GetN(); ++i) {
       std::cout << "Row " << i << ": x = " << graph->GetX()[i] << ", y = " << graph->GetY()[i] << ", log_y = " << TMath::Log10(graph->GetY()[i]) << std::endl;
    }
    double graphYMax = graph->GetYaxis()->GetXmax();

    // Create a histogram to store the log-transformed y values
    // TH1F* hist = new TH1F("hist", "Log Transformed Y Values Histogram", 100, TMath::Log10(graph->GetYaxis()->GetXmin()), TMath::Log10(graph->GetYaxis()->GetXmax()));
    // std::cout << "Declaring a histogram 100 " <<  TMath::Log10(graph->GetYaxis()->GetXmin()) << " " <<  TMath::Log10(graph->GetYaxis()->GetXmax()) << std::endl;
    TH1F* hist = new TH1F("hist", "Log Transformed Y Values Histogram", 100, 0, TMath::Log10(graph->GetYaxis()->GetXmax())+0.5);
    std::cout << "Declaring a histogram 100 " << 0 << " " <<  TMath::Log10(graph->GetYaxis()->GetXmax())+0.5 << std::endl;


    // Fill the histogram with the log-transformed y values of the TGraph
    for (int i = 0; i < graph->GetN(); ++i) {
        double y_value = graph->GetY()[i];
        if (y_value <= 0) continue; // Skip non-positive values
        double log_y = TMath::Log10(y_value);
        std::cout << "filling " << log_y << std::endl;
        hist->Fill(log_y);
    }

    // Perform fitting if needed
    // TF1* fitFunc = new TF1("fitFunc", "gaus(0) + gaus(3) + gaus(6)", hist->GetXaxis()->GetXmin(), hist->GetXaxis()->GetXmax());
    TF1* fitFunc = new TF1("fitFunc", "gaus(0) + gaus(3) + gaus(6) + [9]", hist->GetXaxis()->GetXmin(), hist->GetXaxis()->GetXmax());    

    // Set the fitting range (e.g., from -1 to 1 in log scale)
    double fitRangeMin = 3.0; // Set the minimum value for fitting region
    double fitRangeMax = 8.0;  // Set the maximum value for fitting region
    fitFunc->SetRange(fitRangeMin, fitRangeMax);    

    // Set initial parameters for the first Gaussian
    fitFunc->SetParameter(0, 4); // Amplitude
    fitFunc->SetParameter(1, 7);    // Mean
    fitFunc->SetParameter(2, 0.1);     // Sigma
    fitFunc->SetParLimits(0, 1, 8); // Lower bound: 0.0, Upper bound: 10.0
    fitFunc->SetParLimits(2, 0.001, 0.2); // Lower bound: 0.0, Upper bound: 10.0

    // Set initial parameters for the second Gaussian
    fitFunc->SetParameter(3, 4); // Amplitude
    fitFunc->SetParameter(4, 5);    // Mean
    fitFunc->SetParameter(5, 0.1);     // Sigma
    fitFunc->SetParLimits(3, 1, 8); // Lower bound: 0.0, Upper bound: 10.0
    fitFunc->SetParLimits(5, 0.001, 0.2); // Lower bound: 0.0, Upper bound: 10.0

    // Set initial parameters for the third Gaussian
    fitFunc->SetParameter(6, 3); // Amplitude
    fitFunc->SetParameter(7, 3);    // Mean
    fitFunc->SetParameter(8, 0.2);     // Sigma
    fitFunc->SetParLimits(6, 1, 8); // Lower bound: 0.0, Upper bound: 10.0
    fitFunc->SetParLimits(8, 0.001, 0.2); // Lower bound: 0.0, Upper bound: 10.0

    // Set initial parameters for the constant background
    fitFunc->SetParameter(9, 0.2); // Initial constant value
    fitFunc->SetParLimits(9, 0.01, 0.5);

    // Display the histogram
    TCanvas* canvas = new TCanvas("canvas", "Analysis Canvas", 800, 1600);
    canvas->Divide(1, 2);
    canvas->SetLogy();
    canvas->cd(1);
    gPad->SetLogy();
    graph->Draw();
    canvas->cd(2);
    hist->Draw();
    //hist->Fit(fitFunc, "R", fitRangeMin, fitRangeMax);
    hist->Fit(fitFunc, "R");
    canvas->cd(2);
    canvas->Draw();

    //
    // Get the count rates of 1 p.e., 2 p.e., and 3 p.e.
    double countRate1pe = fitFunc->GetParameter(1);
    double countRate2pe = fitFunc->GetParameter(4);
    double countRate3pe = fitFunc->GetParameter(7);
    std::cout << countRate1pe << " " << countRate2pe << " " << countRate3pe << std::endl;

    int numPoints = graph->GetN();
    bool is1pefound = false;
    bool is2pefound = false;
    bool is3pefound = false;
    double DAC1pe = 0.;
    double DAC2pe = 0.;
    double DAC3pe = 0.;
    int Ninterval12 = 0;
    int Ninterval23 = 0;
    for (int i = 0; i < numPoints; ++i) {
        double x, y;
        graph->GetPoint(i, x, y);
        std::cout << "Point " << i << ": x = " << x << ", logy = " << TMath::Log10(y) << std::endl;

        if (TMath::Abs(TMath::Log10(y)-countRate1pe) < 0.2) {
           is1pefound = true;
           std::cout << " this data point belongs to the 1 photon-equivalent" << std::endl;
        } else if ((TMath::Abs(TMath::Log10(y)-countRate1pe) >= 0.2) &&
                   (is1pefound == true) && (TMath::Abs(TMath::Log10(y)-countRate2pe) >= 0.2) &&
                   (is2pefound == false)) {
           DAC1pe += x;
           Ninterval12++;
           std::cout << "Interval 1 and 2 " << std::endl;
        } else if ((TMath::Abs(TMath::Log10(y)-countRate2pe) < 0.2) && (is1pefound == true)) {
           is2pefound = true;
           std::cout << " this data point belongs to the 2 photon-equivalent" << std::endl;
        } else if ((TMath::Abs(TMath::Log10(y)-countRate2pe) >= 0.2) && (is2pefound == true) &&
                   (TMath::Abs(TMath::Log10(y)-countRate3pe) >= 0.2) && (is3pefound == false)) {
           DAC2pe += x;
           Ninterval23++;
           std::cout << "Interval 2 and 3 " << std::endl;
        } else if ((TMath::Abs(TMath::Log10(y)-countRate3pe) < 0.2) && (is2pefound == true)) {
           is3pefound = true;
           std::cout << " this data point belongs to the 3 photon-equivalent" << std::endl;
        }

/*        if ((TMath::Abs(TMath::Log10(y)-countRate3pe) < 0.2) && (is2pefound == true)) {
           std::cout << " this data point belongs to the 3 photon-equivalent" << std::endl;
        } else if ((TMath::Abs(TMath::Log10(y)-countRate2pe) < 0.2) && (is1pefound == true)) {
           maxDAC2pe = x;
           is2pefound = true;
           std::cout << " this data point belongs to the 2 photon-equivalent" << std::endl;
        } else if (TMath::Abs(TMath::Log10(y)-countRate1pe) < 0.2) {
           maxDAC1pe = x;
           is1pefound = true;
           std::cout << " this data point belongs to the 1 photon-equivalent" << std::endl;
        }
*/
    }
    DAC1pe/=Ninterval12;
    DAC2pe/=Ninterval23;

    std::cout << "DAC1pe " << DAC1pe << " DAC2pe " << DAC2pe << std::endl;

    canvas->cd(1);
    TLine* line1 = new TLine(DAC1pe, 0, DAC1pe, graphYMax);
    TLine* line2 = new TLine(DAC2pe, 0, DAC2pe, graphYMax);
    line1->SetLineColor(kRed); // Set line color to red
    line1->Draw();    
    line2->SetLineColor(kRed); // Set line color to red
    line2->Draw();
//    TString* stringGain = new TString("%f", DAC2pe-DAC1pe);
//    TLatex* textGain = new TLatex(400, 1e6, stringGain->Data());
    TLatex* textGain = new TLatex(400, 1e6, Form("Gain(DAC) = %4.2f", DAC2pe-DAC1pe));
    textGain->Draw();
    canvas->Update();
    //canvas->SaveAs("pulseheightfit.pdf");
    canvas->SaveAs(Form("pic/pulseheight%03d_%02d_%02d.pdf", iCIRASAME, iASIC, iChannel));
    // Close the file
    // file->Close();
}

void pulseheightfit(const char* fileName) {
    // Replace "rootFile.root" with the path to your ROOT file
      for(int iCIRASAME=1, iCIRASAME<=18, iCIRASAME++){
         for(int iASIC=1, iASIC<=4, iASIC++){
            for(int iChannel=1, iChannel<=32, iChannel++){
               analyzeRootFile(fileName, iCIRASAME, iASIC, iChannel);
            }
         }
      }
    
}
