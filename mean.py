def get_mean(norm_value=255, dataset='activitynet'):
    assert dataset in ['activitynet', 'kinetics','cichlids']

    if dataset == 'activitynet':
        return [
            114.7748 / norm_value, 107.7354 / norm_value, 99.4750 / norm_value
        ]
    elif dataset == 'kinetics':
        # Kinetics (10 videos for each class)
        return [
            110.63666788 / norm_value, 103.16065604 / norm_value,
            96.29023126 / norm_value
        ]
        #This mean is for MC6_5 and the next is for CV10_3
    elif dataset == 'cichlids':
        return [
            90 / norm_value, 96 / norm_value,
            88 / norm_value
            ]
            
#     
#     elif dataset == 'cichlids':
#         return [
#             65.61218605139486 / norm_value, 81.2619239251075 / norm_value,
#             21.748924667533245 / norm_value
#         ]



def get_std(norm_value=255, dataset='activitynet'):
    #This mean is for MC6_5 and the next is for CV10_3
    if dataset == 'cichlids':
        return [
            35 / norm_value, 37 / norm_value,
            38 / norm_value
        ]
#     if dataset == 'cichlids':
#         return [
#             31.456187524920107 / norm_value, 31.98858896375627 / norm_value,
#             22.22160022831104 / norm_value
#         ]


    # Kinetics (10 videos for each class)
    else:
        return [
            38.7568578 / norm_value, 37.88248729 / norm_value,
            40.02898126 / norm_value
        ]
    
