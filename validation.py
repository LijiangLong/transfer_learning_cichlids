import torch
from torch.autograd import Variable
import time
import sys
import numpy as np
import pandas as pd
import pdb
from utils import AverageMeter, calculate_accuracy


def val_epoch(epoch, data_loader, model, criterion, opt, logger):
    print('validation at epoch {}'.format(epoch))
    
    model.eval()

    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    accuracies = AverageMeter()

    end_time = time.time()
    
    #########  temp line, needs to be removed##################################
    file  = 'epoch_'+ str(epoch)+'_validation_matrix.csv'
    confusion_matrix = np.zeros((opt.n_classes,opt.n_classes))
    confidence_for_each_validation = {}
    ###########################################################################
    
    #pdb.set_trace()
    for i, (inputs, targets, paths) in enumerate(data_loader):
        data_time.update(time.time() - end_time)

        if not opt.no_cuda:
            targets = targets.cuda(async=True)
        with torch.no_grad():
            
            inputs = Variable(inputs)
            targets = Variable(targets)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            acc = calculate_accuracy(outputs, targets)
            #########  temp line, needs to be removed##################################
            for j in range(len(targets)):
                confidence_for_each_validation[paths[j]] = [x.item() for x in outputs[j]]
            
            rows = [int(x) for x in targets]
            columns = [int(x) for x in np.argmax(outputs.cpu(),1)]
            assert len(rows) == len(columns)
            for idx in range(len(rows)):
                confusion_matrix[rows[idx]][columns[idx]] +=1
            
            ###########################################################################
            losses.update(loss.item(), inputs.size(0))
            accuracies.update(acc, inputs.size(0))

            batch_time.update(time.time() - end_time)
            end_time = time.time()

            print('Epoch: [{0}][{1}/{2}]\t'
                  'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
                  'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
                  'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
                  'Acc {acc.val:.3f} ({acc.avg:.3f})'.format(
                      epoch,
                      i + 1,
                      len(data_loader),
                      batch_time=batch_time,
                      data_time=data_time,
                      loss=losses,
                      acc=accuracies))
    #########  temp line, needs to be removed##################################
    print(confusion_matrix)
    confusion_matrix = pd.DataFrame(confusion_matrix)
    confusion_matrix.to_csv(opt.result_path + 'ConfusionMatrix_' + str(epoch) + '.csv')
    confidence_matrix = pd.DataFrame.from_dict(confidence_for_each_validation, orient='index')
    confidence_matrix.to_csv(opt.result_path + 'ConfidenceMatrix.csv')
    
    #########  temp line, needs to be removed##################################
    
    
    logger.log({'epoch': epoch, 'loss': losses.avg, 'acc': accuracies.avg})

    return losses.avg
