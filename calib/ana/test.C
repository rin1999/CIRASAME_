#include <TCanvas.h>
#include <TGraph.h>
#include <TF1.h>
#include <TFile.h>
#include <iostream>
#include <fstream>

using namespace std;

// Function to perform fitting and plot graph
void fitAndPlot(int iteration) {
    // Generate some sample data
    const int N = 10;
    double x[N] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    double y[N] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29};

    // Create a TGraph
    TGraph *graph = new TGraph(N, x, y);

    // Fit the graph with a simple linear function
    TF1 *fitFunc = new TF1("fitFunc", "pol1");
    graph->Fit(fitFunc, "Q");

    // Create a canvas
    TCanvas *canvas = new TCanvas("canvas", "Canvas", 800, 600);

    // Draw the graph
    graph->Draw("AP");

    // Store the canvas in a PDF file
    TString pdfFileName = Form("output_plots.pdf");
    if (iteration == 0)
        canvas->Print(pdfFileName + "["); // Open PDF for multiple pages
    else
        canvas->Print(pdfFileName);

    // Output fit result to a text file
    ofstream outFile("fit_results.txt", ios::app); // Append mode
    outFile << "Iteration: " << iteration << endl;
    outFile << "Fit Parameters: Slope = " << fitFunc->GetParameter(1) << ", Intercept = " << fitFunc->GetParameter(0) << endl;
    outFile.close();
}

void multiplePagePDF() {
    // Number of iterations
    const int iterations = 5;

    // Loop through each iteration
    for (int i = 0; i < iterations; ++i) {
        fitAndPlot(i);
    }

    // Close PDF after all pages
    TCanvas *canvas = new TCanvas("canvas", "Canvas", 800, 600);
    canvas->Print("output_plots.pdf]");
}

void sampleMacro() {
    multiplePagePDF();
}
