import pandas as pd
from collections import defaultdict

import generator as gen
import separater as sprt

import os
import constant
import time
import storer as sto


class AmountStorer:
    """AmountStorer is used to store the amounts that
    the customers spend at certain times.
    """

    def __init__(self):
        self.map = defaultdict(float)

    def gen_key(self, profile_id, time):
        return str(profile_id) + "-" + str(time)

    def set_amount(self, profile_id, time, amount):
        self.map[self.gen_key(profile_id, time)] += amount

    def get_amount(self, profile_id, time):
        return self.map[self.gen_key(profile_id, time)]


def check_validity(profile_id, group, expected_event_set, amountStorer):
    """ Check the validity (completeness) of events in the single group 
    (grouped by 'profile_id' and 'offer_id').
    
    Note that:
        1.  An event that is rewarded does not necessarily represent a valid response. 
        2.  For informational offer, we can't distinguish whether customer response, 
            because there is no any record about this kind of offer with 'offer completed' event 
            in the data frame called 'transcript'.
    """
    count = 0
    amount = 0.0
    reward = 0

    group = group.sort_values(by='time')
    event_set = set()

    for _, row in group.iterrows():
        event = row['event']
        event_set.add(event)

        if event == 'offer completed':
            if event_set == expected_event_set:
                count += 1
                amount += amountStorer.get_amount(profile_id, row['time'])
                reward += row['event_reward']

            event_set.clear()

    return (count, amount, reward)


def create_response(transcript_cleaned):
    """Creates a data frame about response based on the cleaned transcript.
    
    Parameters
    ----------
    transcript_cleaned : pandas.Dataframe
        The data frame containing the cleaned transcript data.

    Returns
    -------
    response : pandas.Dataframe
        The data frame containing response data.
    """
    transcript_grouped = transcript_cleaned.groupby(['profile_id', 'offer_id'])
    expected_event_set = {'offer received', 'offer viewed', 'offer completed'}
    responses = []

    amountStorer = AmountStorer()

    for name, group in transcript_grouped:
        profile_id, offer_id = name

        if offer_id == 0:  # 'event_type' == transaction
            # store the amount of each transaction for each customer
            for _, row in group.iterrows():
                amountStorer.set_amount(profile_id, row['time'],
                                        row['event_amount'])

            continue

        # The validation criterion for a valid response is to
        # receive, view, and complete an offer.

        count, amount, reward = check_validity(
            profile_id, group, expected_event_set, amountStorer)

        if count > 0:
            responses.append([1, profile_id, offer_id, count, amount, reward])
        else:
            responses.append([0, profile_id, offer_id, 0, 0.0, 0])

    response = pd.DataFrame(
        data=responses,
        columns=[
            'response', 'profile_id', 'offer_id', 'resp_number', 'resp_amount',
            'resp_reward'
        ])

    return response


def merge_response(response, portfolio_cleaned, profile_cleaned):
    """Merge the response data frame with cleaned portfolio and cleaned profile.
    
    Parameters
    ----------
    response : pandas.Dataframe
        The data frame containing the response data.

    portfolio_cleaned : pandas.Dataframe
        The data frame containing the cleaned offer data.

    profile_cleaned : pandas.Dataframe
        The data frame containing the cleaned profile data.

    Returns
    -------
    response_merged : pandas.Dataframe
        The data frame containing merged response data.
    """
    response_merged = pd.merge(
        response,
        portfolio_cleaned,
        on='offer_id',
        how='left',
        validate='many_to_one')

    response_merged = pd.merge(
        response_merged,
        profile_cleaned,
        on='profile_id',
        how='left',
        validate='many_to_one')

    # make sure some column types are correct
    response_merged[['reg_year']] = response_merged[['reg_year']].astype(int)
    response_merged[['reg_month']] = response_merged[['reg_month']].astype(int)

    return response_merged


def aggregate_merged_response(response_merged, profile_cleaned):
    """Aggregates the merged response.
    Create a data frame centered only on profile_id.

    Parameters
    ----------
    response_merged : pandas.Dataframe
        The data frame containing the merged response data.

    profile_cleaned : pandas.Dataframe
        The data frame containing the cleaned profile data.

    Returns
    -------
    response_agg : pandas.Dataframe
        The data frame containing aggregated response data.
    """
    response_groups = response_merged[
        response_merged['offer_type'] != 'informational'].groupby(
            by=['profile_id', 'offer_type'])

    response_agg = response_groups[['response']].sum().reset_index()

    # For the following features, I think we need to use their average.
    response_agg = response_agg.merge(
        response_groups[['resp_number']].mean().reset_index(),
        on=['profile_id', 'offer_type'])

    response_agg = response_agg.merge(
        response_groups[['resp_amount']].mean().reset_index(),
        on=['profile_id', 'offer_type'])

    response_agg = response_agg.merge(
        response_groups[['resp_reward']].mean().reset_index(),
        on=['profile_id', 'offer_type'])

    # For the following features, the average is better than the others.
    response_agg = response_agg.merge(
        response_groups[['difficulty']].mean().reset_index(),
        on=['profile_id', 'offer_type'])

    response_agg = response_agg.merge(
        response_groups[['duration']].mean().reset_index(),
        on=['profile_id', 'offer_type'])

    response_agg = response_agg.merge(
        response_groups[['reward']].mean().reset_index(),
        on=['profile_id', 'offer_type'])

    response_agg.columns = [
        'profile_id', 'offer_type', 'response_sum', 'resp_number_mean',
        'resp_amount_mean', 'resp_reward_mean', 'difficulty_mean',
        'duration_mean', 'reward_mean'
    ]

    # Combine the responses of each customer to the two types of offer.
    response_agg_bogo = response_agg[response_agg['offer_type'] ==
                                     'bogo'].drop(
                                         'offer_type', axis=1)

    response_agg_discount = response_agg[response_agg['offer_type'] ==
                                         'discount'].drop(
                                             'offer_type', axis=1)

    response_agg = response_agg_bogo.merge(
        response_agg_discount,
        on='profile_id',
        how='outer',
        suffixes=['_bogo', '_discount'],
        validate='one_to_one')

    # Merge the data in the profile as well.
    response_agg = response_agg.merge(
        profile_cleaned, on='profile_id', how='left', validate='one_to_one')

    # Fill null values.
    response_agg = response_agg.fillna(0.0)

    return response_agg


def main(input_dir, output_dir):
    """The main function.
    """
    print('Combine the cleaned data...')
    portfolio_cleaned_path = os.path.join(input_dir,
                                          constant.PICKLE_PORTFOLIO_CLEANED)
    profile_cleaned_path = os.path.join(input_dir,
                                        constant.PICKLE_PROFILE_CLEANED)
    transcript_cleaned_path = os.path.join(input_dir,
                                           constant.PICKLE_TRANSCRIPT_CLEANED)
    print('Load cleaned data...')
    portfolio_cleaned = sto.load(portfolio_cleaned_path)
    profile_cleaned = sto.load(profile_cleaned_path)
    transcript_cleaned = sto.load(transcript_cleaned_path)

    print(
        'Create the data frame about the response based on cleaned transcript... (waiting for a minute)'
    )
    start_time = time.time()
    response = create_response(transcript_cleaned)
    end_time = time.time()
    print('The time spent creating the data frame: {}s'.\
      format(end_time - start_time))

    print('Merge the response data with cleaned portfolio and profile...')
    response_merged = merge_response(response, portfolio_cleaned,
                                     profile_cleaned)

    print('Exclude the records related to informational offer...')
    response_merged = response_merged[
        response_merged['offer_type'] != 'informational']

    print('Aggregates the merged response...')
    response_agg = aggregate_merged_response(response_merged, profile_cleaned)

    print('Store data...')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    response_agg_path = get_output_file_path(output_dir)

    sto.store(response_agg, response_agg_path)

    print('Done.\n')


def check(output_dir):
    """Checks the validity for the pickle files.
    """
    print('Check the validity for the pickle files...')
    response_agg_path = get_output_file_path(output_dir)

    print('Check the output file located at {}...'.format(response_agg_path))
    response_agg = sto.load(response_agg_path)
    print('response_agg.shape: {}'.format(response_agg.shape))
    assert response_agg.shape == (
        16928, 22), "The shape of aggregated response is incorrect!"

    print('OK\n')


def get_output_file_path(output_dir):
    """Returns the full path of output files.
    """
    response_agg_path = os.path.join(output_dir, constant.PICKLE_RESPONSE_AGG)

    return response_agg_path


if __name__ == "__main__":
    main(constant.PROCESSED_DATA_DIR, constant.PROCESSED_DATA_DIR)
    check(constant.PROCESSED_DATA_DIR)