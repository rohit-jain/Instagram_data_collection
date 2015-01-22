import csv
import numpy as np
from sklearn.cluster import KMeans

def read_data(filename):
	with open(filename, 'rU') as csvf:
         return [map(float,row[-26:]) for row in csv.reader(csvf)]

if __name__ == "__main__":
	p = read_data("moma_user_baseline.csv")
	# map(int,p)
	K = 3
	km = KMeans(n_clusters = K)
	km.fit(p)
	print km.labels_

