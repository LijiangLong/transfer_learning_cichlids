#plot the log
import matplotlib.pyplot as plt
import pdb
train_log_file = '/Users/lijiang/Downloads/train 20.log'
test_log_file = '/Users/lijiang/Downloads/val 19.log'
train_accuracies = []
test_accuracies = []
fig, ax = plt.subplots()
with open(train_log_file,'r') as input:
    input.readline()
    for line in input:
        accuracy = line.split('\t')[2][7:13]
        train_accuracies.append(float(accuracy))

with open(test_log_file,'r') as input:
    input.readline()
    for line in input:
        accuracy = line.split('\t')[2][7:13]
        test_accuracies.append(float(accuracy))
        
plt.plot(range(len(train_accuracies)),train_accuracies)
plt.plot(range(len(test_accuracies)),test_accuracies)
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.ylim(0,1)
plt.legend(['train','test'])
fig.savefig('train_test_log.svg', transparent=True)