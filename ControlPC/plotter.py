import time
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.colorbar as cbar
import open3d as o3d

def normalize(data):
    min_val = np.min(data)
    max_val = np.max(data)
    return (data - min_val) / (max_val - min_val)


def plot_3d_antenna(csv_path, title):
    data = pd.read_csv(csv_path)
    pitch = np.deg2rad(np.array(data['Pitch'].values))
    azimuth = np.deg2rad(np.array(data['Azimuth'].values))
    
    rssi = np.array(data['RSSI'].values)
    rssi = normalize(rssi)
    

    # Convert spherical to Cartesian coordinates
    x = rssi * np.sin(pitch) * np.cos(azimuth)
    y = rssi * np.sin(pitch) * np.sin(azimuth)
    z = rssi * np.cos(pitch)

    # Plot the 3D radiation pattern
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=rssi, cmap='jet', s=100, marker='o')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'3D Radiation Pattern for {title}')

    plt.show()



def plot_heatmap_antenna(csv_path, title, colors=None, figsize=(20, 20)):
    # Default color scheme if none provided
    if colors is None:
        colors = ["purple", "blue", "cyan", "yellow", "orange", "red"]
    
    # Create a custom colormap
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_colormap", colors)
    
    # Read the CSV file
    data = pd.read_csv(csv_path)

    # Extract azimuth, pitch, and rssi
    pitch_data = np.array(data['Pitch'].values)
    unique_pitch_vals = len(np.unique(pitch_data))
    pitch_data = pitch_data[:unique_pitch_vals]
    azimuth_data = data['Azimuth'].values
    azimuth_data = [azimuth_data[idx] for idx in range(len(azimuth_data)) if idx % unique_pitch_vals == 0]
    rssi_data = np.array(data['RSSI'].values)
    print(len(pitch_data[::10]))
    #print(len(azimuth_data))
    #print(len(rssi_data))
    
    #x = input("Hey:")
    # Ensure that the reshaping works correctly
    heatmap_data = np.array(rssi_data).reshape((len(azimuth_data), len(pitch_data)))

    # Plot the heatmap
    plt.figure(figsize=figsize)
    ax = sns.heatmap(heatmap_data, xticklabels=pitch_data, yticklabels=azimuth_data, cmap="jet")
    # Set custom ticks
    ax.set_xticks(np.arange(len(pitch_data)))
    ax.set_xticklabels(pitch_data)

    ax.set_yticks(np.arange(0, len(azimuth_data), 5))
    ax.set_yticklabels(azimuth_data[::5])
    plt.xticks(rotation=0)
    # Invert y-axis
    ax.invert_yaxis()
    ax.set_ylabel('Azimuth', rotation=0, labelpad=30)
    plt.xlabel('Pitch')
   
    plt.title(f"RSSI heatmap for {title}")
    plt.show()


def plot_antenna_pattern(csv_path=None, title=None, pitch_angle = None):
    # Load data from CSV if a path is provided
    if csv_path:
        data = pd.read_csv(csv_path)
        pitch_data = np.array(data['Pitch'].values)
        filtered_values = data[data['Pitch'] == pitch_angle]['RSSI']
        unique_pitch_vals = len(np.unique(pitch_data))
        pitch_data = pitch_data[:unique_pitch_vals]
        azimuth_data = data['Azimuth'].values
        azimuth_data = [azimuth_data[idx] for idx in range(len(azimuth_data)) if idx % unique_pitch_vals == 0]
        # Assuming data has two columns: 'angle' (in degrees) and 'value'
        angles = np.deg2rad(azimuth_data)  # Convert angles to radians for polar plot
        rssi_data = np.array(data['RSSI'].values)
    else:
        # If no CSV path is provided, use dummy data
        angles = np.linspace(0, 2 * np.pi, 360)
        values = np.random.random(360)  # Random data for demonstration

    # Create a single polar plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, layout='constrained')

    # Plot data
    ax.plot(angles, filtered_values)
    
    # Set the title if provided
    if title:
        ax.set_title(title)
    
    plt.show()


if __name__ == "__main__":
    plot_heatmap_antenna("Results of analyzing.csv", "Freq 900e6 Hz")
    #plot_antenna_pattern("Results of analyzing.csv", "Freq 900e6 Hz", 0)