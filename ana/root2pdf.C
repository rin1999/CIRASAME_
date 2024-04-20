#include <TFile.h>
#include <TGraph.h>
#include <TCanvas.h>
#include <TPDF.h>
#include <TKey.h>

void root2pdf(const char* filename) {
    // Open the ROOT file
    TFile* file = new TFile(filename);
    if (!file || file->IsZombie()) {
        printf("Error: Unable to open file '%s'\n", filename);
        return;
    }

    // Create a canvas
    TCanvas* canvas = new TCanvas("canvas", "TGraphs", 800, 600);

    // Create a PDF to save all TGraphs
    TPDF* pdf = new TPDF("output.pdf", 0);

    // Get the list of TGraphs from the file
    TList* graphs = file->GetListOfKeys();
    if (!graphs) {
        printf("Error: No TGraphs found in file '%s'\n", filename);
        file->Close();
        return;
    }

    // Loop over all TGraphs
    TIter next(graphs);
    TKey* key;
    while ((key = (TKey*)next())) {
        TObject* obj = key->ReadObj();
        if (obj->InheritsFrom("TGraph")) {
            TGraph* graph = (TGraph*)obj;
            TString gtitle = graph->GetTitle();
            std::cout << "Printing the graph " << gtitle << std::endl;
            // Create a new page for each TGraph
            canvas->Clear();
            graph->Draw("AP");
            pdf->NewPage();
            canvas->Update();
        }
    }

    pdf->Close();
    file->Close();
}
