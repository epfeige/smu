import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt


def plot_histogram(df, column, show_histograms=True):
    # Plot histogram
    if show_histograms:
        fig, ax = plt.subplots()
        binwidth = 0.01
        bins = np.arange(df[column].min()-binwidth, df[column].max()+binwidth, binwidth)
        colors = np.where(df[column] < 0, 'darkorange', 'darkblue').reshape(-1, 1)
        ax.hist(df[column], bins=bins, color=colors[0])
        ax.hist(df[column], bins=bins, color=colors[1])
        ax.set_title(f"Histogram of {column}")
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")
        ax.axvline(x=0, color='black', lw=2) # Add vertical line at 0 to indicate separation of positive/negative values
        plt.savefig(f"{column}_histogram.png") # Saving the histogram as a png file with column name as filename
        plt.show()



def analyze_outliers(data_file, column, num_sections, show_histograms=True):
    # Load data into DataFrame
    df = pd.read_csv(data_file)

    plot_histogram(df, column)

    # Create output directory if it doesn't exist
    output_dir = os.path.splitext(data_file)[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # initialize an empty list to store the output strings
    output_strings = ["Analysis Results for " + output_dir + ".csv:\n\n"]

    # Split column into positive and negative values based on %_diff
    pos_df = df[df['%_diff'] >= 0]
    neg_df = df[df['%_diff'] < 0]
    dfs = {'positive': pos_df, 'negative': neg_df}

    # Store results for each DataFrame
    results = {}

    # Analyze each DataFrame
    for label, df in dfs.items():
        print(f"Results for {label} values of {column}:")

        # Count number of rows and outliers
        total_rows = len(df)
        num_outliers = len(df[df['%_diff'] > 0.005])

        # Calculate interquartile range and quartiles
        q1, q2, q3 = np.percentile(df[column], [25, 50, 75])
        iqr = q3 - q1
        q4 = df[column].max()
        mean = df[column].mean()
        std = df[column].std()

        # Calculate section size
        section_size = iqr / num_sections

        # Determine the range of each section
        ranges = []
        for i in range(num_sections):
            lower_bound = q1 + i * section_size
            upper_bound = lower_bound + section_size
            ranges.append((lower_bound, upper_bound))

        # Count number of values in each section
        counts = []
        for lower, upper in ranges:
            if math.isclose(upper, q3, rel_tol=1e-9):
                section_counts = len(df[(df[column] >= lower) & (df[column] <= upper)])
            else:
                section_counts = len(df[(df[column] >= lower) & (df[column] < upper)])
            counts.append(section_counts)

        # Calculate percentage of outliers
        percent_outliers = num_outliers / total_rows * 100

        output_strings.append("\nResults for " + label + " values of " + column + ":\n")

        # Print and save results
        for i, (lower, upper) in enumerate(ranges):
            if math.isclose(upper, q3, rel_tol=1e-9):
                section_str = f"{lower:.4f}, {upper:.4f}]"
            else:
                section_str = f"{lower:.4f}, {upper:.4f})"
            output_string = f"Q{i + 1}: {section_str} - ({lower * 100:.2f}% to {upper * 100:.1f}%) - {counts[i]}"
            output_strings.append(output_string)
            print(output_string)

        output_strings.append("Mean: " + str(round(mean, 2)) + "\n STD: " + str(round(std, 2)) + "\n")

        # extract the last 4 characters of the filename without extension using string slicing
        last_four_chars = output_dir[-4:]
        outfile = last_four_chars + "-report.txt"

        # write the output strings to a text file
        with open(f"{output_dir}/{outfile}", "w") as f:
            f.write("\n".join(output_strings))

        # print(f"Percentage of outliers: {percent_outliers:.1f}% ({num_outliers} of {total_rows})\n")

        # Save results
        results[label] = {
            'q1': q1,
            'q2': q2,
            'q3': q3,
            'q4': q4,
            'num_rows': total_rows,
            'num_outliers': num_outliers,
            'percent_outliers': percent_outliers,
            'ranges': ranges,
            'counts': counts,
            'mean': mean,
            'std': std
        }

    # Plot histogram
    # if show_histograms:
    #     df[column].hist(bins=30)
    #     plt.title(f"{label.capitalize()} values of {column}")
    #     plt.savefig(f"{output_dir}/{label}_histogram.png")  # Saving the histogram as a png file with label as filename
    #     plt.show()



    # Print message to indicate analysis is complete
    print(f"Analysis complete: Files are in {output_dir}")


