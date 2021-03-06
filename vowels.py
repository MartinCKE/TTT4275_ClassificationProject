''' Vowels task python script for classification project in TTT4275 - EDC
    by Einar Avdem & Martin Ericsson
'''

import numpy as np
import os
from sklearn.mixture import GaussianMixture as GMM
import pandas as pd
from scipy.stats import multivariate_normal
import matplotlib.pyplot as plt
import seaborn as sn

vowels = ['ae','ah','aw','eh','er','ei','ih','iy','oa','oo','uh','uw']

def main():
    global features
    nTraining = 70
    features=range(7,16)

    types, data = loadData(features)

    vowelCol = pd.Series([col1[3:] for col1 in types])

    df = pd.DataFrame(data, index=vowelCol)
    trainingData, testingData = splitData(df, nTraining)

    ### Task 1 a-c ###
    print("Starting task 1:")
    print("Training single gaussian mixture classifier with full covariance matrix.")
    vowelModels = singleGMTraining(trainingData, diag=False)
    predictions, actualVowels = singleGMTesting(vowelModels, testingData)
    print("Testing classifier and plotting confusion matrix...")
    confMatrix = confusionMatrixCalc(predictions, actualVowels)
    plotConfusionMatrix(confMatrix)

    ### Task 1 c ###
    print("Training single gaussian mixture classifier with diagonal covariance matrix.")
    vowelModels = singleGMTraining(trainingData, diag=True)
    predictions, actualVowels = singleGMTesting(vowelModels, testingData)
    print("Testing classifier and plotting confusion matrix...")
    confMatrix = confusionMatrixCalc(predictions, actualVowels)
    plotConfusionMatrix(confMatrix)

    ### Task 2 a-b ###
    print("Starting task 2")
    print("Training multiple gaussian mixture classifier with full covariance matrix.")
    print("M = 2")
    M = 2
    GaussianMixtureModels = GMMTraining(trainingData, M)
    predictions, actualVowels = GMMTesting(GaussianMixtureModels, testingData, M)
    print("Testing classifier and plotting confusion matrix...")
    confMatrix = confusionMatrixCalc(predictions, actualVowels)
    plotConfusionMatrix(confMatrix)

    ## Task 2 c ##
    print("Training multiple gaussian mixture classifier with full covariance matrix.")
    print("M = 3")
    M = 3
    GaussianMixtureModels = GMMTraining(trainingData, M)
    predictions, actualVowels = GMMTesting(GaussianMixtureModels, testingData, M)
    print("Testing classifier and plotting confusion matrix...")
    confMatrix = confusionMatrixCalc(predictions, actualVowels)
    plotConfusionMatrix(confMatrix)

def findErrorRate(X):
    ''' Calculates error rate from confusion matrix '''
    errorRate = (1-np.sum(X.diagonal())/np.sum(X))*100
    return errorRate

def getMeanAndCovariance(df, features, vowel, diag=False):
    '''
        Calculates mean and covariance of given vowel and
        features to use.
    '''
    vowelDataFrame = df.loc[vowel]
    mean = vowelDataFrame.mean(axis=0).values
    cov = vowelDataFrame.cov().values

    if diag:
       cov = np.diag(np.diag(cov))

    return mean, cov

def confusionMatrixCalc(predictions, actualVowels, diag=False):
    ''' Builds confusion matrix based on classifier predictions and actual class.
    '''
    confMatrix = np.zeros((len(vowels), len(vowels)))

    for i in range(len(predictions)):
        vowelIndex = vowels.index(actualVowels[i])
        confMatrix[vowelIndex][(predictions[i])] += 1

    return confMatrix

def plotConfusionMatrix(confusionMatrix):
    ''' Function which plots confusion matrix as heat map with
        calculated error rate.
    '''
    ## Plotting
    fig, ax = plt.subplots(figsize=(8,6))
    im = ax.imshow(confusionMatrix, cmap='copper')
    ax.set_xticks(np.arange(0, len(vowels)))
    ax.set_yticks(np.arange(0, len(vowels)))
    ax.set_xticklabels(vowels)
    ax.set_yticklabels(vowels)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    ### Plotting error rate within heat map ###
    errorRate = findErrorRate(confusionMatrix)
    print("errorRate = ", errorRate)
    textstr = ('Error rate = %.1f%%' %(errorRate))
    textBox = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(0.72, 0.935, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=textBox)

    # Creating text annotations in cells
    for i in range(0, len(vowels)):
        for j in range(0, len(vowels)):
            text = ax.text(j, i, confusionMatrix[i,j],
                           ha="center", va="center", color="w")

    ax.set_title("Heatmap visualizing confusion matrix")
    fig.tight_layout()
    plt.colorbar(im)
    plt.show()


def GMMTesting(GaussianMixtureModels, testingData, M):
    ''' Tests the GMM classifier by using mixture models to find  the
        largest probabilities from input testing samples and predicting class.
    '''
    probabilities = np.zeros((len(vowels), len(testingData)))

    for i, vowel in enumerate(vowels):
        GaussianMixtureModel = GaussianMixtureModels[i] ## Get model for current vowel
        for j in range(M):
            curve = multivariate_normal(mean=GaussianMixtureModel.means_[j],
                                        cov=GaussianMixtureModel.covariances_[j], allow_singular=True)
            probabilities[i] += GaussianMixtureModel.weights_[j] * curve.pdf(testingData.values)

    predictions = np.argmax(probabilities, axis=0)
    actualVowels = testingData.index.values

    return predictions, actualVowels

def GMMTraining(trainingData, M):
    ''' Trains the GMM classifier by bulding mixure models from training vowel
        samples, using GMM method.
    '''

    GaussianMixtureModels = []
    for vowel in vowels:
        trainingVowelData = trainingData.loc[vowel].values
        gmm = GMM(n_components=M, covariance_type='diag',reg_covar=1e-4, random_state=0)
        gmm.fit(trainingVowelData)
        GaussianMixtureModels.append(gmm)

    return GaussianMixtureModels

def singleGMTraining(trainingData, diag=False):
    ''' Trains the single Gaussian mode classifier by building multivariate models
        from the input training vowel data
    '''
    vowelModels = list()

    for vowel in vowels:
        mean, covariance = getMeanAndCovariance(trainingData, features, vowel, diag)
        multiVariateModel = multivariate_normal(mean = mean, cov=covariance)
        vowelModels.append(multiVariateModel)

    return vowelModels

def singleGMTesting(vowelModels, testingData):
    ''' Tests the single Gaussian classifier by using the multivariate vowel models
        against testing samples, where class prediction is decided from largest
        probability value
    '''
    probabilities = np.zeros((len(vowels), len(testingData)))

    for i, vowel in enumerate(vowels):
        i_vowel = vowelModels[i]
        probabilities[i] = i_vowel.pdf(testingData.values)

    predictions = np.argmax(probabilities, axis=0)
    actualVowels = testingData.index.values

    return predictions, actualVowels

def splitData(df, nTraining):
    ''' Splits data in to training and testing sub-sets
    '''

    trainingdf = pd.DataFrame()
    testingdf = pd.DataFrame()

    trainingdf = pd.concat([trainingdf.append(df.loc[vowel][:nTraining]) for vowel in vowels])
    testingdf = pd.concat([testingdf.append(df.loc[vowel][nTraining:]) for vowel in vowels])

    return trainingdf, testingdf


def loadData(features):
    ''' Loads raw feature data from vowels data file
    '''

    rawData = np.genfromtxt('./Data/Wovels/vowdata_nohead.dat', dtype = str, delimiter=',',)
    types = list()
    data = np.zeros((len(rawData), len(features)), dtype='int')

    for i, line in enumerate(rawData):
        line = line.split()
        types.append(line[0])
        for index, val in enumerate(features):
            data[i, index] = int(line[val])

    types = np.array(types)
    return types, data


if __name__ == '__main__':
    main()
