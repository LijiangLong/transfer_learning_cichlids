import os
import sys
import json
import numpy as np
import torch
import torchvision
from torch import nn
from torch import optim
from torch.optim import lr_scheduler
from torch.autograd import Variable
import pdb
import pandas as pd
import time

from models import DANN_model
from opts import parse_opts
from transforms import (
    Compose, Normalize, Scale, CenterCrop,
    RandomHorizontalFlip,RandomVerticalFlip, FixedScaleRandomCenterCrop, 
    ToTensor,TemporalCenterCrop, TemporalCenterRandomCrop,
    ClassLabel, VideoID,TargetCompose)
from data_loader import get_training_set, get_validation_set, get_test_set
from utils import Logger,AverageMeter, calculate_accuracy



def train_epoch(epoch, train_loader,test_loader, model, criterion, domain_criterion,optimizer, opt,
                epoch_logger, batch_logger):
    print('train at epoch {}'.format(epoch))
    
    len_train = len(train_loader)
    len_test = len(test_loader)
    
    test_iter = iter(test_loader)
    model.train()

    batch_time = AverageMeter()
    data_time = AverageMeter()
    total_losses = AverageMeter()
    train_label_accuracies = AverageMeter()
    train_domain_accuracies = AverageMeter()
    test_label_accuracies = AverageMeter()
    test_domain_accuracies = AverageMeter()
    
    
    end_time = time.time()
    
    for i, (inputs, targets, paths) in enumerate(train_loader):
    
        p = float(i + epoch * len_train) / opt.n_epochs / len_train
        alpha = 2. / (1. + np.exp(-10 * p)) - 1
        
        data_time.update(time.time() - end_time)
        batch_size = inputs.size(0)
        if not opt.no_cuda:
            targets = targets.cuda(async=True)


        inputs = Variable(inputs)
        targets = Variable(targets)
        train_output_label,train_output_domain = model(inputs, alpha=alpha)
        train_label_loss = criterion(train_output_label, targets)
        train_label_acc = calculate_accuracy(train_output_label, targets)
        train_domain_targets = torch.zeros(batch_size).long().cuda()
        train_domain_loss = domain_criterion(train_output_domain,train_domain_targets)
        train_domain_acc = calculate_accuracy(train_output_domain,train_domain_targets)
        if i < len_test:
            test_inputs,test_targets,test_paths = test_iter.next()
            if not opt.no_cuda:
                test_targets = test_targets.cuda(async=True)
            test_inputs = Variable(test_inputs)
            test_targets = Variable(test_targets)
            test_output_label,test_output_domain = model(test_inputs, alpha=alpha)
            test_label_loss = criterion(test_output_label, test_targets)
            test_label_acc = calculate_accuracy(test_output_label, test_targets)
            test_domain_label = torch.ones(batch_size).long().cuda()
            test_domain_loss = domain_criterion(test_output_domain,test_domain_label)
            test_domain_acc = calculate_accuracy(test_output_domain,test_domain_label)
        
        loss = train_label_loss+train_domain_loss+test_domain_loss
        losses.update(loss.item(), inputs.size(0))
        
        train_label_accuracies.update(train_label_acc, batch_size)
        train_domain_accuracies.update(train_domain_acc, batch_size)
        test_label_accuracies.update(test_label_acc, batch_size)
        test_domain_accuracies.update(test_domain_acc, batch_size)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        batch_time.update(time.time() - end_time)
        end_time = time.time()

        batch_logger.log({
            'epoch': epoch,
            'batch': i + 1,
            'iter': (epoch - 1) * len(train_loader) + (i + 1),
            'loss': losses.val,
            'train_label_acc': train_label_accuracies.val,
            'train_domain_acc': train_domain_accuracies.val,
            'test_label_acc': test_label_accuracies.val,
            'test_domain_acc': test_domain_accuracies.val,
            'lr': optimizer.param_groups[0]['lr'],
        })

        print('Epoch: [{0}][{1}/{2}]\t'
              'Time {batch_time.val:.3f} ({batch_time.avg:.3f})\t'
              'Data {data_time.val:.3f} ({data_time.avg:.3f})\t'
              'Loss {loss.val:.4f} ({loss.avg:.4f})\t'
              'Acc {acc.val:.3f} ({acc.avg:.3f})'.format(
                  epoch,
                  i + 1,
                  len(train_loader),
                  batch_time=batch_time,
                  data_time=data_time,
                  loss=losses,
                  acc=accuracies))
    epoch_logger.log({
        'epoch': epoch,
        'loss': losses.avg,
        'train_label_acc': train_label_accuracies.avg,
        'train_domain_acc': train_domain_accuracies.avg,
        'test_label_acc': test_label_accuracies.avg,
        'test_domain_acc': test_domain_accuracies.avg,
        'lr': optimizer.param_groups[0]['lr']
    })

    if epoch % opt.checkpoint == 0:
        save_file_path = os.path.join(opt.result_path,
                                      'save_{}.pth'.format(epoch))
        states = {
            'epoch': epoch + 1,
            'state_dict': model.state_dict(),
            'optimizer': optimizer.state_dict(),
        }
        torch.save(states, save_file_path)

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
    confusion_matrix.to_csv(opt.result_path + '/ConfusionMatrix_' + str(epoch) + '.csv')
    confidence_matrix = pd.DataFrame.from_dict(confidence_for_each_validation, orient='index')
    confidence_matrix.to_csv(opt.result_path + '/ConfidenceMatrix.csv')
    
    #########  temp line, needs to be removed##################################
    
    
    logger.log({'epoch': epoch, 'loss': losses.avg, 'acc': accuracies.avg})

    return losses.avg

def test_epoch(epoch, data_loader, model, criterion, opt, logger):
    print('test at epoch {}'.format(epoch))
    
    model.eval()

    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()
    accuracies = AverageMeter()

    end_time = time.time()

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

    
    logger.log({'epoch': epoch, 'loss': losses.avg, 'acc': accuracies.avg})

    return losses.avg


def main():
    opt = parse_opts()
    if opt.root_path != '':
        opt.video_path = os.path.join(opt.root_path, opt.video_path)
        opt.annotation_path = os.path.join(opt.root_path, opt.annotation_path)
        opt.result_path = os.path.join(opt.root_path, opt.result_path)
        if not os.path.exists(opt.result_path):
            os.mkdir(opt.result_path)
        if opt.resume_path:
            opt.resume_path = os.path.join(opt.root_path, opt.resume_path)
    print(opt)
    with open(os.path.join(opt.result_path, 'opts.json'), 'w') as opt_file:
       json.dump(vars(opt), opt_file)

    torch.manual_seed(opt.manual_seed)
#     pdb.set_trace()
    model = DANN_model.DANN_resnet18(
                num_classes=opt.n_classes,
                shortcut_type=opt.resnet_shortcut,
                sample_size=opt.sample_size,
                sample_duration=opt.sample_duration)
                
                
#     model = torchvision.models.video.r3d_18(pretrained=False, progress=True)
#     model.fc = nn.Linear(in_features=512, out_features=10, bias=True)
    
    if not opt.no_cuda:
        model = model.cuda()
        model = nn.DataParallel(model, device_ids=None)
    parameters = model.parameters()
#     model, parameters = generate_model(opt)
    print(model)
    criterion = nn.CrossEntropyLoss()
    domain_criterion = nn.CrossEntropyLoss()
    if not opt.no_cuda:
        criterion = criterion.cuda()
        domain_criterion.cuda()
    if not opt.no_train:
        crop_method = FixedScaleRandomCenterCrop(opt.sample_size,opt.sample_spacing)
        spatial_transforms = {}
        with open(opt.mean_file) as f:
            for i,line in enumerate(f):
                if i==0:
                    continue
                tokens = line.rstrip().split(',')
                norm_method = Normalize([float(x) for x in tokens[1:4]], [float(x) for x in tokens[4:7]]) 
                spatial_transforms[tokens[0]] = Compose([crop_method, RandomHorizontalFlip(),RandomVerticalFlip(), ToTensor(opt.norm_value), norm_method])
        annotateData = pd.read_csv(opt.annotation_file, sep = ',', header = 0)
        keys = annotateData['Location']
        values = annotateData['MeanID']

        annotationDictionary = dict(zip(keys, values))

        temporal_transform = TemporalCenterRandomCrop(opt.sample_duration)
        target_transform = ClassLabel()
        training_data = get_training_set(opt, spatial_transforms,
                                         temporal_transform, target_transform, annotationDictionary)
        train_loader = torch.utils.data.DataLoader(
            training_data,
            batch_size=opt.batch_size,
            shuffle=True,
            num_workers=opt.n_threads,
            pin_memory=True)
        train_logger = Logger(
            os.path.join(opt.result_path, 'train.log'),
            ['epoch', 'loss', 'acc', 'lr'])
        train_batch_logger = Logger(
            os.path.join(opt.result_path, 'train_batch.log'),
            ['epoch', 'batch', 'iter', 'loss', 'acc', 'lr', 'means'])

        if opt.nesterov:
            dampening = 0
        else:
            dampening = opt.dampening
        optimizer = optim.SGD(
            parameters,
            lr=opt.learning_rate,
            momentum=opt.momentum,
            dampening=dampening,
            weight_decay=opt.weight_decay,
            nesterov=opt.nesterov)
        scheduler = lr_scheduler.ReduceLROnPlateau(
            optimizer, 'min', patience=opt.lr_patience)
    if not opt.no_val:
        spatial_transforms = {}
        with open(opt.mean_file) as f:
            for i,line in enumerate(f):
                if i==0:
                    continue
                tokens = line.rstrip().split(',')
                norm_method = Normalize([float(x) for x in tokens[1:4]], [float(x) for x in tokens[4:7]]) 
                spatial_transforms[tokens[0]] = Compose([CenterCrop(opt.sample_size,opt.sample_spacing),ToTensor(opt.norm_value), norm_method])

        

        temporal_transform = TemporalCenterCrop(opt.sample_duration)
        target_transform = ClassLabel()
        validation_data = get_validation_set(
            opt, spatial_transforms, temporal_transform, target_transform, annotationDictionary)
        val_loader = torch.utils.data.DataLoader(
            validation_data,
            batch_size=opt.batch_size,
            shuffle=False,
            num_workers=opt.n_threads,
            pin_memory=True)
        val_logger = Logger(
            os.path.join(opt.result_path, 'val.log'), ['epoch', 'loss', 'acc'])

    if not opt.no_test:
        temporal_transform = TemporalCenterCrop(opt.sample_duration)
        target_transform = ClassLabel()
        test_data = get_test_set(
            opt, spatial_transforms, temporal_transform, target_transform, annotationDictionary)
        test_loader = torch.utils.data.DataLoader(
            test_data,
            batch_size=opt.batch_size,
            shuffle=False,
            num_workers=opt.n_threads,
            pin_memory=True)
        test_logger = Logger(
            os.path.join(opt.result_path, 'test.log'), ['epoch', 'loss', 'acc'])
    if opt.resume_path:
        print('loading checkpoint {}'.format(opt.resume_path))
        checkpoint = torch.load(opt.resume_path)
        assert opt.arch == checkpoint['arch']

        opt.begin_epoch = checkpoint['epoch']
        model.load_state_dict(checkpoint['state_dict'])
        if not opt.no_train:
            optimizer.load_state_dict(checkpoint['optimizer'])
    
    print('run')
    pdb.set_trace()
    for i in range(opt.begin_epoch, opt.n_epochs + 1):
        if not opt.no_train:
            train_epoch(i, train_loader, test_loader, model, criterion,domain_criterion, optimizer, opt,
                        train_logger, train_batch_logger)
        if not opt.no_val:
            validation_loss = val_epoch(i, val_loader, model, criterion, opt,
                                        val_logger)

        if not opt.no_train and not opt.no_val:
            scheduler.step(validation_loss)
#         if not opt.no_test:
#             test_epoch(i, test_loader, model, criterion, opt,
#                                         test_logger)
if __name__ == '__main__':
    main()