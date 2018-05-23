from concurrent import futures
import time
import grpc
import async_pb2_grpc
import async_pb2
import sys
import threading as th
import queue
import pickle
from implementations import *
import copy
import random

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

q = queue.Queue()
lambda_ = 0.001
l_rate = 0.3
max_iter = 10000
weights = zeros(47237)
c1 = 1
c2 = 1
i=0
converged = False
port = 50051

# with open('X.pickle', 'rb') as handle:
#     X = pickle.load(handle)
#
# with open('y.pickle', 'rb') as handle:
#     y = pickle.load(handle)
# Reading of the files

print('Reading the files')
file1 = open("./datasets/datasets/lyrl2004_vectors_test_pt0.dat")
file2 = open("./datasets/datasets/lyrl2004_vectors_test_pt1.dat")
file3 = open("./datasets/datasets/lyrl2004_vectors_test_pt2.dat")
file4 = open("./datasets/datasets/lyrl2004_vectors_test_pt3.dat")
files = [file1, file2, file3, file4]
# Parsing the files and storing the ids of the articles along with their respective features
id_ = []
samples = []
for f in files:
    for i in f.readlines():
        id_.append(i.split()[0])
        samples.append(i.strip().split()[2:])
categories = open("./datasets/datasets/rcv1-v2.topics.qrels")
print('Done!')

# Get a mapping of each article id to the set of categories it belongs to
print('Mapping into categories')
cat = []
cat_count = {}
id_to_labels = {}
for line in open("./datasets/datasets/rcv1-v2.topics.qrels").readlines():
    s = line.split(' ')
    id_to_labels.setdefault(s[1],[]).append(s[0])
    cat_count.setdefault(s[0],[]).append(s[1])
    cat.append(s[0])
print('Done!')

# Set the label vector based on the chosen category
# Set the features matrix as sparse matrix by storing only the non zero components in a dict
print('Setting the labels')

y = set_labels("ECAT", id_, id_to_labels)
X = []
for sample in samples:
    d = dict()
    for feature in sample:
        key = int(feature.split(':')[0])
        value = float(feature.split(':')[1])
        d[key] = value
    X.append(d)


x_train, y_train, x_test, y_test = split_data(X, y, ratio=0.8)

def compute_grad(y, X, w,c1,c2, lambda_):
    '''
    Compute the gradient of a sample with penalized loss for inbalanced input data.
    :param y: the label of the sample
    :param X: the sample as a dict
    :param w: the weight vector
    :param c1: the penalization for positive label
    :param c2: the penalization for negative label
    :param lambda_: the regularizer
    :return: the gradient as a dictionaries of non null entries
    '''
    def is_support(y_n, x_n, w):
        return y_n*sum([x_n[x]*w[x] for x in x_n])<1
    res = X.copy()
    if is_support(y,X,w):
        for x in X:
            if y == 1:
                res[x] = -X[x] * y * c2 + lambda_ * w[x]
            else:
                res[x] = -X[x] * y * c1 + lambda_ * w[x]
    else:
        for x in X:
            res[x] = lambda_ * w[x]
    return res


class async_SGDServicer(async_pb2_grpc.async_SGDServicer):

    def Send_Weights(self, request, context):
        '''
        Receive the data necessary to compute the gradient update and returns the updated dimensions
        '''
        weights_2 = request.w_up
        q.put(dict(weights_2))
        return async_pb2.ACK(ack=True)

def serve():
    '''
    Initialize the server on port "port"

    '''
    max_workers = 20
    print("Connecting to port", port)
    print("Number of workers", max_workers)
    server = grpc.server(futures.ThreadPoolExecutor (max_workers=max_workers))
    async_pb2_grpc.add_async_SGDServicer_to_server(async_SGDServicer(), server)
    server.add_insecure_port('[::]:'+str(port))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except (KeyboardInterrupt, SystemExit):
        server.stop(0)

def compute(ips):
    ips = ips.split(",")
    channels = []
    stubs = []
    for i, ip in enumerate(ips):
        host = ip+':'+str(port)
        print("Connecting to server: " + host)
        channels.append(grpc.insecure_channel(host))
        stubs.append(async_pb2_grpc.async_SGDStub(channels[i]))

    global converged
    while not converged:
        results = []
        while not q.empty():
            results.append(q.get())
        for update in results:
            for x in update:
                weights[x] -= l_rate * update[x]
        #print(len(results))
        rd = randint(0,len(x_train))
        batch = x_train[rd]
        lab = y_train[rd]
        res = compute_grad(lab,batch,weights ,c1,c2,lambda_)
        for x in res:
                weights[x] -= l_rate * res[x]
        for s in stubs:
            s.Send_Weights(async_pb2.WS_Update(w_up=res))
        #ack1 = stub1.Send_Weights(async_pb2.WS_Update(w_up=res))
        #ack2 = stub2.Send_Weights(async_pb2.WS_Update(w_up=res))
        #ack3 = stub3.Send_Weights(async_pb2.WS_Update(w_up=res))
        #print(hinge_loss(y_train,x_train, weights))
    print('Training accuracy = {}'.format(accuracy(prediction(x_train, weights), y_train)))
    print('Test accuracy = {}'.format(accuracy(prediction(x_test, weights), y_test)))
    return weights
    #    i+=1
def loss(convergence_radius):
    old_loss = 0
    global converged
    while not converged:
        weights_snapshot = copy.deepcopy(weights)
        current_loss = hinge_loss(y_train,x_train, weights_snapshot)
        if old_loss != 0 and (abs(current_loss-old_loss) < convergence_radius):
            converged = True
        old_loss = current_loss
        print(current_loss)
    print(current_loss)


if __name__ == '__main__':
    ###load file the worker
    t2 = th.Thread(target=serve, args=[])
    t2.start()
    time.sleep(30)
    t1 = th.Thread(target=compute, args=[sys.argv[1]])
    t1.start()
    t3 = th.Thread(target=loss, args=[float(sys.argv[2])])
    t3.start()
    t3.join()
    t1.join()
