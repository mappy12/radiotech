/*
Modulation testing program
*/
#define _USE_MATH_DEFINES
#include <windows.h>
#include <stdio.h>
#include <math.h>
#include "fftw3.h"
#define FFT_POINTS 100000
//#define FFT_POINTS 50000
#define FFT_POINTS2 ((double)FFT_POINTS * (double)FFT_POINTS)
#define FS 1.0E+6
const double F = 50000; // Frequency of the input signal
const double FMOD = 8000; // Frequency of the baseband signal
///const double FMOD = 2000;
///const double FMOD = 8000;
const double DT = 1.0 / FS; // Sampling interval
const double DF = FS / FFT_POINTS; // Frequency step
double Mag = 1.0; // Magnitude of the input signal
OPENFILENAMEA ofn;
HANDLE hFile;
fftw_complex* In, * Inv, * Out; // Arrays for FFT
fftw_plan pDir, pInv;
double S[FFT_POINTS];
double Noise();
int G1(LPWORD X);
int APIENTRY main(HINSTANCE hInstance, HINSTANCE hPrevInstance,
	LPSTR lpCmdLine, int nCmdShow)
{
	char Txt[512];
	sprintf_s(Txt, "samples.txt");
	memset(&ofn, 0, sizeof(OPENFILENAME));
	ofn.lStructSize = sizeof(OPENFILENAME);
	ofn.hwndOwner = NULL;
	ofn.lpstrFilter = "Data Files(*.dat)\0*.dat;\0Any Files(*.*)\0\*.*\0";
	ofn.lpstrFile = Txt;
	ofn.nFilterIndex = 1;
	ofn.nMaxFile = sizeof(Txt);
	ofn.lpstrTitle = "Открыть файл";
	ofn.Flags = OFN_EXPLORER | OFN_OVERWRITEPROMPT;
	if (!GetSaveFileNameA(&ofn)) return FALSE;
	hFile = CreateFileA(ofn.lpstrFile, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile == INVALID_HANDLE_VALUE)
	{
		MessageBoxW(NULL, L"File is not created", L"FFT testing", MB_OK);
		return FALSE;
	}
	In = (fftw_complex*)VirtualAlloc(NULL, (FFT_POINTS) * sizeof(fftw_complex), MEM_COMMIT,
		PAGE_READWRITE);
	Inv = (fftw_complex*)VirtualAlloc(NULL, (FFT_POINTS) * sizeof(fftw_complex), MEM_COMMIT,
		PAGE_READWRITE);
	Out = (fftw_complex*)VirtualAlloc(NULL, (FFT_POINTS) * sizeof(fftw_complex), MEM_COMMIT,
		PAGE_READWRITE);
	if ((In == NULL) || (Out == NULL) || (Out == NULL))
	{
		MessageBoxW(NULL, L"Not enough memory", L"FFT testing", MB_OK);
		return FALSE;
	}
	pDir = fftw_plan_dft_1d(FFT_POINTS, In, Out, FFTW_FORWARD, FFTW_ESTIMATE);
	pInv = fftw_plan_dft_1d(FFT_POINTS, Out, Inv, FFTW_BACKWARD, FFTW_ESTIMATE);
	if ((pDir == NULL) || (pInv == NULL))
	{
		MessageBoxW(NULL, L"FFTW plan was not created", L"FFT testing", MB_OK);
		return FALSE;
	}


	// Для исследования амплитудной манипуляции
	ZeroMemory(In, FFT_POINTS * sizeof(fftw_complex));

	// Длительность импульса в отсчетах (изменять этот параметр)
	int impulse_duration = 50; // ← ИЗМЕНЯТЬ ЭТО ЗНАЧЕНИЕ для изменения длительности (уменьшение в 2 раза)
    //int impulse_duration = 100; - изначальный
    //int impulse_duration = 25; - уменьшение в 4 раза

	// Частота следования импульсов (изменять этот параметр)
	int impulse_period = 200; // ← ИЗМЕНЯТЬ ЭТО ЗНАЧЕНИЕ для изменения частоты

	for (int i = 0; i < FFT_POINTS; i++)
	{
		// Амплитудная манипуляция (ASK)
		if ((i % impulse_period) < impulse_duration)
			Mag = 1.0;  // импульс
		else
			Mag = 0.0;  // пауза

		In[i][0] = S[i] = Mag * cos(2 * M_PI * F * DT * i);
	}


	//for (int i = 0; i < NP/2; i++) In[i][0] = S[i] = Mag * cos(2 * M_PI * F * DT * i);
	//In[0][0] = S[0] = (double)FFT_POINTS;
	//for (int i = 0; i < NP; i++) In[i][0] = S[i] = (double)i;
	//for (int i = NP; i < 2 * NP; i++) In[i][0] = S[i] = (double)(NP - i%NP);
	//int Carrier = 5000;
	//double k = 1.0;
	char buffer[256];
	DWORD ByteNum;
	double P, Q;
	fftw_execute(pDir);
	for (int i = 0; i < FFT_POINTS; i++)
	{
		P = (Out[i][0] * Out[i][0] + Out[i][1] * Out[i][1]) / FFT_POINTS2;
		if (P > 0) sprintf_s(buffer, "%.8g\t%.8g\t%.8g\t%.8g\t%.8g\r\n", i * DF, S[i], P,
			Inv[i][0] / FFT_POINTS, 10 * log10(P));
		else sprintf_s(buffer, "%.8g\t%.8g\t%.8g\t%.8g\t%.8g\r\n", i * DF, S[i], P, Inv[i][0] /
			FFT_POINTS, -350.0);
		WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
	}
	MessageBoxA(NULL, "Game over", "Modulation testing", MB_OK);
	CloseHandle(hFile);
	VirtualFree(In, 0, MEM_RELEASE);
	VirtualFree(Out, 0, MEM_RELEASE);
	VirtualFree(Inv, 0, MEM_RELEASE);
	fftw_destroy_plan(pDir);
	fftw_destroy_plan(pInv);
	return 0;
}
double Noise()
{
	double T = 0.0;
	for (int j = 0; j < 12; j++) T += ((double)rand() / RAND_MAX);
	return (T - 6);
}
int G1(LPWORD X) // G1 generator
{
	int Result;
	if ((*X & 0x0004) != 0) Result = 1; else Result = 0;
	*X = ((*X >> 1) & 0x00FF) | ((*X ^ (*X << 4)) & 0x0010) << 4;
	return Result;
}
