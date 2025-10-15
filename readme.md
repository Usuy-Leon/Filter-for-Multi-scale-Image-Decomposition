

<div align="center">
<div style="background-color: #1a1b1e; padding: 20px; border-radius: 8px; margin-bottom: 20px;">

# Multi Scale image Decomposition

I forked this repo initially ment for MATLAB to write it again in python, Julia and with luck even make it a ImageJ extension. Is a very interesting Digital Filter. In short, **It smooths an image while preserving strong edges.**


</div>

<div align="left">
 
- If a region has low variance, it’s likely smooth (sky, wall, etc.), so it gets blurred more.

- If a region has high variance (edges, textures), it’s likely important detail, so it’s preserved.


## Sub-window Variance Filter 

 First descoription of this filter is in the article [_Multi-scale Image Decomposition Using a Local Statistical Edge Model_](https://arxiv.org/abs/2105.01951). 
 For details go check the paper.
 
</div>
<div align="center">

<img src="cat.png" alt="Input" width=256/> | <img src="cat_A.png" alt="Input" width=256/> | <img src="cat_SVF.png" alt="Input" width=256/> 
:---: | :---: | :---:  
*Input* | *Per-pixel preservation* (A) | *Filtered* (result)

It decomposes an image into coarse (base), medium, and fine detail layers, then enhances those details using amplification factors.

<img src="cat_Enhanced.png" alt="Input" width=256/> |
:---: |
*Both medium and fine details enhanced* |

</div>

<div align="left">
 
## Python Implementation

1. Radius (r)

Think of it like blur size or scale of smoothing.

2. Epsilon (e)

Defines the variance threshold to decide what is an "edge" versus a "flat area".

| Parameter | Symbol    | Meaning                                               | Effect                                                                          |
| --------- | --------- | ----------------------------------------------------- | ------------------------------------------------------------------------------- |
| `r`       | (radius)  | Size of the local analysis window (in pixels).        | Controls how much area around each pixel is considered for variance estimation. |
| `e`       | (epsilon) | Threshold variance defining what counts as an “edge.” | Controls how strongly edges are preserved.                                      |

##  Workflow

#### Start simple:
Try the defaults: radius=3, epsilon=0.025, m_amp=2.0, f_amp=3.0.

#### Adjust smoothness:
Increase radius for more smoothing, decrease for sharper details.

#### Tune edge sensitivity:
- If edges look too soft → decrease epsilon.
- If too harsh or noisy → increase epsilon.

#### Control enhancement strength:

> m_amp: affects edges and contrast.
>
> f_amp: affects micro-textures.
> Start from 1.0 (neutral) and raise gradually.

#### Avoid artifacts:

- Don’t set both amplifications too high (>4).


## Julia Implementation
Key differences and improvements in the Julia version:

##### Performance benefits:
  - Julia's JIT compilation can make this code faster than the Python version
  - Better memory management and vectorization


To use this code:
```julia

using Pkg
Pkg.add(["Images", "ImageFiltering", "FileIO", "ArgParse"])

```
#### Run the script using bash: 

```bash

julia svf_enhance.jl input_image.jpg --radius 3 --epsilon 0.025 --m_amp 2.0 --f_amp 3.0 --output enhanced.png
```
The Julia version maintains the same functionality while leveraging Julia's performance characteristics and type system. 

</div>
