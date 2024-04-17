import numpy as np
import pandas as pd
import math

#Constants
file_head_size_sl2 = 8
frame_head_size_sl2 = 144

file_head_size_sl3 = 8
frame_head_size_sl3 = 168

#NumPy custom dtypes
dtype_sl2 = np.dtype([
    ("first_byte", "<u4"),
    ("frame_size", "<u2"),
    ("survey_type", "<u2"),
    ("min_range", "<f4"),
    ("max_range", "<f4"),
    ("water_depth", "<f4"),
    ("x", "<i4"),
    ("y", "<i4"),
    ("heading", "<f4")
    ])

dtype_sl3 = np.dtype([
    ("first_byte", "<u4"),
    ("frame_size", "<u2"),
    ("survey_type", "<u2"),
    ("min_range", "<f4"),
    ("max_range", "<f4"),
    ("water_depth", "<f4"),
    ("x", "<i4"),
    ("y", "<i4"),
    ("heading", "<f4")
    ])

#Helper functions to convert units etc.
survey_dict = {0: 'primary', 1: 'secondary', 2: 'downscan', 3: 'left_sidescan', 4: 'right_sidescan', 5: 'sidescan'}

def x2lon(x):
    return(x/6356752.3142*(180/math.pi))

def y2lat(y):
    return(((2*np.arctan(np.exp(y/6356752.3142)))-(math.pi/2))*(180/math.pi))

#Funtion for reading binary data into memory
def read_bin(path):

    with open(path, "rb") as f:
        data = f.read()
        
    return(data)


#Function for parsing binary data in '.sl2' format
def sl2_decode(data):
    
    position = file_head_size_sl2
    headers = []

    # Cut binary blob
    while (position < len(data)):
        head = data[position:(position+frame_head_size_sl2)]
        frame_size = int.from_bytes(head[28:30], "little", signed = False)
        head_sub = head[0:4]+head[28:30]+head[32:34]+head[40:48]+head[64:68]+head[108:116]+head[124:128]    
        headers.append(head_sub)
        position += frame_size
    
    # Parse binary blob using NumPy custom dtype
    frame_head_np = np.frombuffer(b''.join(headers), dtype=dtype_sl2)

    # Convert to pandas dataframe
    frame_head_df = pd.DataFrame(frame_head_np)
    
    # Convert x-y coordinates to lat/long 
    frame_head_df["longitude"] = x2lon(frame_head_df["x"])
    frame_head_df["latitude"] = y2lat(frame_head_df["y"])

    # Get survey type label
    frame_head_df["survey_label"] = [survey_dict.get(i, "Other") for i in frame_head_df["survey_type"]]

    # Convert feet to meters
    frame_head_df[["water_depth", "min_range", "max_range"]] /= 3.2808399
    
    return frame_head_df



def read_sl(path):
    print("reading sl file")
    format = path.split(".")[-1]

    if format == "sl2":
        print("reading sl2")
        data = read_bin(path)
        df = sl2_decode(data)

    elif format == "sl3":
        print("reading sl3")
        data = read_bin(path)
        df = sl3_decode(data)

    else:
        print("Only '.sl2' or '.sl3' file formats supported")
        return(-1)

    return(df)

#Function for parsing binary data in '.sl3' format
def sl3_decode(data):
    position = file_head_size_sl3
    headers = []

    #Cut binary blob
    while (position < len(data)):
        head = data[position:(position+frame_head_size_sl3)]
        frame_size = int.from_bytes(head[8:10], "little", signed = False)
        head_sub = head[0:4]+head[8:10]+head[12:14]+head[20:28]+head[48:52]+head[92:100]+head[104:108]    
        headers.append(head_sub)
        position += frame_size
    
    #Parse binary blob using NumPy custom dtype
    frame_head_np = np.frombuffer(b''.join(headers), dtype=dtype_sl3)

    #Convert to pandas dataframe
    frame_head_df = pd.DataFrame(frame_head_np)
    
    #Convert x-y coordinates to lat/long 
    frame_head_df["longitude"] = x2lon(frame_head_df["x"])
    frame_head_df["latitude"] = y2lat(frame_head_df["y"])

    #Get survey type label
    frame_head_df["survey_label"] = [survey_dict.get(i, "Other") for i in frame_head_df["survey_type"]]

    #Convert feet to meters
    frame_head_df[["water_depth", "min_range", "max_range"]] /= 3.2808399
    
    return(frame_head_df)

