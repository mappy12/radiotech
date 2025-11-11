/*
Modulation testing program - Quadrature Modulation
*/
#define _USE_MATH_DEFINES
#include <windows.h>
#include <stdio.h>
#include <math.h>
#include "fftw3.h"

#define FFT_POINTS 100000
#define FFT_POINTS2 ((double)FFT_POINTS * (double)FFT_POINTS)
#define FS 1.0E+6

const double F = 200000; // Frequency of the input signal
//const double F = 100000;
//const double F = 50000;
const double DT = 1.0 / FS; // Sampling interval
const double DF = FS / FFT_POINTS; // Frequency step

OPENFILENAMEA ofn;
HANDLE hFile;
fftw_complex* In, * Out;
fftw_plan pDir;
double S[FFT_POINTS];

int G1(LPWORD X);

int APIENTRY main(HINSTANCE hInstance, HINSTANCE hPrevInstance,
    LPSTR lpCmdLine, int nCmdShow)
{
    char Txt[512];
    sprintf_s(Txt, "quadrature_modulation.txt");

    memset(&ofn, 0, sizeof(OPENFILENAME));
    ofn.lStructSize = sizeof(OPENFILENAME);
    ofn.hwndOwner = NULL;
    ofn.lpstrFilter = "Data Files(*.dat)\0*.dat;\0Any Files(*.*)\0\*.*\0";
    ofn.lpstrFile = Txt;
    ofn.nFilterIndex = 1;
    ofn.nMaxFile = sizeof(Txt);
    ofn.lpstrTitle = "Save quadrature data";
    ofn.Flags = OFN_EXPLORER | OFN_OVERWRITEPROMPT;

    if (!GetSaveFileNameA(&ofn)) return FALSE;

    hFile = CreateFileA(ofn.lpstrFile, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
    {
        MessageBoxW(NULL, L"File is not created", L"FFT testing", MB_OK);
        return FALSE;
    }

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

    // Quadrature modulation with G1 generator
    ZeroMemory(In, FFT_POINTS * sizeof(fftw_complex));
    int NP = (int)(100.0 / F / DT);
    WORD X = 0xF0FA;
    double Mag1 = 1.0, Mag2 = 1.0;

    for (int i = 0; i < FFT_POINTS; i++)
    {
        if (i % (NP / 2) == 0)
        {
            Mag2 = Mag1;
            if (G1(&X) == 0)
                Mag1 = -1.0;
            else
                Mag1 = 1.0;
        }

        // I * cos + Q * sin quadrature modulation
        In[i][0] = Mag1 * cos(2 * M_PI * F * DT * i);
        In[i][0] = In[i][0] + Mag2 * sin(2 * M_PI * F * DT * i);
        S[i] = In[i][0];
    }

    // Perform FFT
    fftw_execute(pDir);

    // Write results to file
    char buffer[256];
    DWORD ByteNum;
    double P;

    sprintf_s(buffer, "Frequency\tSignal\tPower\n");
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);

    for (int i = 0; i < FFT_POINTS / 2; i++)
    {
        P = (Out[i][0] * Out[i][0] + Out[i][1] * Out[i][1]) / FFT_POINTS2;
        sprintf_s(buffer, "%.8g\t%.8g\t%.8g\n", i * DF, S[i], P);
        WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    }

    MessageBoxA(NULL, "Quadrature modulation completed!", "Modulation testing", MB_OK);

    CloseHandle(hFile);
    VirtualFree(In, 0, MEM_RELEASE);
    VirtualFree(Out, 0, MEM_RELEASE);
    fftw_destroy_plan(pDir);

    return 0;
}

int G1(LPWORD X)
{
    int Result;
    if ((*X & 0x0004) != 0) Result = 1; else Result = 0;
    *X = ((*X >> 1) & 0x00FF) | ((*X ^ (*X << 4)) & 0x0010) << 4;
    return Result;
}