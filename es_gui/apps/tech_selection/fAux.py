def pdSeriesIdxWhereTrue(pdSeries):
    """
    Return the indexes of a pandas series for which the corresponding values are True (boolean).

    Parameters
    ----------
    pdSeries: pandas series
        Input pandas series of the type Boolean

    Returns
    -------
    List
        Indexes of the pandas series that correspond to True values
    """
    
    return pdSeries.index[pdSeries].tolist()