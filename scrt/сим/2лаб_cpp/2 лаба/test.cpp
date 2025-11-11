/*
Modulation testing program - Balance Modulation and SSB
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
fftw_complex* In, * Inv, * Out; // Arrays for FFT
fftw_plan pDir, pInv;
double S[FFT_POINTS];

double Noise();
int G1(LPWORD X);

// Функция для подавления несущей
void suppress_carrier(int carrier_bin, double k_suppress)
{
    // Подавление несущей в положительных частотах
    Out[carrier_bin][0] *= k_suppress;
    Out[carrier_bin][1] *= k_suppress;
    
    // Подавление несущей в отрицательных частотах (симметрично)
    Out[FFT_POINTS - carrier_bin][0] *= k_suppress;
    Out[FFT_POINTS - carrier_bin][1] *= k_suppress;
}

// Функция для формирования ОБП (подавление одной боковой полосы)
void create_ssb(int carrier_bin, bool suppress_upper)
{
    if (suppress_upper) {
        // Подавление верхней боковой полосы (USB) - оставляем LSB
        for (int i = carrier_bin + 1; i < FFT_POINTS/2; i++) {
            Out[i][0] = 0;
            Out[i][1] = 0;
            Out[FFT_POINTS - i][0] = 0;
            Out[FFT_POINTS - i][1] = 0;
        }
    } else {
        // Подавление нижней боковой полосы (LSB) - оставляем USB
        for (int i = 1; i < carrier_bin; i++) {
            Out[i][0] = 0;
            Out[i][1] = 0;
            Out[FFT_POINTS - i][0] = 0;
            Out[FFT_POINTS - i][1] = 0;
        }
    }
}

// Функция для вычисления мощности в полосе
double calculate_band_power(int start_bin, int end_bin)
{
    double total_power = 0;
    for (int i = start_bin; i <= end_bin; i++) {
        double P = (Out[i][0] * Out[i][0] + Out[i][1] * Out[i][1]) / FFT_POINTS2;
        total_power += P;
    }
    return total_power;
}

// Функция для нахождения полосы, содержащей 90% мощности
void find_90_percent_bandwidth(int carrier_bin, double& bandwidth, double& total_power)
{
    total_power = calculate_band_power(0, FFT_POINTS/2);
    double target_power = 0.9 * total_power;
    
    // Ищем центральную полосу, содержащую 90% мощности
    int left = carrier_bin;
    int right = carrier_bin;
    double current_power = calculate_band_power(carrier_bin, carrier_bin);
    
    while (current_power < target_power) {
        // Расширяем полосу в обе стороны
        left = max(1, left - 1);
        right = min(FFT_POINTS/2 - 1, right + 1);
        current_power = calculate_band_power(left, right);
    }
    
    bandwidth = (right - left) * DF;
}

int APIENTRY main(HINSTANCE hInstance, HINSTANCE hPrevInstance,
    LPSTR lpCmdLine, int nCmdShow)
{
    char Txt[512];
    sprintf_s(Txt, "modulation_study.txt");
    memset(&ofn, 0, sizeof(OPENFILENAME));
    ofn.lStructSize = sizeof(OPENFILENAME);
    ofn.hwndOwner = NULL;
    ofn.lpstrFilter = "Data Files(*.dat)\0*.dat;\0Any Files(*.*)\0\*.*\0";
    ofn.lpstrFile = Txt;
    ofn.nFilterIndex = 1;
    ofn.nMaxFile = sizeof(Txt);
    ofn.lpstrTitle = "Сохранить файл";
    ofn.Flags = OFN_EXPLORER | OFN_OVERWRITEPROMPT;
    
    if (!GetSaveFileNameA(&ofn)) return FALSE;
    
    hFile = CreateFileA(ofn.lpstrFile, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
    {
        MessageBoxW(NULL, L"File is not created", L"FFT testing", MB_OK);
        return FALSE;
    }
    
    // Выделение памяти
    In = (fftw_complex*)VirtualAlloc(NULL, FFT_POINTS * sizeof(fftw_complex), MEM_COMMIT, PAGE_READWRITE);
    Inv = (fftw_complex*)VirtualAlloc(NULL, FFT_POINTS * sizeof(fftw_complex), MEM_COMMIT, PAGE_READWRITE);
    Out = (fftw_complex*)VirtualAlloc(NULL, FFT_POINTS * sizeof(fftw_complex), MEM_COMMIT, PAGE_READWRITE);
    
    if ((In == NULL) || (Out == NULL) || (Inv == NULL))
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
    
    char buffer[512];
    DWORD ByteNum;
    double P, Q;
    
    // Определение номера гармоники несущей
    int Carrier = (int)(F / DF);
    
    // Исследование разных видов модуляции
    double k_values[] = {1.0, 0.5, 0.25, 0.0}; // k=1.0 - классическая АМ, k=0 - полное подавление
    
    for (int mod_type = 0; mod_type < 4; mod_type++) {
        ZeroMemory(In, FFT_POINTS * sizeof(fftw_complex));
        
        // Создание АМ сигнала с псевдослучайной модуляцией
        WORD X = 0xF0FA;
        for (int i = 0; i < FFT_POINTS; i++)
        {
            if (i % 100 == 0) Mag = G1(&X); // Псевдослучайная модуляция
            In[i][0] = S[i] = Mag * (1.0 + 0.75 * cos(2 * M_PI * FMOD * DT * i)) * cos(2 * M_PI * F * DT * i);
        }
        
        // Прямое преобразование Фурье
        fftw_execute(pDir);
        
        double k_suppress = k_values[mod_type];
        const char* mod_name = "";
        
        switch (mod_type) {
            case 0: 
                mod_name = "Классическая АМ";
                break;
            case 1: 
                mod_name = "БМ с k=0.5";
                suppress_carrier(Carrier, k_suppress);
                break;
            case 2: 
                mod_name = "БМ с k=0.25"; 
                suppress_carrier(Carrier, k_suppress);
                break;
            case 3: 
                mod_name = "БМ с k=0 (полное подавление)";
                suppress_carrier(Carrier, k_suppress);
                break;
        }
        
        // Обратное преобразование Фурье для получения модифицированного сигнала
        fftw_execute(pInv);
        
        // Анализ полосы пропускания
        double bandwidth, total_power;
        find_90_percent_bandwidth(Carrier, bandwidth, total_power);
        
        // Запись информации о модуляции
        sprintf_s(buffer, "\n%s: k=%.2f, Несущая: %d, Ширина полосы (90%%): %.1f Гц, Общая мощность: %.6f\n", 
                 mod_name, k_suppress, Carrier, bandwidth, total_power);
        WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
        
        // Запись данных СПМ
        sprintf_s(buffer, "Frequency\tPower_%s\tPower_dB_%s\n", mod_name, mod_name);
        WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
        
        for (int i = 0; i < FFT_POINTS/2; i++) {
            P = (Out[i][0] * Out[i][0] + Out[i][1] * Out[i][1]) / FFT_POINTS2;
            if (P > 0) 
                sprintf_s(buffer, "%.8g\t%.8g\t%.8g\n", i * DF, P, 10 * log10(P));
            else 
                sprintf_s(buffer, "%.8g\t%.8g\t%.8g\n", i * DF, P, -350.0);
            WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
        }
    }
    
    // Исследование ОБП модуляции
    sprintf_s(buffer, "\n=== ОДНОПОЛОСНАЯ МОДУЛЯЦИЯ (SSB) ===\n");
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    
    // LSB (нижняя боковая полоса)
    ZeroMemory(In, FFT_POINTS * sizeof(fftw_complex));
    WORD X = 0xF0FA;
    for (int i = 0; i < FFT_POINTS; i++) {
        if (i % 100 == 0) Mag = G1(&X);
        In[i][0] = S[i] = Mag * (1.0 + 0.75 * cos(2 * M_PI * FMOD * DT * i)) * cos(2 * M_PI * F * DT * i);
    }
    
    fftw_execute(pDir);
    suppress_carrier(Carrier, 0.0); // Полное подавление несущей
    create_ssb(Carrier, false); // Подавление LSB, оставляем USB
    fftw_execute(pInv);
    
    double bandwidth_usb, power_usb;
    find_90_percent_bandwidth(Carrier, bandwidth_usb, power_usb);
    sprintf_s(buffer, "USB (Upper Side Band): Ширина полосы: %.1f Гц, Мощность: %.6f\n", bandwidth_usb, power_usb);
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    
    // USB (верхняя боковая полоса)  
    ZeroMemory(In, FFT_POINTS * sizeof(fftw_complex));
    X = 0xF0FA;
    for (int i = 0; i < FFT_POINTS; i++) {
        if (i % 100 == 0) Mag = G1(&X);
        In[i][0] = S[i] = Mag * (1.0 + 0.75 * cos(2 * M_PI * FMOD * DT * i)) * cos(2 * M_PI * F * DT * i);
    }
    
    fftw_execute(pDir);
    suppress_carrier(Carrier, 0.0); // Полное подавление несущей
    create_ssb(Carrier, true); // Подавление USB, оставляем LSB
    fftw_execute(pInv);
    
    double bandwidth_lsb, power_lsb;
    find_90_percent_bandwidth(Carrier, bandwidth_lsb, power_lsb);
    sprintf_s(buffer, "LSB (Lower Side Band): Ширина полосы: %.1f Гц, Мощность: %.6f\n", bandwidth_lsb, power_lsb);
    WriteFile(hFile, buffer, strlen(buffer), &ByteNum, NULL);
    
    MessageBoxA(NULL, "Исследование модуляций завершено", "Modulation testing", MB_OK);
    
    // Освобождение ресурсов
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