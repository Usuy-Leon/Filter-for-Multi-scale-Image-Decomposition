

import numpy as np
import cv2
from scipy.ndimage import uniform_filter


def svf(image: np.ndarray, radius: int, epsilon: float):

    if image.ndim == 3:
        base = np.zeros_like(image)
        variance_map = np.zeros_like(image)
        for c in range(3):
            base[:, :, c], variance_map[:, :, c] = svf(image[:, :, c], radius, epsilon)
        return base, variance_map

    kernel_size = 2 * radius + 1

    # Compute local mean and variance
    mean = uniform_filter(image, kernel_size)
    mean_sq = uniform_filter(image ** 2, kernel_size)
    variance = mean_sq - mean ** 2

    # Compute adaptive smoothing weight
    weight = variance / (variance + epsilon)
    base = weight * image + (1 - weight) * mean

    return base, variance


def svf_enhance(
    image_path: str,
    radius: int = 3,
    epsilon: float = 0.025,
    m_amp: float = 2.0,
    f_amp: float = 3.0
) -> np.ndarray:

    # Load and normalize
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float64) / 255.0

    # 1. Fine detail decomposition
    base0, _ = svf(img, radius, epsilon)
    detail_f = img - base0

    # 2. Medium detail decomposition
    base1, _ = svf(base0, radius * 4, epsilon * 2)
    detail_m = base0 - base1

    # 3. Reconstruct enhanced image
    result = base1 + m_amp * detail_m + f_amp * detail_f
    result = np.clip(result, 0, 1)

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image Enhancement using Sub-Window Variance Filter (SVF)")
    parser.add_argument("image_path", type=str, help="Path to input image (PNG/JPG)")
    parser.add_argument("--radius", type=int, default=3, help="Base SVF radius")
    parser.add_argument("--epsilon", type=float, default=0.025, help="Variance threshold")
    parser.add_argument("--m_amp", type=float, default=2.0, help="Medium detail amplification")
    parser.add_argument("--f_amp", type=float, default=3.0, help="Fine detail amplification")
    parser.add_argument("--output", type=str, default="enhanced_result.png", help="Output filename")

    args = parser.parse_args()

    enhanced = svf_enhance(
        args.image_path,
        radius=args.radius,
        epsilon=args.epsilon,
        m_amp=args.m_amp,
        f_amp=args.f_amp
    )

    out_bgr = cv2.cvtColor((enhanced * 255).astype('uint8'), cv2.COLOR_RGB2BGR)
    cv2.imwrite(args.output, out_bgr)
    print(f"Saved enhanced image to {args.output}")
