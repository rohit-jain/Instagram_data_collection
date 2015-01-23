import csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn import metrics

# constants
MIN_N_CLUSTERS = 2
MAX_N_CLUSTERS = 26

def read_data(filename):
	with open(filename, 'rU') as csvf:
         return [map(float,row[-26:]) for row in csv.reader(csvf)]

def cluster(X,K):
	X = np.array(X)
	km = KMeans(n_clusters = K)
	km.fit(X)
	labels = km.labels_
	return metrics.silhouette_score(X, labels, metric='euclidean')

def plot_coefficients(coeffs):
	plt.plot(range(MIN_N_CLUSTERS,MAX_N_CLUSTERS),coeffs)
	plt.ylabel("silhouette_score")
	plt.xlabel("number of clusters")
	plt.show()

def analyze(filename):
	X = read_data(filename)
	coeffs = [] 
	for k in range(MIN_N_CLUSTERS,MAX_N_CLUSTERS):
		coeffs.append(cluster(k))
	plot_coefficients(coeffs)

if __name__ == "__main__":
	analyze("moma_user_baseline.csv")	