"""Generate featured.png: an independent component fit to pure smoothed noise.

    pixi run python featured.py
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from scipy.ndimage import gaussian_filter
from sklearn.decomposition import FastICA

SHAPE, P, FWHM = (48, 48, 30), 400, 2.5

mask = np.zeros(SHAPE, dtype=bool)
mask[4:-4, 4:-4, 3:-3] = True
idx = np.flatnonzero(mask.ravel())

sig = FWHM / np.sqrt(8 * np.log(2))
vol = gaussian_filter(
    np.random.default_rng(7000).normal(size=SHAPE + (P,)), (sig, sig, sig, 0)
)
S = FastICA(n_components=5, random_state=0, max_iter=1000,
            whiten="unit-variance").fit_transform(vol.reshape(-1, P)[idx])
m = S[:, 0]
m = (m - m.mean()) / m.std()

full = np.full(SHAPE, np.nan).ravel()
full[idx] = m
sl = full.reshape(SHAPE)[:, :, SHAPE[2] // 2]

fig, ax = plt.subplots(figsize=(4, 4), dpi=160)
ax.imshow(np.where(np.abs(sl) > 2, sl, np.nan).T, origin="lower", cmap="RdBu_r",
          norm=TwoSlopeNorm(vmin=-4.5, vcenter=0, vmax=4.5))
ax.set_axis_off()
fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("featured.png", bbox_inches="tight", pad_inches=0.05,
            transparent=True)
print("wrote featured.png")
