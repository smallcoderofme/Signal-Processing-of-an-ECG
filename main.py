"""
    main.py
    The main module for ENEL420-20S2 Assignment 1.
    This module imports ECG data from a .txt and
    creates IIR and FIR notch filters to reduce
    narrowband noise from the data. Figures of
    the data, filtered data and filter responses
    are produced. The noise power is calculated.
    All results are saved in the current directory.

    Authors: Matt Blake   (58979250)
             Reweti Davis (23200856)
    Group Number: 18
    Last Modified: 14/08/2020
"""

# Imported libraries
from scipy.signal import freqz, lfilter, firwin, remez, firwin2, convolve, kaiserord
from scipy.fft import fft
import numpy as np
from signalPlots import *
from IIR import *
from FIR import *
from noise import *
from configFiles import *



def main():
    """Main function of ENEL420 Assignment 1"""

    # Define filenames
    filename = 'enel420_grp_18.txt' # Location in project where ECG data is stored
    figures_filename = 'Group_18_Figures' # Folder to save created figure images to
    noise_power_output_filename = 'Group_18_Noise_Power_(Variance)_Data_from_Created_Filters.txt' # File to save calculated noise power data
    figure_names = ['ECG_Time_Plot.png', 'ECG_Freq_Plot.png', 'IIR_Pole_Zero_Plot.png', 'IIR_Notched_ECG_Time_Plot.png',
                    'IIR_Notched_Freq_Plot.png', 'IIR_Frequency_Response.png', 'Windowed_ECG_Time_Plot.png',
                    'Windowed_Freq_Plot.png', 'Windowed_Frequency_Response.png', 'Optimal_ECG_Time_Plot.png',
                    'Optimal_Freq_Plot.png', 'Optimal_Frequency_Response.png', 'Freq_Sampled_ECG_Time_Plot.png',
                    'Freq_Sampled_Freq_Plot.png', 'Freq_Sampled_Frequency_Response.png']  # The names that each figure should be saved as

    # Define filter and data parameters
    sample_rate = 1024  # Sample rate of data (Hz)
    cutoff = [57.755, 88.824] # Frequencies to attenuate (Hz), which were calculated based on previous graphical analysis
    passband_f = [10, 10] # Passband frequencies (Hz) used to calculate the gain factor
    notch_width = 5 # 3 dB bandwidth of the notch filters (Hz)
    num_FIR_taps = 399 # The number for each FIR filter

    # Gather data from input files
    samples = importData(filename) # Import data from file
    base_time = getTimeData(sample_rate, len(samples)) # Create a time array based on imported data
    base_freq, base_freq_data = calcFreqSpectrum(samples, sample_rate) # Calculate the frequency spectrum of the data

    # Create IIR Notch filters and use them to filter the ECG data
    notch_num_1, notch_denom_1 = createIIRNotchFilter(cutoff[0], notch_width, passband_f[0], sample_rate) # Calculate the first notch filter's coefficents
    notch_num_2, notch_denom_2 = createIIRNotchFilter(cutoff[1], notch_width, passband_f[1], sample_rate) # Calculate the second notch filter's coefficents
    half_notched_samples, notched_samples = applyIIRNotchFilters(notch_num_1, notch_denom_1, notch_num_2, notch_denom_2, samples) # Apply cascaded notch filters to data
    notch_time = getTimeData(sample_rate, len(notched_samples)) # Create a time array based on notch filtered data
    notch_frequency, notch_freq_data = calcFreqSpectrum(notched_samples, sample_rate) # Calculate frequency of the IIR filtered ECG data
    notched_numerator, notched_denominator = combineFilters(notch_num_1, notch_denom_1, notch_num_2, notch_denom_2)  # Combine the two IIR notch filters

    # Create and apply FIR filters to data
    window_filter_1, window_filter_2, window_filter_overall = createWindowFilters(cutoff, sample_rate, notch_width, num_FIR_taps) # Calculate window filter coefficents
    half_windowed_samples, full_windowed_samples, overall_windowed_samples = applyFIRFilters(window_filter_1, window_filter_2, window_filter_overall, samples) # Apply window filter to data
    win_time = getTimeData(sample_rate, len(full_windowed_samples)) # Create a time array based on window filtered data
    win_frequency, win_freq_data = calcFreqSpectrum(overall_windowed_samples, sample_rate) # Calculate frequency of the window IIR filtered ECG data

    optimal_filter_1, optimal_filter_2, optimal_filter_overall = createOptimalFilters(cutoff, sample_rate, notch_width, num_FIR_taps)
    half_optimal_samples, full_optimal_samples, overall_optimal_samples = applyFIRFilters(optimal_filter_1, optimal_filter_2, optimal_filter_overall, samples)
    opt_time = getTimeData(sample_rate, len(full_optimal_samples)) # Create a time array based on optimal filtered data
    opt_frequency, opt_freq_data = calcFreqSpectrum(overall_optimal_samples, sample_rate) # Calculate frequency of the window IIR filtered ECG data
    
    freq_sampling_filter_1, freq_sampling_filter_2, freq_filter_overall  = createFreqSamplingFilters(cutoff, sample_rate, notch_width, num_FIR_taps)
    half_freq_samples, full_freq_samples, overall_freq_samples = applyFIRFilters(freq_sampling_filter_1, freq_sampling_filter_2, freq_filter_overall, samples)
    freq_sampling_time = getTimeData(sample_rate, len(full_freq_samples)) # Create a time array based on optimal filtered data
    freq_s_frequency, freq_s_freq_data = calcFreqSpectrum(overall_freq_samples, sample_rate) # Calculate frequency of the window IIR filtered ECG data

    # Plot unfiltered data
    ECG = plotECG(samples, base_time) # Plot a time domain graph of the ECG data
    ECGSpectrum = plotECGSpectrum(base_freq, base_freq_data) # Plot the frequency spectrum of the ECG data

    # Plot IIR notch filtered data
    IIRPoleZero = plotIIRPoleZero(cutoff, notch_width, sample_rate) # Plot a pole-zero plot of the created IIR notch filter
    IIRNotchECG = plotIIRNotchECG(notched_samples, notch_time) # Plot a time domain graph of the IIR notch filtered ECG data
    IIRNotchECGSpectrum = plotIIRNotchECGSpectrum(notch_frequency, notch_freq_data) # Plot the frequency spectrum of the IIR notch filtered ECG data
    IIRNotchFilterResponse = plotIIRNotchFilterResponse(notched_numerator, notched_denominator, sample_rate) # Plot the frequency response of the notch filter

    # Plot window filtered data
    WindowedECG = plotWindowedECG(overall_windowed_samples, win_time) # Plot a time domain graph of the window filtered ECG data
    WindowedECGSpectrum = plotWindowedECGSpectrum(win_frequency, win_freq_data) # Plot the frequency spectrum of the window filtered ECG data
    WindowFilterResponse = plotWindowFilterResponse(window_filter_overall, sample_rate) # Plot the frequency response of the window filter

    #Plot optimal filtered data
    OptimalECG = plotOptimalECG(overall_optimal_samples, opt_time) # Plot a time domain graph of the optimal filtered ECG data
    OptimalECGSpectrum = plotOptimalECGSpectrum(opt_frequency, opt_freq_data) # Plot the frequency spectrum of the optimal filtered ECG data
    OptimalFilterResponse = plotOptimalFilterResponse(optimal_filter_overall, sample_rate) # Plot the frequency response of the optimal filter

    #Plot Frequency Sampling filtered data
    FrequencySamplingECG = plotFrequencySampledECG(overall_freq_samples, freq_sampling_time) # Plot a time domain graph of the frequency sampling filtered ECG data
    FrequencySamplingECGSpectrum = plotFrequencySampledECGSpectrum(freq_s_frequency, freq_s_freq_data) # Plot the frequency spectrum of the frequency sampling filtered ECG data
    FrequencySamplingFilterResponse = plotFrequencySampledFilterResponse(freq_filter_overall, sample_rate) # Plot the frequency response of the frequency sampling filter

    # Save figures
    figures = [ECG, ECGSpectrum, IIRPoleZero, IIRNotchECG, IIRNotchECGSpectrum, IIRNotchFilterResponse, WindowedECG,
               WindowedECGSpectrum, WindowFilterResponse, OptimalECG, OptimalECGSpectrum, OptimalFilterResponse,
               FrequencySamplingECG, FrequencySamplingECGSpectrum, FrequencySamplingFilterResponse] # The figures to save, which must be in the same order as figure_names
    saveFigures(figures, figures_filename, figure_names) # Save the figures to an output folder in the current directory

    # Calculate the variance of IIR filtered data
    notched_noise_variance = calculateNoiseVariance(samples, notched_samples)  # Calculate the variance of the noise removed by the IIR notch filters
    first_notched_noise_variance = calculateNoiseVariance(samples, half_notched_samples)  # Calculate the variance of the noise removed by the first IIR notch filter
    second_notched_noise_variance = calculateNoiseVariance(half_notched_samples, notched_samples)  # Calculate the variance of the noise removed by the second IIR notch filter

    # Calculate the variance of window filtered data
    window_noise_variance = calculateNoiseVariance(samples, overall_windowed_samples)  # Calculate the variance of the noise removed by the 
    first_window_noise_variance = calculateNoiseVariance(samples, half_windowed_samples)  # Calculate the variance of the noise removed by the 
    second_window_noise_variance = calculateNoiseVariance(half_windowed_samples, full_windowed_samples)  # Calculate the variance of the noise removed by the 

    # Calculate the variance of optimal filtered data
    optimal_noise_variance = calculateNoiseVariance(samples, overall_optimal_samples)  # Calculate the variance of the noise removed by the 
    first_optimal_noise_variance = calculateNoiseVariance(samples, half_optimal_samples)  # Calculate the variance of the noise removed by the 
    second_optimal_noise_variance = calculateNoiseVariance(half_optimal_samples, full_optimal_samples)  # Calculate the variance of the noise removed by the 

    # Calculate the variance of frequency sampling filtered data
    freq_sampling_noise_variance = calculateNoiseVariance(samples, overall_freq_samples)  # Calculate the variance of the noise removed by the 
    first_freq_sampling_noise_variance = calculateNoiseVariance(samples, half_freq_samples)  # Calculate the variance of the noise removed by the 
    second_freq_sampling_noise_variance = calculateNoiseVariance(half_freq_samples, full_freq_samples)  # Calculate the variance of the noise removed by the

    # Save noise power to a .txt file
    noise_power_data = {'IIR notch filters': notched_noise_variance,
                        'first IIR notch filter': first_notched_noise_variance,
                        'second IIR notch filter': second_notched_noise_variance,
                        'FIR Window filters': window_noise_variance,
                        'first window filter': first_window_noise_variance,
                        'second window filter': second_window_noise_variance,
                        'FIR Optimal filters': optimal_noise_variance,
                        'first optimal filter': first_optimal_noise_variance,
                        'second optimal filter': second_optimal_noise_variance,
                        'FIR Frequency Sampling filters': freq_sampling_noise_variance,
                        'first frequency sampling filter': first_freq_sampling_noise_variance,
                        'second frequency sampling filter': second_freq_sampling_noise_variance
                        }  # Create a dictionary of the filter name and its noise power
    saveNoisePowerData(noise_power_data, noise_power_output_filename)  # Save the data about each filter to a file



# Run program if called
if __name__ == '__main__':
    main()
