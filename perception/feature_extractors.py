"""
Classes for image feature extraction.
Author: Jeff Mahler
"""
from abc import ABCMeta, abstractmethod

import copy
import IPython
import logging
import numpy as np
import os
import time

import alan.constants as constants
from alan.rgbd.cnn import AlexNet
from alan.rgbd.image import Image, ColorImage

class FeatureExtractor:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def extract(self, image):
        """
        Returns a set of extracted features for an image
        Params:
           image: Image object to extract for
        """
        pass

class CNNBatchFeatureExtractor(FeatureExtractor):
    """ Extract feature descriptors for images in a giant batch """
    def __init__(self, config):
        self.cnn_ = AlexNet(config, use_default_weights=True)

    def open(self):
        self.cnn_.open_session()

    def close(self):
        self.cnn_.close_session()

    def _forward_pass(self, images):
        """ Forward pass images through the CNN """
        # form image array
        num_images = len(images)
        if num_images == 0:
            return None
        for image in images:
            if not isinstance(image, Image):
                new_images = []
                for image in images:
                    new_images.append(ColorImage(image, frame='unspecified'))
                images = new_images
                break
                #raise ValueError('Must use AUTOLAB Image object')

        im_height = images[0].height
        im_width = images[0].width
        channels = images[0].channels
        image_arr = np.zeros([num_images, im_height, im_width, channels])
        for j, image in enumerate(images):
            image_arr[j,:,:,:] = image.raw_data

        # predict
        fp_start = time.time()
        final_blobs = self.cnn_.featurize(image_arr)
        fp_stop = time.time()
        logging.debug('Featurization took %f sec per image' %((fp_stop - fp_start) / len(images)))
        return final_blobs.reshape(final_blobs.shape[0], -1)

    def extract(self, images):
        """ Form feature descriptors for a set of images """
        return self._forward_pass(images)

class CNNReusableBatchFeatureExtractor(CNNBatchFeatureExtractor):
    """ Extract feature descriptors for images in a giant batch """
    def __init__(self, cnn):
        self.cnn_ = cnn

