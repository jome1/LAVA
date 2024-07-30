

#Copernicus Global Land Service: Land Cover 100m: collection 3: epoch 2019: Globe 
#downloaded from zenodo: https://zenodo.org/records/3939050

#original url?: https://land.copernicus.eu/en/products/global-dynamic-land-cover/copernicus-global-land-service-land-cover-100m-collection-3-epoch-2018-globe
#product user manual with legends: https://land.copernicus.eu/en/technical-library/global-dynamic-land-cover-product-user-manual-v3.0/@@download/file

colors_dict_copernicus_global_coll3 = {
    0: (0.15686275, 0.15686275, 0.15686275),  # No input data available
    111: (0.34509804, 0.28235294, 0.12156863),  # Closed forest, evergreen needle leaf
    113: (0.43921569, 0.4, 0.24313725),  # Closed forest, deciduous needle leaf
    112: (0.0, 0.6, 0.0),  # Closed forest, evergreen, broad leaf
    114: (0.0, 0.8, 0.0),  # Closed forest, deciduous broad leaf
    115: (0.30588235, 0.45882353, 0.12156863),  # Closed forest, mixed
    116: (0.0, 0.47058824, 0.0),  # Closed forest, unknown
    121: (0.4, 0.37647059, 0.0),  # Open forest, evergreen needle leaf
    123: (0.55294118, 0.45490196, 0.0),  # Open forest, deciduous needle leaf
    122: (0.55294118, 0.70588235, 0.0),  # Open forest, evergreen broad leaf
    124: (0.62745098, 0.8627451, 0.0),  # Open forest, deciduous broad leaf
    125: (0.57254902, 0.6, 0.0),  # Open forest, mixed
    126: (0.39215686, 0.54901961, 0.0),  # Open forest, unknown
    20: (1.0, 0.73333333, 0.13333333),  # Shrubs
    30: (1.0, 1.0, 0.29803922),  # Herbaceous vegetation
    90: (0.0, 0.58823529, 0.62745098),  # Herbaceous wetland
    100: (0.98039216, 0.90196078, 0.62745098),  # Moss and lichen
    60: (0.70588235, 0.70588235, 0.70588235),  # Bare / sparse vegetation
    40: (0.94117647, 0.58823529, 1.0),  # Cultivated and managed vegetation/agriculture (cropland)
    50: (1.0, 0.0, 0.0),  # Urban / built up
    70: (0.94117647, 0.94117647, 0.94117647),  # Snow and Ice
    80: (0.0, 0.19607843, 0.78431373),  # Permanent water bodies
    200: (0.0, 0.0, 0.50196078)  # Open sea
}

legend_dict_copernicus_global_coll3 = {
    0: 'No input data available',
    111: 'Closed forest, evergreen needle leaf',
    113: 'Closed forest, deciduous needle leaf',
    112: 'Closed forest, evergreen, broad leaf',
    114: 'Closed forest, deciduous broad leaf',
    115: 'Closed forest, mixed',
    116: 'Closed forest, unknown',
    121: 'Open forest, evergreen needle leaf',
    123: 'Open forest, deciduous needle leaf',
    122: 'Open forest, evergreen broad leaf',
    124: 'Open forest, deciduous broad leaf',
    125: 'Open forest, mixed',
    126: 'Open forest, unknown',
    20: 'Shrubs',
    30: 'Herbaceous vegetation',
    90: 'Herbaceous wetland',
    100: 'Moss and lichen',
    60: 'Bare / sparse vegetation',
    40: 'Cultivated and managed vegetation/agriculture (cropland)',
    50: 'Urban / built up',
    70: 'Snow and Ice',
    80: 'Permanent water bodies',
    200: 'Open sea'
}



# CLC Europe 2012

colors_dict_Corine_Europe_2012 = {
    1: (0.9019607843137255, 0.0, 0.30196078431372547),
    2: (1.0, 0.0, 0.0),
    3: (0.8, 0.30196078431372547, 0.9490196078431372),
    4: (0.8, 0.0, 0.0),
    5: (0.9019607843137255, 0.8, 0.8),
    6: (0.9019607843137255, 0.8, 0.9019607843137255),
    7: (0.6509803921568628, 0.0, 0.8),
    8: (0.6509803921568628, 0.30196078431372547, 0.0),
    9: (1.0, 0.30196078431372547, 1.0),
    10: (1.0, 0.6509803921568628, 1.0),
    11: (1.0, 0.9019607843137255, 1.0),
    12: (1.0, 1.0, 0.6588235294117647),
    13: (1.0, 1.0, 0.0),
    14: (0.9019607843137255, 0.9019607843137255, 0.0),
    15: (0.9019607843137255, 0.5019607843137255, 0.0),
    16: (0.9490196078431372, 0.6509803921568628, 0.30196078431372547),
    17: (0.9019607843137255, 0.6509803921568628, 0.0),
    18: (0.9019607843137255, 0.9019607843137255, 0.30196078431372547),
    19: (1.0, 0.9019607843137255, 0.6509803921568628),
    20: (1.0, 0.9019607843137255, 0.30196078431372547),
    21: (0.9019607843137255, 0.8, 0.30196078431372547),
    22: (0.9490196078431372, 0.8, 0.6509803921568628),
    23: (0.5019607843137255, 1.0, 0.0),
    24: (0.0, 0.6509803921568628, 0.0),
    25: (0.30196078431372547, 1.0, 0.0),
    26: (0.8, 0.9490196078431372, 0.30196078431372547),
    27: (0.6509803921568628, 1.0, 0.5019607843137255),
    28: (0.6509803921568628, 0.9019607843137255, 0.30196078431372547),
    29: (0.6509803921568628, 0.9490196078431372, 0.0),
    30: (0.9019607843137255, 0.9019607843137255, 0.9019607843137255),
    31: (0.8, 0.8, 0.8),
    32: (0.8, 1.0, 0.8),
    33: (0.0, 0.0, 0.0),
    34: (0.6509803921568628, 0.9019607843137255, 0.8),
    35: (0.6509803921568628, 0.6509803921568628, 1.0),
    36: (0.30196078431372547, 0.30196078431372547, 1.0),
    37: (0.8, 0.8, 1.0),
    38: (0.9019607843137255, 0.9019607843137255, 1.0),
    39: (0.6509803921568628, 0.6509803921568628, 0.9019607843137255),
    40: (0.0, 0.8, 0.9490196078431372),
    41: (0.5019607843137255, 0.9490196078431372, 0.9019607843137255),
    42: (0.0, 1.0, 0.6509803921568628),
    43: (0.6509803921568628, 1.0, 0.9019607843137255),
    44: (0.9019607843137255, 0.9490196078431372, 1.0),
    -128: (1.0, 1.0, 1.0)
}

legend_dict_Corine_Europe_2012 ={
    1: "Continuous urban fabric",
    2: "Discontinuous urban fabric",
    3: "Industrial or commercial units",
    4: "Road and rail networks and associated land",
    5: "Port areas",
    6: "Airports",
    7: "Mineral extraction sites",
    8: "Dump sites",
    9: "Construction sites",
    10: "Green urban areas",
    11: "Sport and leisure facilities",
    12: "Non-irrigated arable land",
    13: "Permanently irrigated land",
    14: "Rice fields",
    15: "Vineyards",
    16: "Fruit trees and berry plantations",
    17: "Olive groves",
    18: "Pastures",
    19: "Annual crops associated with permanent crops",
    20: "Complex cultivation patterns",
    21: "Land principally occupied by agriculture with significant areas of natural vegetation",
    22: "Agro-forestry areas",
    23: "Broad-leaved forest",
    24: "Coniferous forest",
    25: "Mixed forest",
    26: "Natural grasslands",
    27: "Moors and heathland",
    28: "Sclerophyllous vegetation",
    29: "Transitional woodland-shrub",
    30: "Beaches - dunes - sands",
    31: "Bare rocks",
    32: "Sparsely vegetated areas",
    33: "Burnt areas",
    34: "Glaciers and perpetual snow",
    35: "Inland marshes",
    36: "Peat bogs",
    37: "Salt marshes",
    38: "Salines",
    39: "Intertidal flats",
    40: "Water courses",
    41: "Water bodies",
    42: "Coastal lagoons",
    43: "Estuaries",
    44: "Sea and ocean",
    -128: "NODATA"
}