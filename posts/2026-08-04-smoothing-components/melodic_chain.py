"""MELODIC's model-order selection, in numpy.

A reimplementation of the chain FSL's MELODIC uses to decide how many
components to extract:

    eigenspectrum -> adj_eigspec -> Feta -> ppca_est -> ppca_select

The originals are `adj_eigspec`, `Feta`, `ppca_est` and `ppca_select` in
`melhlprfns.cc`, and `est_resels` in `meldata.cc`. This port is a trimmed copy
of the harness in <https://github.com/psadil/gigica>, which is checked
count-for-count against `fsl-melodic 2601`; the model orders it returns on the
data in this post match the binary's (see the post for the comparison).

Only what the post needs is here. The one addition to MELODIC's own interface
is `discount`, which sets the sample-size ratio `r = N / n_eff` directly
instead of computing it as `2.5 * resels` -- the post needs to vary that ratio
on its own, which no MELODIC flag allows.
"""

from __future__ import annotations

import numpy as np
from scipy.special import gammaln

# MELODIC clamps the noise reference away from zero before dividing by it.
CIRCLE_LAW_FLOOR = 5e-9

CRITERIA = ["lap", "bic", "mdl", "rrn", "aic"]

N_BOOT = 4000  # bootstrap resamples behind every interval in the post


# --------------------------------------------------------------------------
# The noise reference
# --------------------------------------------------------------------------


def feta(n1: int, n2: int) -> np.ndarray:
    """Expected noise eigenvalue at each rank, descending (MELODIC's `Feta`).

    The Marchenko-Pastur density at aspect ratio ``nu = n1 / n2``, integrated
    on a grid and inverted to give an eigenvalue per rank. ``nu`` alone fixes
    the bulk edges ``(1 +/- sqrt(nu))**2``, which is the whole point: hand it a
    different ``n2`` and the reference moves, whatever the data did.
    """
    res = np.zeros(n1)
    if n1 == 0 or n2 == 0:
        return res
    nu = n1 / n2
    bm = (1 - np.sqrt(nu)) ** 2
    bp = (1 + np.sqrt(nu)) ** 2

    n_eta = 30 * n1
    eta_step = (1.1 * bp - 0.9 * bm) / n_eta
    eta = 0.9 * bm + eta_step * np.arange(1, n_eta + 1)

    n_teta = 10 * n1
    teta_step = (bp - bm) / n_teta
    teta_raw = teta_step * np.arange(1, n_teta + 1)
    inner = teta_raw * (bp - bm - teta_raw)
    dens = np.sqrt(np.maximum(inner, 0.0)) / (2 * np.pi * nu * (teta_raw + bm))
    teta = teta_raw + bm

    claw = np.empty(n_eta)
    acc, j = 0.0, 0
    for i in range(n_eta):
        while j < n_teta and teta[j] < eta[i]:
            acc += dens[j]
            j += 1
        claw[i] = max(n1 * (1 - teta_step * acc), 0.0)

    fl = np.floor(claw)
    for i in range(n_eta - 1):
        if fl[i] > fl[i + 1] and fl[i] >= 1:
            idx = int(fl[i])
            if idx <= n1:
                res[idx - 1] = eta[i]
    return res


# The discount MELODIC applies to the sample size is `2.5 * resels`. Neither
# constant appears in either technical report. It is derivable, though: a
# covariance estimated over spatially correlated columns has an effective
# column count of N / integral(rho^2), and for a field smoothed to FWHM f the
# autocorrelation is rho(h) = exp(-|h|^2 / 4 sigma^2), so
#
#     integral rho^2 = (2 pi sigma^2)^{d/2} = (pi / (4 ln 2))^{d/2} f^d
#
# with d the number of axes `est_resels` measured. `resels` is already the
# product of the per-axis FWHM, so the discount is a constant times it.
DISCOUNT_PER_RESEL = {2: (np.pi / (4 * np.log(2))), 3: (np.pi / (4 * np.log(2))) ** 1.5}


def effective_discount(resels: float, ndim: int = 3) -> float:
    """The discount `2.5 * resels` is trying to be.

    ``1.206 * resels`` in three dimensions, ``1.133 * resels`` in two.
    """
    return float(DISCOUNT_PER_RESEL[ndim] * resels)


# --------------------------------------------------------------------------
# Spatial smoothness
# --------------------------------------------------------------------------


def est_resels(vol, mask=None) -> float:
    """Spatial smoothness in resels, ported from `MelodicData::est_resels`.

    ``vol`` is ``(nx, ny, nz, nt)``. Standardizes each in-mask voxel's time
    course, converts the lag-one spatial autocorrelation along each axis into a
    Gaussian-kernel FWHM, and multiplies the three -- the resel volume of
    random field theory, in voxel units.

    Note that the product is always three-dimensional, whatever the data look
    like. An axis with no smoothness contributes about 0.42, not 1.
    """
    nx, ny, nz, _ = vol.shape
    if mask is None:
        mask = np.ones((nx, ny, nz), dtype=bool)
    sd = vol.std(axis=3, ddof=1)
    usable = mask & (sd > 0)
    z = np.zeros_like(vol)
    np.divide(
        vol - vol.mean(axis=3, keepdims=True),
        sd[..., None],
        out=z,
        where=usable[..., None],
    )

    use_z = nz > 1
    ss, s2 = np.zeros(3), np.zeros(3)
    for ax, (a, b) in enumerate(
        [(z[1:, 1:, :], z[:-1, 1:, :]), (z[1:, 1:, :], z[1:, :-1, :])]
    ):
        m = usable[1:, 1:, :] & (usable[:-1, 1:, :] if ax == 0 else usable[1:, :-1, :])
        ss[ax] = (a * b)[m].sum()
        s2[ax] = 0.5 * ((a**2)[m].sum() + (b**2)[m].sum())
    if use_z:
        a, b = z[:, :, 1:], z[:, :, :-1]
        m = usable[:, :, 1:] & usable[:, :, :-1]
        ss[2] = (a * b)[m].sum()
        s2[2] = 0.5 * ((a**2)[m].sum() + (b**2)[m].sum())

    fwhm = np.ones(3)
    for ax in range(3 if use_z else 2):
        if s2[ax] <= 0:
            return 1.0
        sm = min(ss[ax], 0.99999 * s2[ax])
        ratio = abs(sm / s2[ax])
        if ratio <= 0:
            return 1.0
        sigsq = -1.0 / (4.0 * np.log(ratio))
        if not np.isfinite(sigsq) or sigsq <= 0:
            return 1.0
        fwhm[ax] = np.sqrt(8 * np.log(2) * sigsq)
    r = fwhm[0] * fwhm[1] * (fwhm[2] if use_z else 1.0)
    return float(r) if np.isfinite(r) and r > 0 else 1.0


def axis_fwhm(vol, mask=None) -> np.ndarray:
    """The per-axis FWHM `est_resels` multiplies together.

    Same arithmetic as :func:`est_resels`, reported per axis instead of as a
    product, so an unsmoothed axis's contribution is visible on its own.
    """
    nx, ny, nz, _ = vol.shape
    if mask is None:
        mask = np.ones((nx, ny, nz), dtype=bool)
    sd = vol.std(axis=3, ddof=1)
    usable = mask & (sd > 0)
    z = np.zeros_like(vol)
    np.divide(
        vol - vol.mean(axis=3, keepdims=True),
        sd[..., None],
        out=z,
        where=usable[..., None],
    )

    c = z[1:, 1:, 1:]
    keep = usable[1:, 1:, 1:]
    out = []
    for nb, km in (
        (z[:-1, 1:, 1:], usable[:-1, 1:, 1:]),
        (z[1:, :-1, 1:], usable[1:, :-1, 1:]),
        (z[1:, 1:, :-1], usable[1:, 1:, :-1]),
    ):
        m = keep & km
        ss = float((c * nb)[m].sum())
        s2 = float(0.5 * ((c**2)[m].sum() + (nb**2)[m].sum()))
        out.append(np.sqrt(8 * np.log(2) * (-1.0 / (4.0 * np.log(abs(ss / s2))))))
    return np.array(out)


# --------------------------------------------------------------------------
# The chain
# --------------------------------------------------------------------------


def adj_eigspec(
    evals,
    n_features,
    resels,
    *,
    drop_two=True,
    use_resels=True,
    ceiling=0.98,
    discount=None,
):
    """`adj_eigspec`. ``evals`` ascending.

    Builds the noise reference at the *discounted* sample size and divides the
    observed eigenvalues -- which still come from all ``n_features`` columns --
    by it, then re-sorts. When the two sample sizes disagree the quotient is
    sloped rather than flat, and that slope is what the criterion counts.

    ``discount`` sets ``r = n_features / n_eff`` directly, in place of
    MELODIC's ``2.5 * resels``. ``discount=1.0`` means no discount, which is
    the truth for data with independent voxels.
    """
    kept = evals[2:][::-1] if drop_two else evals[::-1]
    d = len(kept)
    if d == 0:
        return None

    if discount is not None:
        n_eff = max(int(n_features / discount), 1)
    elif use_resels:
        n_eff = max(int(n_features / (2.5 * resels)), 1)
    else:
        n_eff = max(n_features, 1)
    cl = np.maximum(feta(d, n_eff), CIRCLE_LAW_FLOOR)

    total = kept.sum()
    perc = np.cumsum(kept / total) if total else np.zeros(d)
    adjusted = np.sort(kept / cl)[::-1]

    max_ev = 1
    for i in range(d - 1):
        if perc[i] < ceiling <= perc[i + 1]:
            max_ev = i + 1
    if max_ev < 3:
        max_ev = d // 2
    max_ev = int(np.clip(max_ev, 1, d))

    return {
        "candidates": np.abs(adjusted[:max_ev]),
        "max_ev": max_ev,
        "percent": perc,
        "n_eff": n_eff,
        "reference": cl,
        "ratio": np.sort(kept / cl)[::-1],
    }


def ppca_est(ev, n):
    """`ppca_est`. ``ev`` positive and descending.

    Returns ``[ev, lap, bic, mdl, rrn, aic]`` -- the evidence curve for each of
    MELODIC's model-order criteria, evaluated at every candidate rank.
    """
    d = len(ev)
    if d == 0:
        return None
    nf, df = float(n), float(d)
    log_lambda = np.log(ev)
    k = np.arange(1, d + 1, dtype=float)
    m = df * k - 0.5 * k * (k + 1)

    loggam = np.cumsum(gammaln(0.5 * (df - np.arange(d))))
    half_log_pi = np.cumsum(0.5 * np.log(np.pi) * (df - np.arange(d)))
    l_prob_u = -np.log(2) * k + loggam - half_log_pi

    tail = ev.sum() - np.cumsum(ev)
    tail[-1] = 0.95 * ev[-1]
    tail_log = log_lambda.sum() - np.cumsum(log_lambda)
    tail_log[-1] = log_lambda[-1]

    disc = df - k
    disc[-1] = 1.0
    noise_var = np.maximum(tail / disc, 0.01)
    disc = np.maximum(disc, 0.01)
    tail = np.maximum(tail, 0.01)

    l_nu = -nf / 2 * (df - k) * np.log(noise_var)
    l_nu[-1] = 0.0
    l_lam = -(nf / 2) * np.cumsum(log_lambda)
    l_lhood = tail_log / disc - np.log(tail / disc)

    gap, inv = np.zeros(d), np.zeros(d)
    for i in range(d):
        j = np.arange(i + 1, d)
        if len(j):
            g = ev[i] - ev[j]
            gap[i] = np.log(g[g > 0]).sum()
            v = 1.0 / noise_var[j] - 1.0 / ev[i]
            inv[i] = np.log(v[v > 0]).sum()
    l_az = np.cumsum(gap) + np.cumsum(inv)

    ln_n = np.log(nf)
    lap = (
        l_prob_u
        + l_nu
        + l_az
        + l_lam
        + 0.5 * np.log(2 * np.pi) * (m + k)
        - 0.5 * ln_n * k
    )
    bic = l_lam + l_nu - 0.5 * ln_n * (m + k)
    rrn = -0.5 * nf * k * np.log(np.cumsum(ev) / k) + l_nu
    aic = -(-2 * nf * disc * l_lhood + 2 * (1 + df * k + 0.5 * (k - 1)))
    mdl = -(-nf * disc * l_lhood + 0.5 * (1 + df * k + 0.5 * (k - 1)) * ln_n)
    return [ev, lap, bic, mdl, rrn, aic]


def _minmax(v):
    lo, hi = v.min(), v.max()
    return (v - lo) / (hi - lo) if hi > lo else np.zeros_like(v)


def ppca_select(curves, max_ev, which="lap"):
    """`ppca_select`. Walks up while the normalized curve is still rising."""
    norm = [_minmax(c) for c in curves]
    d = len(curves[0])
    est = []
    for col in norm[1:]:
        slot, i = 1, 0
        while i + 1 < d - 1 and col[i] < col[i + 1] and i + 1 < max_ev:
            slot, i = i + 2, i + 1
        est.append(slot)

    if which in CRITERIA:
        return est[CRITERIA.index(which)], est
    if which == "mean":
        return int(sum(est) / 5), est
    if which == "median":
        return int(np.sort(est)[2]), est
    if which == "aut":
        perc = np.cumsum(norm[0] / norm[0].sum()) if norm[0].sum() else np.zeros(d)
        lap_e, bic_e = est[0], est[1]
        if bic_e < lap_e and perc[max(bic_e - 1, 0)] > 0.8:
            return bic_e, est
        return lap_e, est
    raise ValueError(which)


def estimate(X, resels=1.0, which="lap", **kw):
    """The full chain on a ``(n_timepoints, n_voxels)`` matrix."""
    _, n = X.shape
    Xc = X - X.mean(axis=0, keepdims=True)
    evals = np.sort(np.linalg.eigvalsh(np.cov(Xc, bias=True)))
    return order_from_evals(evals, n, resels, which, **kw)


def order_from_evals(evals, n, resels=1.0, which="lap", **kw):
    """:func:`estimate` when the eigenvalues are already in hand, ascending.

    Sweeping ``discount`` re-scores one spectrum, so the covariance -- the
    expensive part -- is computed once and reused.
    """
    spec = adj_eigspec(
        evals,
        n,
        resels,
        drop_two=kw.pop("drop_two", True),
        use_resels=kw.pop("use_resels", True),
        ceiling=kw.pop("ceiling", 0.98),
        discount=kw.pop("discount", None),
    )
    curves = ppca_est(spec["candidates"], spec["n_eff"])
    dim, est = ppca_select(curves, spec["max_ev"], which)
    return int(np.clip(dim, 1, len(evals))), {
        "max_ev": spec["max_ev"],
        "n_eff": spec["n_eff"],
        "estimators": est,
    }


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def boot_ci(values, stat=np.median, level=0.95, seed=0):
    """Bootstrap percentile interval for ``stat`` over ``values``."""
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, v.size, size=(N_BOOT, v.size))
    boot = stat(v[draws], axis=1)
    a = (1 - level) / 2
    return float(stat(v)), float(np.quantile(boot, a)), float(np.quantile(boot, 1 - a))
