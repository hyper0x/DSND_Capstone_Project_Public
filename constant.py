class Const:
    """ Const will be the constant type in this file.
    """

    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError('Can not rebind constant {}!'.format(name))

        if not name.isupper():
            raise self.ConstCaseError(
                'Constant {} is not all letters are capitalized!'.format(name))

        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError('Can not unbind constant {}!'.format(name))


import sys
sys.modules[__name__] = Const()

import constant

constant.DATA_DIR = 'data'  # store the original data file
constant.PROCESSED_DATA_DIR = 'processed_data'  # store files containing processed data
constant.MODEL_DIR = 'model'  # store the trained model files

constant.JSON_PORTFOLIO = 'portfolio.json'
constant.JSON_PROFILE = 'profile.json'
constant.JSON_TRANSCRIPT = 'transcript.json'

constant.PICKLE_PORTFOLIO_CLEANED = 'portfolio_cleaned.pkl'
constant.PICKLE_PROFILE_CLEANED = 'profile_cleaned.pkl'
constant.PICKLE_TRANSCRIPT_CLEANED = 'transcript_cleaned.pkl'

constant.PICKLE_RESPONSE_AGG = 'response_agg.pkl'

constant.PICKLE_CLUSTERING_MODEL = 'clustering_model.pkl'
constant.PICKLE_RESPONSE_LABELED = 'response_labeled.pkl'
