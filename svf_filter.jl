using Images, ImageFiltering, FileIO, ArgParse

"""
    svf(image, radius, epsilon)

Sub-Window Variance Filter for edge-preserving smoothing.

# Arguments
- `image`: Input image (Float32 or Float64), normalized to [0, 1]
- `radius`: Radius of the local window
- `epsilon`: Variance threshold. Higher values preserve stronger edges

# Returns
- `base`: Smoothed image (edge-preserving)
- `variance_map`: Local variance map used for filtering
"""
function svf(image::AbstractArray{T,2}, radius::Int, epsilon::Float64) where T<:AbstractFloat
    kernel_size = 2 * radius + 1
    
    # Compute local mean and variance using box filter
    mean_local = imfilter(image, Kernel.box((kernel_size, kernel_size)))
    mean_sq = imfilter(image.^2, Kernel.box((kernel_size, kernel_size)))
    variance = mean_sq - mean_local.^2
    
    # Compute adaptive smoothing weight
    weight = variance ./ (variance .+ epsilon)
    base = weight .* image .+ (1 .- weight) .* mean_local
    
    return base, variance
end

function svf(image::AbstractArray{T,3}, radius::Int, epsilon::Float64) where T<:AbstractFloat
    base = similar(image)
    variance_map = similar(image)
    
    for c in 1:size(image, 3)
        base[:, :, c], variance_map[:, :, c] = svf(image[:, :, c], radius, epsilon)
    end
    
    return base, variance_map
end

"""
    svf_enhance(image_path, radius, epsilon, m_amp, f_amp)

Multiscale image enhancement using Sub-Window Variance Filter.

# Arguments
- `image_path`: Path to the input image
- `radius`: Base filter radius for SVF (default: 3)
- `epsilon`: Variance threshold for edge preservation (default: 0.025)
- `m_amp`: Amplification factor for medium details (default: 2.0)
- `f_amp`: Amplification factor for fine details (default: 3.0)

# Returns
- `result`: Enhanced image (Float64, range [0, 1])
"""
function svf_enhance(
    image_path::String;
    radius::Int = 3,
    epsilon::Float64 = 0.025,
    m_amp::Float64 = 2.0,
    f_amp::Float64 = 3.0
)
    # Load and normalize image
    img = load(image_path)
    img_float = Float64.(channelview(img))
    
    # Convert from channel-first to channel-last format for consistency with Python version
    if ndims(img_float) == 3
        img_float = permutedims(img_float, (2, 3, 1))
    else
        img_float = reshape(img_float, size(img_float)..., 1)
    end
    
    # 1. Fine detail decomposition
    base0, _ = svf(img_float, radius, epsilon)
    detail_f = img_float - base0
    
    # 2. Medium detail decomposition
    base1, _ = svf(base0, radius * 4, epsilon * 2)
    detail_m = base0 - base1
    
    # 3. Reconstruct enhanced image
    result = base1 + m_amp .* detail_m + f_amp .* detail_f
    result = clamp.(result, 0.0, 1.0)
    
    return result
end

function save_enhanced_image(result::Array{Float64,3}, output_path::String)
    # Convert back to channel-first format and proper image type
    if size(result, 3) == 3
        result_permuted = permutedims(result, (3, 1, 2))
        img_result = colorview(RGB, result_permuted)
    else
        result_reshaped = dropdims(result, dims=3)
        img_result = colorview(Gray, result_reshaped')
    end
    
    save(output_path, img_result)
end

function main()
    parser = ArgParseSettings(description="Image Enhancement using Sub-Window Variance Filter (SVF)")
    
    @add_arg_table! parser begin
        "image_path"
            help = "Path to input image (PNG/JPG)"
            required = true
        "--radius"
            help = "Base SVF radius"
            arg_type = Int
            default = 3
        "--epsilon"
            help = "Variance threshold"
            arg_type = Float64
            default = 0.025
        "--m_amp"
            help = "Medium detail amplification"
            arg_type = Float64
            default = 2.0
        "--f_amp"
            help = "Fine detail amplification"
            arg_type = Float64
            default = 3.0
        "--output"
            help = "Output filename"
            default = "enhanced_result.png"
    end
    
    args = parse_args(parser)
    
    try
        enhanced = svf_enhance(
            args["image_path"],
            radius = args["radius"],
            epsilon = args["epsilon"],
            m_amp = args["m_amp"],
            f_amp = args["f_amp"]
        )
        
        save_enhanced_image(enhanced, args["output"])
        println("Saved enhanced image to $(args["output"])")
        
    catch e
        if isa(e, SystemError) || isa(e, ArgumentError)
            println("Error: Could not load image: $(args["image_path"])")
        else
            rethrow(e)
        end
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
