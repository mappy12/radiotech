/*
Modulation testing program - Frequency Modulation
Формула для вычисления индекса модуляции: m = FD / FMOD
где:
FD - девиация частоты (frequency deviation)
FMOD - частота модулирующего сигнала
*/

#define _USE_MATH_DEFINES
#include <windows.h>
#include <stdio.h>
#include <math.h>
#include "fftw3.h"

#define FFT_POINTS 1000000
#define FFT_POINTS2 ((double)FFT_POINTS * (double)FFT_POINTS)
#define FS 20.0E+6

const double F = 2000000;        // Carrier frequency
const double FD = 100000;        // Frequency deviation
const double FMOD = 20;          // Modulation frequency
//const double FMOD = 10;
const double DT = 1.0 / FS;      // Sampling interval
const double DF = FS / FFT_POINTS; // Frequency step

// ИНДЕКС МОДУЛЯЦИИ - МЕНЯТЬ ЭТО ЗНАЧЕНИЕ
const double m = 10000; 
//const double m = 100;
//const double m = 10000;

// m = FD / FMOD = 100000 / 10 = 10000
//
// Другие варианты для экспериментов:
// const double m = 2.0;         // Малый индекс модуляции
// const double m = 10.0;        // Средний индекс модуляции
// const double m = 100.0;       // Большой индекс модуляции

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
    sprintf_s(Txt, "fm_signal_m_%.0f.txt", m);

    memset(&ofn, 0, sizeof(OPENFILENAME));
    ofn.lStructSize = sizeof(OPENFILENAME);
    ofn.hwndOwner = NULL;
    ofn.lpstrFilter = "Data Files(*.dat)\0*.dat;\0Any Files(*.*)\0\*.*\0";
    ofn.lpstrFile = Txt;
    ofn.nFilterIndex = 1;
    ofn.nMaxFile = sizeof(Txt);
    ofn.lpstrTitle = "Save FM data";
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

    // Generate FM signal
    ZeroMemory(In, FFT_POINTS * sizeof(fftw_complex));
    for (int i = 0; i < FFT_POINTS; i++)
    {
        In[i][0] = S[i] = Mag * cos(2 * M_PI * F * DT * i + m * sin(2 * M_PI * FMOD * DT * i));
    }

    // Perform FFT
    fftw_execute(pDir);

    // Write results to file
    char buffer[256];
    DWORD ByteNum;
    double P;

    // Write header with parameters
    sprintf_s(buffer, "FM Modulation Parameters: m=%.1f, F=%d, FMOD=%d, FD=%d\n", m, (int)F, (int)FMOD, (int)FD);
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    sprintf_s(buffer, "Frequency\tSignal\tPower\n");
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);

    // Write data (only positive frequencies)
    for (int i = 0; i < FFT_POINTS / 2; i++)
    {
        P = (Out[i][0] * Out[i][0] + Out[i][1] * Out[i][1]) / FFT_POINTS2;
        sprintf_s(buffer, "%.8g\t%.8g\t%.8g\n", i * DF, S[i], P);
        WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    }

    sprintf_s(buffer, "\nBandwidth analysis for m=%.1f:\n", m);
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    sprintf_s(buffer, "Theoretical bandwidth: ~%.0f Hz\n", 2 * (m * FMOD + FMOD));
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);

    char msg[100];
    sprintf_s(msg, "FM modulation completed! m=%.1f", m);
    MessageBoxA(NULL, msg, "FM testing", MB_OK);

    // Cleanup
    CloseHandle(hFile);
    VirtualFree(In, 0, MEM_RELEASE);
    VirtualFree(Out, 0, MEM_RELEASE);
    fftw_destroy_plan(pDir);

    return 0;
}