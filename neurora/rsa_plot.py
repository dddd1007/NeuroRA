# -*- coding: utf-8 -*-

' a module for plotting the RDM '

__author__ = 'Zitong Lu'

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from nilearn import plotting
import nibabel as nib
from neurora.stuff import get_affine

def plot_rdm(rdm, rescale=False):

    if len(np.shape(rdm)) != 2:

        return None

    a, b = np.shape(rdm)

    if a != b:

        return None

    if rescale == True:

        cons = rdm.shape[0]
        vrdm = np.reshape(rdm, [cons*cons])
        svrdm = set(vrdm)
        lvrdm = list(svrdm)
        lvrdm.sort()
        maxvalue = lvrdm[-1]
        minvalue = lvrdm[1]
        for i in range(cons):
            for j in range(cons):
                if i != j:
                    rdm[i, j] = float((rdm[i, j]-minvalue)/(maxvalue-minvalue))

    plt.imshow(rdm, cmap=plt.cm.jet, clim=(0, 1))

    plt.axis("off")
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=16)
    font = {'size': 18}
    if rescale == True:
        cb.set_label("Dissimilarity (Rescaling)", fontdict=font)
    elif rescale == False:
        cb.set_label("Dissimilarity", fontdict=font)
    plt.show()

def plot_rdm_withvalue(rdm, fontsize=10):

    if len(np.shape(rdm)) != 2:

        return None

    a, b = np.shape(rdm)

    if a != b:

        return None

    plt.imshow(rdm, cmap=plt.cm.Greens, clim=(0, 1))

    plt.axis("off")

    for i in range(a):
        for j in range(b):
            text = plt.text(i, j, float('%.4f'%rdm[i, j]),
                           ha="center", va="center", color="blue", fontsize=fontsize)

    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=16)
    font = {'size': 18}
    cb.set_label("Dissimilarity", fontdict=font)

    plt.show()

def plot_corrs_by_time(corrs, labels=None, time_unit=[0, 0.1]):
    # corrs represent the correlation coefficients point-by-point, its shape :
    #       [n, ts, 2] (here 2 contains r-value and p-value) or [n, ts] (r-value)
    # label represent the conditions of RSA results, its shape : [n]
    # time_unit=[start_t, t_step]

    n = corrs.shape[0]
    ts = corrs.shape[1]

    start_t = time_unit[0]
    tstep = time_unit[1]

    end_t = start_t + ts * tstep

    x = np.arange(start_t, end_t, tstep)

    t = ts * 50

    x_soft = np.linspace(x.min(), x.max(), t)

    y_soft = np.zeros([n, t])

    for i in range(n):
        if len(corrs.shape) == 3:
            f = interp1d(x, corrs[i, :, 0], kind='cubic')
            y_soft[i] = f(x_soft)
        if len(corrs.shape) == 2:
            f = interp1d(x, corrs[i, :], kind='cubic')
            y_soft[i] = f(x_soft)

    vmax = np.max(y_soft)
    vmin = np.min(y_soft)

    if vmax <= 1/1.1:
        ymax = np.max(y_soft)*1.1
    else:
        ymax = 1

    if vmin >= 0:
        ymin = -0.1
    elif vmin < 0 and vmin > -1/1.1:
        ymin = np.min(y_soft)*1.1
    else:
        ymin = -1

    fig, ax = plt.subplots()

    for i in range(n):
        if labels:
            plt.plot(x_soft, y_soft[i], linewidth=3, label=labels[i])
        else:
            plt.plot(x_soft, y_soft[i], linewidth=3)

    plt.ylim(ymin, ymax)
    plt.ylabel("Similarity", fontsize=20)
    plt.xlabel("Time (s)", fontsize=20)
    plt.tick_params(labelsize=18)

    if labels:
        plt.legend()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.show()

def plot_corrs_hotmap(eegcorrs, chllabels=[], time_unit=[0, 0.1], lim=[0, 1], smooth=True):
    # eegcorrs represents the correlation coefficients time-by-time, its shape:
    # [N_chls, ts, 2] or [N_chls, ts], N_chls: number of channels, ts: number of time points, 2: a r-value and a p-value
    # chllabel represents the names of channels
    # time_unit=[start_t, t_step]
    # smooth represents smoothing the results or not

    nchls = eegcorrs.shape[0]
    ts = eegcorrs.shape[1]

    start_t = time_unit[0]
    tstep = time_unit[1]

    end_t = start_t + ts * tstep

    x = np.arange(start_t, end_t, tstep)

    for i in range(nchls):
        if i % 10 == 0 and i != 10:
            newlabel = str(i+1) + "st"
        elif i % 10 == 1 and i != 11:
            newlabel = str(i+1) + "nd"
        elif i % 10 == 2 and i != 12:
            newlabel = str(i+1) + "rd"
        else:
            newlabel = str(i+1) + "th"
        chllabels.append(newlabel)

    if smooth == True:

        t = ts * 50

        x_soft = np.linspace(x.min(), x.max(), t)

        y_soft = np.zeros([nchls, t])

        for i in range(nchls):
            if len(eegcorrs.shape) == 3:
                f = interp1d(x, eegcorrs[i, :, 0], kind='cubic')
                y_soft[i] = f(x_soft)
            elif len(eegcorrs.shape) == 2:
                f = interp1d(x, eegcorrs[i, :], kind='cubic')
                y_soft[i] = f(x_soft)

        rlts = y_soft

    if smooth == False:
        if len(eegcorrs.shape) == 3:
            rlts = eegcorrs[:, :, 0]
        elif len(eegcorrs.shape) == 2:
            rlts = eegcorrs

    print(rlts.shape)

    fig = plt.gcf()
    fig.set_size_inches(10, 3)

    limmin = lim[0]
    limmax = lim[1]
    plt.imshow(rlts, extent=(float(start_t*nchls/3), float(end_t*nchls/3), 0, 0.16*nchls), clim=(limmin, limmax), origin='low')

    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=16)
    font = {'size': 18}
    cb.set_label("Similarity", fontdict=font)
    xi = []
    for i in range(nchls):
        xi.append(0.16*i + 0.08)
    yi = chllabels
    plt.tick_params(labelsize=18)
    plt.yticks(xi, yi, fontsize=18)
    plt.ylabel("Channel", fontsize=20)
    plt.xlabel("Time (s)", fontsize=20)
    plt.show()

def plot_brainrsa_rlts(img, threshold=None):

    if threshold != None:

        imgarray = nib.load(img).get_data()
        affine = get_affine(img)

        sx = np.shape(imgarray)[0]
        sy = np.shape(imgarray)[1]
        sz = np.shape(imgarray)[2]

        imgarray = correct_by_threshold(imgarray, sx, sy, sz, threshold)

        img = nib.Nifti1Image(imgarray, affine)

    roi_bg = "template/ch2.nii.gz"
    print(nib.load(roi_bg))

    plotting.plot_roi(roi_img=img, bg_img=roi_bg, threshold=0, vmin=0.1, vmax=1, resampling_interpolation="continuous")

    plt.show()

#def plot_brainrsa_regions():

#def plot_brainrsa_montage():

#def plot_brainrsa_glass():



def correct_by_threshold(img, sx, sy, sz, threshold):

    nsmall = 1
    while nsmall*nsmall*nsmall < threshold:
        nsmall = nsmall + 1

    nlarge = nsmall + 2

    for i in range(sx-nlarge+1):
        for j in range(sy-nlarge+1):
            for k in range(sz-nlarge+1):

                listlarge = list(np.reshape(img[i:i+nlarge, j:j+nlarge, k:k+nlarge], [nlarge*nlarge*nlarge]))
                print(listlarge.count(0))
                if listlarge.count(0) < nlarge*nlarge*nlarge:
                    print(i, j, k)
                    print("count:"+str(listlarge.count(0)))
                    index1 = 0
                    for l in range(nlarge):
                        for m in range(nlarge):
                            if img[i + l, j + m, k] == 0:
                                index1 = index1 + 1
                            if img[i + l, j + m, k + nlarge - 1] == 0:
                                index1 = index1 + 1
                    for l in range(nlarge-1):
                        for m in range(nlarge-2):
                            if img[i + l, j, k + m] == 0:
                                index1 = index1 + 1
                            if img[i, j + l + 1, k + m] == 0:
                                index1 = index1 + 1
                            if img[i + nlarge - 1, j + l, k + m] == 0:
                                index1 = index1 + 1
                            if img[i + l + 1, j + nlarge - 1, k + m] == 0:
                                index1 = index1 + 1
                    nex = nlarge * nlarge * nlarge - nsmall * nsmall * nsmall
                    print("index1:"+str(index1))
                    if index1 == nex:
                        print("**************************")
                        unit = img[i+1:i+1+nsmall, j+1:j+1+nsmall, k+1:k+1+nsmall]
                        unit = np.reshape(unit, [nsmall*nsmall*nsmall])
                        list_internal = list(unit)
                        index2 = nsmall*nsmall*nsmall-list_internal.count(0)
                        print(index1, index2)
                        if index2 < threshold:
                            img[i+1:i+1+nsmall, j]
                            for l in range(nsmall):
                                for m in range(nsmall):
                                    for p in range(nsmall):
                                        img[i+1:i+1+nsmall, j+1:j+1+nsmall, k+1:k+1+nsmall] = np.zeros([nsmall, nsmall, nsmall])
    return img


roi_bg = "template/ch2.nii.gz"
print(nib.load(roi_bg))