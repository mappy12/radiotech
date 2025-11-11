/*
Modulation testing program - Balance Modulation with k=0.5
*/
#define _USE_MATH_DEFINES
#include <windows.h>
#include <stdio.h>
#include <math.h>
#include "fftw3.h"

#define FFT_POINTS 100000
#define FFT_POINTS2 ((double)FFT_POINTS * (double)FFT_POINTS)
#define FS 1.0E+6

const double F = 50000; // Frequency of the input signal
const double FMOD = 8000; // Frequency of the baseband signal
const double DT = 1.0 / FS; // Sampling interval
const double DF = FS / FFT_POINTS; // Frequency step

double Mag = 1.0; // Magnitude of the input signal

OPENFILENAMEA ofn;
HANDLE hFile;
fftw_complex* In, * Out;
fftw_plan pDir;

double S[FFT_POINTS];

int APIENTRY main(HINSTANCE hInstance, HINSTANCE hPrevInstance,
    LPSTR lpCmdLine, int nCmdShow)
{
    char Txt[512];
    sprintf_s(Txt, "balance_modulation_k0.5.txt");

    memset(&ofn, 0, sizeof(OPENFILENAME));
    ofn.lStructSize = sizeof(OPENFILENAME);
    ofn.hwndOwner = NULL;
    ofn.lpstrFilter = "Data Files(*.dat)\0*.dat;\0Any Files(*.*)\0\*.*\0";
    ofn.lpstrFile = Txt;
    ofn.nFilterIndex = 1;
    ofn.nMaxFile = sizeof(Txt);
    ofn.lpstrTitle = "Save file";
    ofn.Flags = OFN_EXPLORER | OFN_OVERWRITEPROMPT;

    if (!GetSaveFileNameA(&ofn)) return FALSE;

    hFile = CreateFileA(ofn.lpstrFile, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
    {
        MessageBoxW(NULL, L"File is not created", L"FFT testing", MB_OK);
        return FALSE;
    }

    // Memory allocation
    In = (fftw_complex*)VirtualAlloc(NULL, FFT_POINTS * sizeof(fftw_complex), MEM_COMMIT, PAGE_READWRITE);
    Out = (fftw_complex*)VirtualAlloc(NULL, FFT_POINTS * sizeof(fftw_complex), MEM_COMMIT, PAGE_READWRITE);

    if ((In == NULL) || (Out == NULL))
    {
        MessageBoxW(NULL, L"Not enough memory", L"FFT testing", MB_OK);
        return FALSE;
    }

    pDir = fftw_plan_dft_1d(FFT_POINTS, In, Out, FFTW_FORWARD, FFTW_ESTIMATE);

    if (pDir == NULL)
    {
        MessageBoxW(NULL, L"FFTW plan was not created", L"FFT testing", MB_OK);
        return FALSE;
    }

    // Generate Balance Modulated signal with k=0.5
    ZeroMemory(In, FFT_POINTS * sizeof(fftw_complex));

    double k = 0.0; // Carrier suppression coefficient
    //k = 0.5
    //k = 0.1
    //k = 0.0
    //k = 0.25


    for (int i = 0; i < FFT_POINTS; i++)
    {
        // Balance modulation: carrier is suppressed by factor k
        double modulation = 0.75 * cos(2 * M_PI * FMOD * DT * i);
        In[i][0] = S[i] = (k + modulation) * cos(2 * M_PI * F * DT * i);
    }

    // Perform FFT
    fftw_execute(pDir);

    // Write results to file
    char buffer[256];
    DWORD ByteNum;
    double P;

    // Write header
    sprintf_s(buffer, "Frequency\tSignal\tPower\n");
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);

    // Write data (only positive frequencies)
    for (int i = 0; i < FFT_POINTS / 2; i++)
    {
        P = (Out[i][0] * Out[i][0] + Out[i][1] * Out[i][1]) / FFT_POINTS2;

        sprintf_s(buffer, "%.8g\t%.8g\t%.8g\n", i * DF, S[i], P);
        WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    }

    MessageBoxA(NULL, "Balance modulation with k=0.5 completed!", "Modulation testing", MB_OK);

    // Cleanup
    CloseHandle(hFile);
    VirtualFree(In, 0, MEM_RELEASE);
    VirtualFree(Out, 0, MEM_RELEASE);
    fftw_destroy_plan(pDir);

    return 0;
}