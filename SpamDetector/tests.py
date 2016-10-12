from django.test import TestCase

# Create your tests here.

import unittest
import os

from SpamDetector.normalize import Normalizer
from SpamDetector.kmeans import KMeanClusterer


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def getDatasetSize(self, datafile):

        norm = Normalizer()
        data = norm.load_csv(datafile)
        iris_data_matrix = []
        for line in data:
            try:
                iris_data_matrix.append(line)
            except IndexError:
                pass
        return len(iris_data_matrix)

    def testKMeanForcedInitialisation(self):
        print("** test KMean Initalisation **")

        k = 2
        workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
        datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
        champs = [1, 2, 3]

        # perform initialization
        kMeanClusterer = KMeanClusterer(k, datafile, champs)

        # check the number of clusters
        clusterNumber = kMeanClusterer.getClusterNumber()
        self.assertTrue(clusterNumber == k, "actual cluster number: " + str(clusterNumber) + "; expected: " + str(k))

        # check the consistency of each cluster
        centroids = set()
        for i in range(clusterNumber):
            currentCluster = kMeanClusterer.getCluster(i)
            # check centroid format
            centroid = currentCluster.getCentroid()
            expectedObsDimensions = len(champs)
            self.assertTrue(len(centroid) == expectedObsDimensions,
                            "centroid expected to contain " + str(expectedObsDimensions) +
                            " data items, has actually " + str(len(centroid)))
            # check observation format
            observations = currentCluster.getObservations()
            self.assertTrue(len(observations) == 0, "0 observation expected per cluster, has actually "
                            + str(len(observations)))

            # check all centroid are different at initialisation
            new_centroid = False
            if tuple(centroid) not in centroids:
                new_centroid = True
                centroids.add(tuple(centroid))
            self.assertTrue(new_centroid, "centroid are different: " + str(new_centroid))


    def testKMeanAssignement(self):
        print("** test KMean assignement **")

        # perform initialization
        k = 2
        workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
        datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
        champs = [1, 2, 3]

        kMeanClusterer = KMeanClusterer(k, datafile, champs)
        datasetSize = self.getDatasetSize(datafile)

        kMeanClusterer.assignement()

        obsNumber = 0
        clusterNumber = kMeanClusterer.getClusterNumber()
        for i in range(clusterNumber):
            currentCluster = kMeanClusterer.getCluster(i)
            observations = currentCluster.getObservations()
            for obs in observations:
                obsNumber += 1

        # check that all observations are assigned
        self.assertTrue(datasetSize == obsNumber, "size of dataset: " + str(datasetSize)
                        + "; current number of observations in cluster:" + str(obsNumber))

        # check that the observations are assigned to the nearest centroid
        centroids = []
        for i in range(clusterNumber):
            currentCluster = kMeanClusterer.getCluster(i)
            centroids.append(currentCluster.getCentroid())

        for i in range(clusterNumber):
            currentCluster = kMeanClusterer.getCluster(i)
            for obs in currentCluster.getObservations():
                distance_to_centroid = kMeanClusterer.computeDistance(obs, currentCluster.getCentroid())
                for j in range(len(centroids)):
                    if i != j:
                        dst = kMeanClusterer.computeDistance(obs, kMeanClusterer.getCluster(j).getCentroid())
                        self.assertTrue(distance_to_centroid <= dst,
                                        "distance to centroid of own cluster " + str(i) + ":"
                                        + str(distance_to_centroid) + "; distance to centroid of cluster" + str(j) + ": " + str(dst))


    def testKMean(self):
        print("** test KMean **")

        # perform initialization
        k = 2
        workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
        datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
        champs = [1, 2, 3]
        kMeanClusterer = KMeanClusterer(k,datafile, champs)
        kMeanClusterer.assignement()

        #total number of lines in the dataset
        dataLines = 0
        norm = Normalizer()
        data_matrix = norm.load_csv(datafile)
        for row in data_matrix:
            if len(row) > 0:
                dataLines += 1

        #check the number of observations from dataset is kept
        totalObsNb = 0
        for clusterNb in range(kMeanClusterer.getClusterNumber()):
            cluster = kMeanClusterer.getCluster(clusterNb)
            totalObsNb += len(cluster.getObservations())

        self.assertTrue(dataLines == totalObsNb, "Number of entries in dataset: "+str(dataLines)
                        +" is different from number of observations in cluster: "+str(totalObsNb))

    def testKMeanUpdate(self):
        print("** test KMean update **")

        k = 2
        workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
        datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
        champs = [1, 2, 3]
        kMeanClusterer = KMeanClusterer(k,datafile, champs)

        kMeanClusterer.assignement()

        # check existence of centroid
        for i in range(kMeanClusterer.getClusterNumber()):
            current_cluster = kMeanClusterer.getCluster(i)
            self.assertTrue(len(current_cluster.getCentroid()) > 0, "void centroid for cluster "+str(i))

        # check validity of centroid
        for i in range(kMeanClusterer.getClusterNumber()):
            current_cluster = kMeanClusterer.getCluster(i)
            current_centroid = current_cluster.getCentroid()
            obs = current_cluster.getObservations()
            for j in range(len(current_centroid)):
                tmp = 0
                for i in range(len(obs)):
                    try:
                        tmp += float(obs[i][j])
                    except ValueError:
                        pass # field is not numeric
                try:
                    value = float(current_centroid[j])#for test that data is numeric
                    self.assertTrue(tmp/len(obs) == value, "current centroid: "+str(value)
                                +"; actual centroid value: "+str(tmp/len(obs)))
                except ValueError:
                        pass # field is not numeric

    def testarray_equility(self):
        print("** test array equility **")

        a = [5.1, 3.5, 1.4, 0.2]
        b = [5.1, 3.5, 1.4, 0.2]
        self.assertTrue(a == b, "a not equal to b")

    def testNormalize(self):
        print("** test des valeurs normalisees **")
        norm = Normalizer()
        workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
        datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
        data = norm.load_csv(datafile)
        data = norm.normalization()
        for l in data:
            for c in l:
                self.assertTrue((c >=0 and c<=1) , "les valeur ne sont pas entre 0 et 1")

    def testStats(self):
        print("** test des statistiques**")
        norm = Normalizer()
        workpath = os.path.dirname(os.path.abspath(__file__)) #Returns the Path your .py file is in
        datafile = os.path.join(workpath, 'dataset/spambase.data.txt')
        data = norm.load_csv(datafile)
        data = norm.normalization()
        normalizedData = norm.normalization()
        normSplitedData = norm.split(normalizedData)
        normNospams = normSplitedData[1]
        normSpams = normSplitedData[0]
        stat = norm.stats(normSpams,normNospams)
        self.assertTrue(stat[0][0][57]==norm.truncate(1,5) , "Les stats des spams ne peuvent pas etre correctes : le minimum des spams n'est pas egal a 1 pour le dernier champ" + stat[0][0][57])
        self.assertTrue(stat[0][1][57]==norm.truncate(1,5) , "Les stats des spams ne peuvent pas etre correctes : le maximum des spams n'est pas egal a 1 pour le dernier champ")
        self.assertTrue(stat[0][2][57]==norm.truncate(1,5) , "Les stats des spams ne peuvent pas etre correctes : la moyenne des spams n'est pas egale a 1 pour le dernier champ")
        self.assertTrue(stat[0][3][57]==norm.truncate(0,5) , "Les stats des spams ne peuvent pas etre correctes : la moyenne des spams n'est pas egale a 0 pour le dernier champ")
        self.assertTrue(stat[1][0][57]==norm.truncate(0,5) , "Les stats des non spams ne peuvent pas etre correctes : le minimum des non spams n'est pas egal a 0 pour le dernier champ")
        self.assertTrue(stat[1][1][57]==norm.truncate(0,5) , "Les stats des non spams ne peuvent pas etre correctes : le maximum des non spams n'est pas egal a 0 pour le dernier champ")
        self.assertTrue(stat[1][2][57]==norm.truncate(0,5) , "Les stats des non spams ne peuvent pas etre correctes : la moyenne des non spams n'est pas egale a 0 pour le dernier champ")
        self.assertTrue(stat[1][3][57]==norm.truncate(0,5) , "Les stats des non spams ne peuvent pas etre correctes : la moyenne des non spams n'est pas egale a 0 pour le dernier champ")

if __name__ == "__main__":
    unittest.main()