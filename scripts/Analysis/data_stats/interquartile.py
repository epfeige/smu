import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt


def analyze_outliers(data_file, column, num_sections, show_histograms=True):
    # Load data into DataFrame
    df = pd.read_csv(data_file)

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


        # Print results
        for i, (lower, upper) in enumerate(ranges):
            if math.isclose(upper, q3, rel_tol=1e-9):
                section_str = f"{lower:.4f}, {upper:.4f}]"
            else:
                section_str = f"{lower:.4f}, {upper:.4f})"
            print(f"Q{i + 1}: {section_str} - ({lower * 100:.2f}% to {upper * 100:.1f}%) - {counts[i]}")

        print(f"Percentage of outliers: {percent_outliers:.1f}% ({num_outliers} of {total_rows})\n")

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
        if show_histograms:
            df[column].hist(bins=30)
            plt.title(f"{label.capitalize()} values of {column}")
            plt.show()

    # Create output directory if it doesn't exist
    output_dir = os.path.splitext(data_file)[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    newline = os.linesep
    # Write results to text file
    with open(f"{output_dir}/analysis_results.txt", "w") as f:
        f.write(f"Analysis Results for {output_dir}.csv:{newline}{newline}")

        for label, result in results.items():
            f.write(f"Results for {label} values of %_diff:{newline}")
            f.write(
                f"Q1: ({result['ranges'][0]:.4f}, {result['ranges'][1]:.4f}) - ({result['percent_outliers']:.2f}% to {result['ranges'][2]:.1f}%) - {result['counts'][0]}{newline}")
            f.write(
                f"Q2: ({result['ranges'][1]:.4f}, {result['ranges'][2]:.4f}) - ({result['ranges'][2]:.2f}'%' to {result['ranges'][3]:.1f}'%') - {result['counts'][1]}{newline}")
            f.write(
                f"Q3: ({result['ranges'][2]:.4f}, {result['ranges'][3]:.4f}) - ({result['ranges'][3]:.2f}'%' to {result['ranges'][4]:.1f}'%') - {result['counts'][2]}{newline}")
            f.write(
                f"Q4: ({result['ranges'][3]:.4f}, {result['ranges'][4]:.4f}] - ({result['ranges'][4]:.2f}'%' to {result['percent_outliers']:.1f}'%') - {result['counts'][3]}{newline}")
            f.write(f"Mean: {result['mean']:.4f}{newline}")
            f.write(f"Standard deviation: {result['std']:.4f}{newline}{newline}")

    # Print message to indicate analysis is complete
    print(f"Analysis complete: Files are in {output_dir}")
