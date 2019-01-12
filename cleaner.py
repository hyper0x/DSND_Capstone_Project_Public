import pandas as pd
import numpy as np
import separater as sprt

import os
import constant
import generator as gen
import storer as sto


def clean_portfolio_df(original_df, offer_id_map):
    """Cleans the data frame of portfolio.

    Parameters
    ----------
    original_df : pandas.Dataframe
        The data frame containing the offer data.

    offer_id_map : collections.defaultdict
        The dictionary containing all mappings from the old offer ID to the new offer ID.
    
    Returns
    -------
    portfolio_cleaned : pandas.Dataframe
        The data frame containing cleaned offer data.
    """
    portfolio_cleaned = original_df.copy()

    # clean channels
    channel_types = ['email', 'mobile', 'social', 'web']

    channel_df = sprt.separate_channels_col(portfolio_cleaned['channels'],
                                            channel_types, 'channel')

    portfolio_cleaned = portfolio_cleaned.join(channel_df)

    # simplify the ID of offer
    portfolio_cleaned['offer_id'] = portfolio_cleaned['id'].apply(
        lambda x: offer_id_map[x])

    # drop the useless columns
    useless_columns = ['channels', 'id']

    for name in useless_columns:
        if name not in portfolio_cleaned.columns:
            continue

    portfolio_cleaned = portfolio_cleaned.drop(name, axis=1)

    # rearrange all the columns
    portfolio_cleaned = portfolio_cleaned[[
        'offer_id', 'offer_type', 'difficulty', 'duration', 'reward',
        'channel_email', 'channel_mobile', 'channel_social', 'channel_web'
    ]]

    return portfolio_cleaned


def clean_profile_df(original_df, profile_id_map, discretize,
                     drop_missing_rows):
    """Cleans the data frame of profile.
    
    Parameters
    ----------
    original_df : pandas.Dataframe
        The data frame containing the profile data.

    profile_id_map : collections.defaultdict
        The dictionary containing all mappings from the old profile ID to the new profile ID.

    discretize : bool
        Whether to discretize age and income into multiple buckets.

    drop_missing_rows : bool
        Whether to delete rows containing missing values directly.
    
    Returns
    -------
    profile_cleaned : pandas.Dataframe
        The data frame containing cleaned profile data.
    """
    profile_cleaned = original_df.copy()

    # simplify the ID of profile
    profile_cleaned['profile_id'] = profile_cleaned['id'].apply(
        lambda x: profile_id_map[x])

    if drop_missing_rows:
        # drop missing rows
        profile_cleaned = profile_cleaned[
            (profile_cleaned['age'] != 118)
            & (profile_cleaned['gender'].notnull()) &
            (profile_cleaned['income'].notnull())]
    else:
        # handle missing values
        profile_cleaned['age'] = profile_cleaned['age'].apply(
            lambda x: np.nan if x == 118 else x)
        profile_cleaned['age'] = profile_cleaned['age'].fillna(method='bfill')
        profile_cleaned['gender'] = profile_cleaned['gender'].fillna('U')
        profile_cleaned['income'] = profile_cleaned['income'].fillna(
            method='bfill')

    # split became_member_on
    profile_cleaned['reg_year'] = \
        profile_cleaned['became_member_on'].apply(lambda x: int((str(x))[0:4]))

    profile_cleaned['reg_month'] = \
        profile_cleaned['became_member_on'].apply(lambda x: int((str(x))[4:6]))

    if discretize:
        # append age_backet
        age_backet_df = pd.DataFrame()

        age_backet_df['age_backet'] = sprt.separate_age_vals(
            profile_cleaned['age'])

        profile_cleaned = pd.concat([profile_cleaned, age_backet_df], axis=1)

        # append income_backet
        income_backet_df = pd.DataFrame()

        income_backet_df['income_backet'] = sprt.separate_income_vals(
            profile_cleaned['income'])

        profile_cleaned = pd.concat([profile_cleaned, income_backet_df],
                                    axis=1)

    # drop the useless columns
    useless_columns = ['became_member_on', 'id']

    for name in useless_columns:
        if name not in profile_cleaned.columns:
            continue
        profile_cleaned = profile_cleaned.drop(name, axis=1)

    # rearrange all the columns
    col_names = []
    if discretize:
        col_names = [
            'profile_id', 'gender', 'age', 'age_backet', 'income',
            'income_backet', 'reg_year', 'reg_month'
        ]
    else:
        col_names = [
            'profile_id', 'gender', 'age', 'income', 'reg_year', 'reg_month'
        ]

    profile_cleaned = profile_cleaned[col_names]

    return profile_cleaned


def clean_transcript_df(original_df, offer_id_map, profile_id_map):
    """Cleans the data frame of transcript.

    Parameters
    ----------
    original_df : pandas.Dataframe
        The data frame containing the profile data.

    offer_id_map : collections.defaultdict
        The dictionary containing all mappings from the old offer ID to the new offer ID.

    profile_id_map : collections.defaultdict
        The dictionary containing all mappings from the old profile ID to the new profile ID.
    
    Returns
    -------
    transcript_cleaned : pandas.Dataframe
        The data frame containing cleaned transcript data.
    """
    transcript_cleaned = original_df.copy()

    # generate event ID
    transcript_cleaned['event_id'] = range(1, transcript_cleaned.shape[0] + 1)

    # replace and store the ID of profile(person)
    transcript_cleaned['profile_id'] = transcript_cleaned['person'].apply(
        lambda x: profile_id_map[x])

    # extract the ID of offer from value
    def extract_offer_id_from_value(value):
        keys = value.keys()
        if 'offer_id' in keys:
            return value['offer_id']
        elif 'offer id' in keys:
            return value['offer id']
        else:
            return '0'

    transcript_cleaned['offer_id_str'] = transcript_cleaned['value'].apply(
        lambda x: extract_offer_id_from_value(x))

    # replace and store the ID of offer
    transcript_cleaned['offer_id'] = transcript_cleaned['offer_id_str'].apply(
        lambda x: offer_id_map[x] if x != '0' else 0)

    # extract the amount from value
    transcript_cleaned['event_amount'] = transcript_cleaned['value'].apply(
        lambda x: x['amount'] if 'amount' in x.keys() else 0)

    # extract the reward from value
    transcript_cleaned['event_reward'] = transcript_cleaned['value'].apply(
        lambda x: x['reward'] if 'reward' in x.keys() else 0)

    # drop the useless columns
    useless_columns = ['person', 'value', 'offer_id_str']

    for name in useless_columns:
        if name not in transcript_cleaned.columns:
            continue
        transcript_cleaned = transcript_cleaned.drop(name, axis=1)

    # rearrange all the columns
    transcript_cleaned = transcript_cleaned[[
        'event_id', 'event', 'event_amount', 'event_reward', 'time',
        'profile_id', 'offer_id'
    ]]

    return transcript_cleaned


def main(input_dir, output_dir):
    """The main function.
    """
    print('Clean up the original data...')
    portfolio_path = os.path.join(input_dir, constant.JSON_PORTFOLIO)
    profile_path = os.path.join(input_dir, constant.JSON_PROFILE)
    transcript_path = os.path.join(input_dir, constant.JSON_TRANSCRIPT)

    print('Load original data...')
    portfolio = pd.read_json(portfolio_path, orient='records', lines=True)
    profile = pd.read_json(profile_path, orient='records', lines=True)
    transcript = pd.read_json(transcript_path, orient='records', lines=True)

    print('Generate map for offer ID...')
    offer_id_map = gen.gen_id_map(portfolio['id'])

    print('Clean up data about portfolio (offer)...')
    portfolio_cleaned = clean_portfolio_df(portfolio, offer_id_map)

    print('Generate map for customer ID...')
    profile_id_map = gen.gen_id_map(profile['id'])

    print('Clean up data about profile (customer)...')
    profile_cleaned = clean_profile_df(profile, profile_id_map, True, False)

    print('Clean up data about transcript (event record)...')
    transcript_cleaned = clean_transcript_df(transcript, offer_id_map,
                                             profile_id_map)

    print('Store data...')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    portfolio_cleaned_path, profile_cleaned_path, transcript_cleaned_path = get_output_file_paths(
        output_dir)

    sto.store(portfolio_cleaned, portfolio_cleaned_path)
    sto.store(profile_cleaned, profile_cleaned_path)
    sto.store(transcript_cleaned, transcript_cleaned_path)

    print('Done.\n')


def check(output_dir):
    """Checks the validity for the pickle files.
    """
    print('Check the validity for the pickle files...')
    portfolio_cleaned_path, profile_cleaned_path, transcript_cleaned_path = get_output_file_paths(
        output_dir)

    print('Check the output file located at {}...'.format(
        portfolio_cleaned_path))
    portfolio_cleaned = sto.load(portfolio_cleaned_path)
    print('portfolio_cleaned.shape: {}'.format(portfolio_cleaned.shape))
    assert portfolio_cleaned.shape == (
        10, 9), "The shape of cleaned portfolio is incorrect!"

    print(
        'Check the output file located at {}...'.format(profile_cleaned_path))
    profile_cleaned = sto.load(profile_cleaned_path)
    print('profile_cleaned.shape: {}'.format(profile_cleaned.shape))
    assert profile_cleaned.shape == (
        17000, 8), "The shape of cleaned profile is incorrect!"

    print('Check the output file located at {}...'.format(
        transcript_cleaned_path))
    transcript_cleaned = sto.load(transcript_cleaned_path)
    print('transcript_cleaned.shape: {}'.format(transcript_cleaned.shape))
    assert transcript_cleaned.shape == (
        306534, 7), "The shape of cleaned transcript is incorrect!"

    print('OK\n')


def get_output_file_paths(output_dir):
    """Returns the full path of output files.
    """
    portfolio_cleaned_path = os.path.join(output_dir,
                                          constant.PICKLE_PORTFOLIO_CLEANED)
    profile_cleaned_path = os.path.join(output_dir,
                                        constant.PICKLE_PROFILE_CLEANED)
    transcript_cleaned_path = os.path.join(output_dir,
                                           constant.PICKLE_TRANSCRIPT_CLEANED)

    return (portfolio_cleaned_path, profile_cleaned_path,
            transcript_cleaned_path)


if __name__ == '__main__':
    main(constant.DATA_DIR, constant.PROCESSED_DATA_DIR)
    check(constant.PROCESSED_DATA_DIR)
