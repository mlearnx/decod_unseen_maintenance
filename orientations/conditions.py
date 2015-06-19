# Decoding parameters
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVR
from utils import (
    clf_2class_proba, SVR_angle, angle2circle,
    scorer_angle, scorer_auc, scorer_spearman)

scaler = StandardScaler()

# SVC
svc = clf_2class_proba(C=1, class_weight='auto')
pipeline_svc = Pipeline([('scaler', scaler), ('svc', svc)])

# SVR
svr = LinearSVR(C=1)
pipeline_svr = Pipeline([('scaler', scaler), ('svr', svr)])

# SVR angles
pipeline_svrangle = SVR_angle()

absent = dict(cond='present', values=[0])
unseen = dict(cond='seen_unseen', values=[0])
seen = dict(cond='seen_unseen', values=[1])


def analysis(name, include, exclude=[absent], clf=None, scorer=None,
             change=None, chance=None):
    if len(include['values']) == 2:
        clf = pipeline_svc if clf is None else clf
        scorer = scorer_auc if scorer is None else scorer
        chance = .5 if chance is None else chance
    else:
        clf = pipeline_svr if clf is None else clf
        scorer = scorer_spearman if scorer is None else scorer
        chance = 0. if chance is None else chance
    return dict(name=name, include=include, exclude=exclude, clf=clf,
                chance=chance, scorer=scorer)


angles = angle2circle([15, 45, 75, 105, 135, 165])
analyses = (
    analysis('s_presence', dict(cond='present', values=[0, 1]), exclude=[]),
    analysis('s_targetContrast',
             dict(cond='targetContrast', values=[0, .5, .75, 1]), exclude=[]),
    analysis('s_lambda', dict(cond='lambda', values=[1, 2])),
    analysis('s_targetAngle', dict(cond='orientation_target_rad', values=angles),
             clf=pipeline_svrangle, chance=1. / 6., scorer=scorer_angle),
    analysis('s_probeAngle', dict(cond='orientation_probe_rad', values=angles),
             clf=pipeline_svrangle, chance=1. / 6., scorer=scorer_angle),
    analysis('s_tilt', dict(cond='tilt', values=[-1, 1])),
    analysis('m_responseButton', dict(cond='response_tilt', values=[-1, 1]),
             exclude=[dict(cond='response_tilt', values=[0])]),
    analysis('m_accuracy', dict(cond='correct', values=[0, 1])),  # XXX Absent?
    analysis('m_visibilities',
             dict(cond='response_visibilityCode', values=[1, 2, 3, 4])),
    analysis('m_seen', dict(cond='seen_unseen', values=[0, 1])),
)

# ###################### Define subscores #####################################
subscores = [
    dict(name='4visibilitiesPresentAll',
         contrast='4visibilitiesPresent',
         include=dict(cond='response_visibilityCode', values=[1, 2, 3, 4]),
         exclude=[absent],
         clf=pipeline_svr, chance=0,
         scorer=scorer_spearman),
    dict(name='visibilityPresentAll',
         contrast='visibilityPresent',
         include=dict(cond='seen_unseen', values=[0, 1]),
         exclude=[absent],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='presentAbsentAll',
         contrast='presentAbsent',
         include=dict(cond='present', values=[0, 1]),
         exclude=[],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='presentAbsentANDseen',
         contrast='presentAbsent',
         include=dict(cond='present', values=[0, 1]),
         exclude=[unseen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='presentAbsentANDunseen',
         contrast='presentAbsent',
         include=dict(cond='present', values=[0, 1]),
         exclude=[seen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='accuracyAll',
         contrast='accuracy',
         include=dict(cond='correct', values=[0, 1]),
         exclude=[dict(cond='correct', values=[float('NaN')])],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='accuracyANDseen',
         contrast='accuracy',
         include=dict(cond='correct', values=[0, 1]),
         exclude=[dict(cond='correct', values=[float('NaN')]), unseen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='accuracyANDunseen',
         contrast='accuracy',
         include=dict(cond='correct', values=[0, 1]),
         exclude=[dict(cond='correct', values=[float('NaN')]), seen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='lambdaAll',
         contrast='lambda',
         include=dict(cond='lambda', values=[1, 2]),
         exclude=[absent],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='lambdaANDseen',
         contrast='lambda',
         include=dict(cond='lambda', values=[1, 2]),
         exclude=[absent, unseen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='lambdaANDunseen',
         contrast='lambda',
         include=dict(cond='lambda', values=[1, 2]),
         exclude=[absent, seen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='tiltAll',
         contrast='tilt',
         include=dict(cond='tilt', values=[-1, 1]),
         exclude=[absent],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='tiltANDseen',
         contrast='tilt',
         include=dict(cond='tilt', values=[-1, 1]),
         exclude=[absent, unseen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='tiltANDunseen',
         contrast='tilt',
         include=dict(cond='tilt', values=[-1, 1]),
         exclude=[absent, seen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='responseButtonAll',
         contrast='responseButton',
         include=dict(cond='response_tilt', values=[-1, 1]),
         exclude=[dict(cond='response_tilt', values=[0])],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='responseButtonANDseen',
         contrast='responseButton',
         include=dict(cond='response_tilt', values=[-1, 1]),
         exclude=[dict(cond='response_tilt', values=[0]), unseen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='responseButtonANDunseen',
         contrast='responseButton',
         include=dict(cond='response_tilt', values=[-1, 1]),
         exclude=[dict(cond='response_tilt', values=[0]), seen],
         clf=pipeline_svc, chance=.5,
         scorer=scorer_auc),
    dict(name='targetAngleAll',
         contrast='targetAngle',
         include=dict(cond='orientation_target_rad',
                      values=angle2circle([15, 45, 75, 105, 135, 165])),
         exclude=[absent],
         clf=pipeline_svrangle, chance=1. / 6.,
         scorer=scorer_angle),
    dict(name='targetAngleANDseen',
         contrast='targetAngle',
         include=dict(cond='orientation_target_rad',
                      values=angle2circle([15, 45, 75, 105, 135, 165])),
         exclude=[absent, unseen], chance=1. / 6.,
         scorer=scorer_angle),
    dict(name='targetAngleANDunseen',
         contrast='targetAngle',
         include=dict(cond='orientation_target_rad',
                      values=angle2circle([15, 45, 75, 105, 135, 165])),
         exclude=[absent, seen], chance=1. / 6.,
         scorer=scorer_angle),
    dict(name='probeAngleAll',
         contrast='probeAngle',
         include=dict(cond='orientation_probe_rad',
                      values=angle2circle([15, 45, 75, 105, 135, 165])),
         exclude=[absent],
         clf=pipeline_svrangle, chance=1. / 6.,
         scorer=scorer_angle),
    dict(name='probeAngleANDseen',
         contrast='probeAngle',
         include=dict(cond='orientation_probe_rad',
                      values=angle2circle([15, 45, 75, 105, 135, 165])),
         exclude=[absent, unseen],
         clf=pipeline_svrangle, chance=1. / 6.,
         scorer=scorer_angle),
    dict(name='probeAngleANDunseen',
         contrast='probeAngle',
         include=dict(cond='orientation_probe_rad',
                      values=angle2circle([15, 45, 75, 105, 135, 165])),
         exclude=[absent, seen],
         clf=pipeline_svrangle, chance=1. / 6.,
         scorer=scorer_angle),
    dict(name='targetContrastAll',
         contrast='targetContrast',
         include=dict(cond='targetContrast', values=[0, .5, .75, 1]),
         exclude=[],
         clf=pipeline_svr, chance=0.,
         scorer=scorer_spearman),
    dict(name='targetContrastANDseen',
         contrast='targetContrast',
         include=dict(cond='targetContrast', values=[0, .5, .75, 1]),
         exclude=[unseen],
         clf=pipeline_svr, chance=0.,
         scorer=scorer_spearman),
    dict(name='targetContrastANDunseen',
         contrast='targetContrast',
         include=dict(cond='targetContrast', values=[0, .5, .75, 1]),
         exclude=[seen],
         clf=pipeline_svr, chance=0.,
         scorer=scorer_spearman),
]

# ############# Define second-order subscores #################################
subscores2 = [
    dict(name='presentAbsent:seenVSunseen',
         contrast1='presentAbsentANDseen',
         contrast2='presentAbsentANDunseen',
         include=dict(cond='present', values=[0, 1]),
         exclude=[unseen],
         clf=pipeline_svc, chance=0,
         scorer=scorer_auc),
    dict(name='accuracy:seenVSunseen',
         contrast1='accuracyANDseen',
         contrast2='accuracyANDunseen',
         include=dict(cond='correct', values=[0, 1]),
         exclude=[dict(cond='correct', values=[float('NaN')]), unseen],
         clf=pipeline_svc, chance=0,
         scorer=scorer_auc),
    dict(name='lambda:seenVSunseen',
         contrast1='lambdaANDseen',
         contrast2='lambdaANDunseen',
         include=dict(cond='lambda', values=[1, 2]),
         exclude=[absent, unseen],
         clf=pipeline_svc, chance=0,
         scorer=scorer_auc),
    dict(name='tilt:seenVSunseen',
         contrast1='tiltANDseen',
         contrast2='tiltANDunseen',
         include=dict(cond='tilt', values=[-1, 1]),
         exclude=[absent, unseen],
         clf=pipeline_svc, chance=0,
         scorer=scorer_auc),
    dict(name='responseButton:seenVSunseen',
         contrast1='responseButtonANDseen',
         contrast2='responseButtonANDseen',
         include=dict(cond='response_tilt', values=[-1, 1]),
         exclude=[dict(cond='response_tilt', values=[0]), unseen],
         clf=pipeline_svc, chance=0,
         scorer=scorer_auc),

]


def format_analysis(contrast):
    """This functions takes the contrasts defined for decoding  and format it
    so as to be usable by the univariate scripts

    We need to homogeneize the two types of analysis definitions
     """
    from .utils import evoked_spearman, evoked_subtract
    name = contrast['name']
    if contrast['scorer'] == scorer_spearman:
        operator = evoked_spearman
    elif contrast['scorer'] == scorer_auc:
        operator = evoked_subtract
    elif contrast['scorer'] == scorer_angle:
        # TODO evoked_vtest
        return
    # exclude
    exclude = dict()
    for exclude_ in contrast['exclude']:
        cond = exclude_['cond']
        exclude[cond] = exclude_['values']

    # include
    conditions = list()
    cond = contrast['include']['cond']
    for value in contrast['include']['values']:
        include_ = dict()
        include_[cond] = value
        conditions.append(dict(name=cond + str(value), include=include_,
                               exclude=exclude))
    analysis = dict(name=name, operator=operator, conditions=conditions)
    return analysis
