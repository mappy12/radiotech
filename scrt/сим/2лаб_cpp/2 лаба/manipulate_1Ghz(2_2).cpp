/*
Modulation testing program - Frequency Shift Keying (FSK)
*/
#define _USE_MATH_DEFINES
#include <windows.h>
#include <stdio.h>
#include <math.h>
#include "fftw3.h"

#define FFT_POINTS 100000
#define FFT_POINTS2 ((double)FFT_POINTS * (double)FFT_POINTS)
#define FS 1.0E+6

const double F = 50000;          // Carrier frequency
const double F1 = 5000;          // Frequency for symbol "0"
const double F2 = 10000;         // Frequency for symbol "1"
const double DT = 1.0 / FS;      // Sampling interval
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
    sprintf_s(Txt, "fsk_modulation.txt");
    
    memset(&ofn, 0, sizeof(OPENFILENAME));
    ofn.lStructSize = sizeof(OPENFILENAME);
    ofn.hwndOwner = NULL;
    ofn.lpstrFilter = "Data Files(*.dat)\0*.dat;\0Any Files(*.*)\0\*.*\0";
    ofn.lpstrFile = Txt;
    ofn.nFilterIndex = 1;
    ofn.nMaxFile = sizeof(Txt);
    ofn.lpstrTitle = "Save FSK data";
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
    
    // Generate FSK signal
    ZeroMemory(In, FFT_POINTS * sizeof(fftw_complex));
    int NP = (int)(100.0 / F / DT);
    double FTR;
    
    for (int i = 0; i < FFT_POINTS; i++)
    {
        if (i % NP < NP / 2) 
            FTR = F + F1;  // Symbol "0"
        else 
            FTR = F + F2;  // Symbol "1"
            
        In[i][0] = S[i] = Mag * cos(2 * M_PI * FTR * DT * i);
    }
    
    // Perform FFT
    fftw_execute(pDir);
    
    // Write results to file
    char buffer[256];
    DWORD ByteNum;
    double P;
    
    // Write header with parameters
    sprintf_s(buffer, "FSK Modulation Parameters: F=%d, F1=%d, F2=%d\n", (int)F, (int)F1, (int)F2);
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    sprintf_s(buffer, "Frequency\tSignal\tPower\n");
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    
    // Write data (only positive frequencies)
    for (int i = 0; i < FFT_POINTS/2; i++)
    {
        P = (Out[i][0] * Out[i][0] + Out[i][1] * Out[i][1]) / FFT_POINTS2;
        sprintf_s(buffer, "%.8g\t%.8g\t%.8g\n", i * DF, S[i], P);
        WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    }
    
    MessageBoxA(NULL, "FSK modulation completed!", "FSK testing", MB_OK);
    
    // Cleanup
    CloseHandle(hFile);
    VirtualFree(In, 0, MEM_RELEASE);
    VirtualFree(Out, 0, MEM_RELEASE);
    fftw_destroy_plan(pDir);
    
    return 0;
}