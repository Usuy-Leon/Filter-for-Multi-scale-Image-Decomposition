"""
svf_filter.py


-------------------------------------------------------
Usage Example
-------------------------------------------------------
    from svf_filter import svf
    import cv2

    img = cv2.imread("cat.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype("float64") / 255.0

    A, result = svf(img, r=3, e=0.025)

    cv2.imwrite("cat_svf.png", (result[:, :, ::-1] * 255).astype("uint8"))


 """

import numpy as np
from scipy.ndimage import uniform_filter


def _integral_mean(image: np.ndarray, size: int) -> np.ndarray:

    return uniform_filter(image, size=size, mode="reflect")


def svf(s: np.ndarray, r: int, e: float):
    """.

    Parameters
    ----------
    s : np.ndarray
        Input image (float64), range [0, 1].
        Can be grayscale (H×W) or color (H×W×3).
    r : int
        Filter radius (in pixels).
    e : float
        Epsilon, a small threshold variance value of a clear edge to preserve.

    Returns
    -------
    A : np.ndarray
        Per-pixel preservation factor (float64, H×W).
    SVF : np.ndarray
        Filtered (edge-preserving smoothed) image (float64, same shape as `s`).
    """
    if s.ndim == 2:
        s = s[:, :, np.newaxis]

    h, w, ch = s.shape
    pad = r
    s_pad = np.pad(s, ((pad, pad), (pad, pad), (0, 0)), mode="symmetric")

    kWin = 2 * r + 1  # full window size

    # Compute local mean and variance for full window
    mean_W = _integral_mean(s_pad, kWin)[pad:-pad, pad:-pad, :]
    mean_sq_W = _integral_mean(s_pad ** 2, kWin)[pad:-pad, pad:-pad, :]
    var_W = mean_sq_W - mean_W ** 2

    # --- Sub-windows (A, B, C, D) ---
    kw = r + 1  # subwindow size (approx half)
    var_A = _integral_mean(s_pad ** 2, kw)[pad:-pad, pad:-pad, :] - _integral_mean(s_pad, kw)[pad:-pad, pad:-pad, :] ** 2
    var_B = np.roll(var_A, shift=(r // 2, 0), axis=(0, 1))
    var_C = np.roll(var_A, shift=(0, r // 2), axis=(0, 1))
    var_D = np.roll(var_A, shift=(r // 2, r // 2), axis=(0, 1))

    # Combine local variances
    maxV = np.maximum.reduce([var_A, var_B, var_C, var_D, var_W])
    minV = np.minimum.reduce([var_A, var_B, var_C, var_D])

    Ak = np.minimum(1.0, maxV / (minV + e))

    # Collapse across color channels (if RGB)
    if ch > 1:
        Ak = np.max(Ak, axis=2)
    else:
        Ak = Ak[:, :, 0]

    # Compute per-pixel Bk term (local mean blend)
    Bk = np.zeros_like(s)
    for i in range(ch):
        Bk[:, :, i] = (1 - Ak) * mean_W[:, :, i]

    # Second smoothing stage (per-pixel A and B)
    A_mean = _integral_mean(Ak, kWin)
    B_mean = np.zeros_like(s)
    for i in range(ch):
        B_mean[:, :, i] = _integral_mean(Bk[:, :, i], kWin)

    # Final filter
    SVF = np.zeros_like(s)
    for i in range(ch):
        SVF[:, :, i] = A_mean * s[:, :, i] + B_mean[:, :, i]

    if SVF.shape[2] == 1:
        SVF = SVF[:, :, 0]

    return A_mean, SVF


