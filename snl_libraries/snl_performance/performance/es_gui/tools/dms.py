from __future__ import print_function, absolute_import

from collections import OrderedDict
import pickle
import logging
import os

import numpy as np


class DataManagementSystem():
    """
    A class used to store processed DataFrames as NumPy ndarrays and manage memory consumed. Data is stored in nested dictionaries up to a depth of 2: {key_0: {key_0_0: data}}. When the calculated memory exceeds max_memory, the dictionary at depth 1 at the front of the queue is popped out of the dictionary until the memory consumption is less than the maximum. The queue is determined by time of accessing. Accessing or adding to the structure at any depth will push the depth 1 dictionary to the back of the queue.

    :param save_name: The path/filename to pickle the DMS's data.
    :param max_memory: The maximum amount of memory, in bytes, that the contained ndarrays may collectively occupy.
    """
    def __init__(self, save_name, save_data=False, max_memory=500000):
        self.memory_used = 0
        self.max_memory = max_memory
        self.save_data = save_data
        self.save_name = save_name

        try:
            with open(self.save_name, 'rb') as pfile:
                self.data = pickle.load(pfile)
                logging.info('DMS: Successfully loaded {fname}.'.format(fname=self.save_name))
        except FileNotFoundError:
            self.data = OrderedDict()
        except pickle.PickleError:
            logging.error('DMS: Could not unpickle data; purging and restarting DMS.')
            self.delete_pickle()
            self.data = OrderedDict()
    
    def delete_pickle(self):
        """Deletes the pickle file used for self.data object persistence."""
        os.remove(self.save_data)

    def save_state(self):
        """Pickles self.data at self.save_name."""
        if self.save_data:
            logging.info('DMS: Saving {0}.'.format(self.save_name))
            with open(self.save_name, 'wb') as pfile:
                pickle.dump(self.data, pfile, protocol=3)

    def pop(self):
        """Shortcut for popping the queue of the OrderedDict."""
        k, v = self.data.popitem(last=False)
        print('Popped: ', (k))

    def requeue(self, key):
        """Moves self.data[key] to the back of the queue for being purged."""

        if key in self.data:
            to_requeue = self.data.pop(key)
            self.data[key] = to_requeue

    def manage_memory(self):
        """Pops entries from the queue until occupied memory is less than the maximum allocated."""
        dms_sz = self.compute_memory()

        while dms_sz > self.max_memory:
            print('Memory limit exceeded. Purging old data...')
            print('Currently using: ', dms_sz, 'bytes')
            print('Maximum allowed: ', self.max_memory, 'bytes')
            self.pop()
            dms_sz = self.compute_memory()
            print('Now using: ', dms_sz, 'bytes')

        self.save_state()

    def compute_memory(self):
        """Computes the memory footprint of the entire data structure."""
        def _compute_memory(coll):
            dms_sz = 0

            for value in coll.values():
                if isinstance(value, np.ndarray):
                    array_sz = value.nbytes
                else:
                    array_sz = _compute_memory(value)

                dms_sz += array_sz
            return dms_sz

        dms_sz = _compute_memory(self.data)
        self.memory_used = dms_sz
        return dms_sz

    def add_data(self, value, *args):
        """Adds value to self.data[arg[0]][...][arg[N-1]]. Requeues self.data[arg[0]] after updating."""

        # def _add_data(keys, val):
        #     val = {keys.pop(): val}
        #     if keys:
        #         val = _add_data(keys, val)
        #     return val

        # # TODO: generalize this to nested dictionaries greater than depth=2...
        # args = list(args)

        # if args[0] in self.data:
        #     # dictionary at depth=1 already defined for key=args[0]
        #     tmp_dict = _add_data(args[1:], value)
        #     self.data[args[0]].update(tmp_dict)
        # else:
        #     # dictionary at depth=1 not defined yet for key=args[0]
        #     try:
        #         tmp_dict = _add_data(args[1:], value)
        #     except IndexError:
        #         # this dictionary only goes to depth=2
        #         tmp_dict = value
        #     finally:
        #         self.data[args[0]] = tmp_dict
        self.data[args[0]] = value

        self.requeue(args[0])
        self.manage_memory()

    def get_data(self, *args):
        """Retrieves NumPy ndarray from self.data according to provided sequence of keys."""
        tmp = self.data

        for key in args:
            if isinstance(tmp, np.ndarray):
                print('>>> Warning: Already reached end of data tree. Too many arguments provided.')
                print('keys provided: {0}'.format(args))
                print('current key: {0}'.format(key))
                break
            else:
                try:
                    tmp = tmp[key]
                except KeyError:
                    logging.info('DMS: Data not yet in DMS, loading...')
                    raise(KeyError('KeyError when retrieving: {0}'.format(key)))

        self.requeue(args[0])
        logging.info('DMS: Data located in DMS, retrieving...')
        return tmp
