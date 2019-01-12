import pandas as pd


def separate_channels_col(channels_col, types, col_name_prefix):
    """Separates column 'channels' into columns based on different values, 
    and then return the data frame containing the columns.

    Parameters
    ----------
    channels_col : pandas.Series
        The column containing the channels values.

    types : list
        The list containing channel types.
        
    col_name_prefix : str
        The prefix for the name of the new column.
    
    Returns
    -------
    df : pandas.Dataframe
        The data frame containing all new columns related to the channel.
    """
    types.sort()
    col_names = [col_name_prefix + "_" + t for t in types]

    df = pd.DataFrame()
    for i, t in enumerate(types):
        df[col_names[i]] = channels_col.apply(lambda x: 1 if t in x else 0)

    return df


def separate_col(col, col_name_prefix, columns=None):
    """Separates a column into columns based on different values, 
    and then return the data frame containing the columns.

    Parameters
    ----------
    col : pandas.Series
        The column containing data to be separated.

    col_name_prefix : str
        The prefix for the name of the new column.

    columns : list
        The list containing channel types.
    
    Returns
    -------
    df : pandas.Dataframe
        The data frame containing all new columns.
    """
    df = pd.get_dummies(
        col,
        prefix=col_name_prefix,
        prefix_sep='_',
        columns=columns,
        drop_first=False,
        dummy_na=False)

    return df


def separate_offer_type_col(offer_type_col):
    """Separates column 'offer_type' into columns based on different values, 
    and then return the data frame containing the columns.
    """
    return separate_col(offer_type_col, 'offer_type')


def separate_gender_col(gender_col):
    """Separates column 'gender' into columns based on different values, 
    and then return the data frame containing the columns.
    """
    return separate_col(gender_col, 'gender')


def separate_age_backet_col(age_backet_col):
    """Separates column 'age_backet' into columns based on different values, 
    and then return the data frame containing the columns.
    """
    return separate_col(age_backet_col, 'age')


def separate_income_backet_col(income_backet_col):
    """Separates column 'income_backet' into columns based on different values, 
    and then return the data frame containing the columns.
    """
    return separate_col(income_backet_col, 'income')


def separate_reg_year_col(reg_year_col):
    """Separates column 'reg_year' into columns based on different values, 
    and then return the data frame containing the columns.
    """
    df = separate_col(reg_year_col, 'reg_year')
    col_names = []
    # delete the ".0 " in the column names.
    for val in df.columns:
        if val.endswith(".0"):
            col_names.append(val[:-2])
        else:
            col_names.append(val)
    df.columns = col_names
    return df


def separate_reg_month_col(reg_month_col):
    """Separates column 'reg_month' into columns based on different values, 
    and then return the data frame containing the columns.
    """
    df = separate_col(reg_month_col, 'reg_month')
    col_names = []
    # delete the ".0 " in the column names.
    for val in df.columns:
        if val.endswith(".0"):
            col_names.append(val[:-2])
        else:
            col_names.append(val)
    df.columns = col_names
    return df


def separate_age_vals(age_col):
    """Separates the values in column 'age' according to fixed segments.

    Parameters
    ----------
    age_col : pandas.Series
        The column containing age data to be separated.
    
    Returns
    -------
    new_col : pandas.Series
        The new column containing the age values that have been discretized.
    """
    new_col = age_col.apply(lambda x: get_age_segment(x))
    return new_col


def get_age_segment(age):
    """Gets the segment to which the age value belongs.
   
    Parameters
    ----------
    age : int or float
        This value represents a specific age.
    
    Returns
    -------
    new_val : str
        The string representation of the segment at which given age value.
    """
    new_val = -1
    if age <= 20:
        new_val = '(0, 20]'
    elif age > 20 and age <= 30:
        new_val = '(20, 30]'
    elif age > 30 and age <= 40:
        new_val = '(30, 40]'
    elif age > 40 and age <= 50:
        new_val = '(40, 50]'
    elif age > 50 and age <= 60:
        new_val = '(50, 60]'
    elif age > 60 and age <= 70:
        new_val = '(60, 70]'
    elif age > 70 and age <= 80:
        new_val = '(70, 80]'
    elif age > 80 and age <= 90:
        new_val = '(80, 90]'
    elif age > 90 and age <= 100:
        new_val = '(90, 100]'
    else:
        new_val = '(100, 120]'

    return new_val


def separate_income_vals(income_col):
    """Separates the values in column 'income' according to fixed segments.

    Parameters
    ----------
    income_col : pandas.Series
        The column containing income data to be separated.
    
    Returns
    -------
    new_col : pandas.Series
        The new column containing the income values that have been discretized.
    """
    new_col = income_col.apply(lambda x: get_income_segment(x))
    return new_col


def get_income_segment(income):
    """Gets the segment to which the income value belongs.

    Parameters
    ----------
    income : int or float
        This value represents a specific income.
    
    Returns
    -------
    new_val : str
        The string representation of the segment at which given income value.
    """
    new_val = -1
    if income <= 30000:
        new_val = '(0, 30000]'
    elif income > 30000 and income <= 40000:
        new_val = '(30000, 40000]'
    elif income > 40000 and income <= 50000:
        new_val = '(40000, 50000]'
    elif income > 50000 and income <= 60000:
        new_val = '(50000, 60000]'
    elif income > 60000 and income <= 70000:
        new_val = '(60000, 70000]'
    elif income > 70000 and income <= 80000:
        new_val = '(70000, 80000]'
    elif income > 80000 and income <= 90000:
        new_val = '(80000, 90000]'
    elif income > 90000 and income <= 100000:
        new_val = '(90000, 100000]'
    elif income > 100000 and income <= 110000:
        new_val = '(100000, 110000]'
    else:
        new_val = '(110000, 120000]'

    return new_val