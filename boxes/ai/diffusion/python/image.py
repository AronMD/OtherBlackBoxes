import torch
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

model_id = "stabilityai/stable-diffusion-2-1"

# Use the Euler scheduler here instead
scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")

## GPU
#pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, revision="fp16", torch_dtype=torch.float16)
#pipe = pipe.to("cuda")

# CPU
pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, revision="fp16", torch_dtype=torch.float32)
pipe = pipe.to("cpu")

# Something
pipe.enable_attention_slicing()

# Set prompt
prompt = "hallmark christmas card style image of two kids dressed for winter weather in a snow storm"

# Set height and width based on UNet size and VAE scale factor
# - pipe.unet.config.sample_size = 64 / 96
# - pipe.vae_scale_factor = 8
#height = 512
#width = 512
height = 768
width = 768

# Check inputs. Raise error if not correct
pipe.check_inputs(prompt, height, width, 1)

# Define call parameters
batch_size = 1
device = pipe._execution_device
guidance_scale = 9 # greater than 1 means do classifier free guidance
do_classifier_free_guidance = True

# Encode input prompt
num_images_per_prompt = 1
negative_prompt = None
text_embeddings = pipe._encode_prompt(prompt, device, num_images_per_prompt, do_classifier_free_guidance, negative_prompt)

# Prepare timesteps
num_inference_steps = 50
strength = 0.75
pipe.scheduler.set_timesteps(num_inference_steps, device=device)

# Adjust timesteps to start later in the denoising
offset = pipe.scheduler.config.get("steps_offset", 0)
init_timestep = int(num_inference_steps * strength) + offset
init_timestep = min(init_timestep, num_inference_steps)
t_start = max(num_inference_steps - init_timestep + offset, 0)
timesteps = pipe.scheduler.timesteps[t_start:]
num_inference_steps = num_inference_steps - t_start
first_latent_timestep = timesteps[:1]

# Prepare latent variables (random initialize)
generator = None
latents = None
num_channels_latents = pipe.unet.in_channels

# Load starting image and encode
with torch.no_grad():
    image = Image.open("/home/kampff/Downloads/xmas.jpg")
    w, h = image.size
    w, h = map(lambda x: x - x % 32, (w, h))  # resize to integer multiple of 32
    #image = image.resize((w, h), resample=PIL_INTERPOLATION["lanczos"])
    image = np.array(image).astype(np.float32) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)
    image = 2.0 * image - 1.0
    image = image.to(device=device, dtype=torch.float32)
    dist = pipe.vae.encode(image).latent_dist
    latents = dist.sample(generator=generator)
    latents = 0.18215 * latents
    # Add noise to latents
    noise = torch.randn(latents.shape, generator=generator, device=device, dtype=torch.float32)
    latents = pipe.scheduler.add_noise(latents, noise, first_latent_timestep)

# Was adding too much noise...bu...divided by 8...for no reason

# Visualize initial latents
plt.subplot(2,2,1)
plt.imshow(latents[0, 0, :, :])
plt.subplot(2,2,2)
plt.imshow(latents[0, 1, :, :])
plt.subplot(2,2,3)
plt.imshow(latents[0, 2, :, :])
plt.subplot(2,2,4)
plt.imshow(latents[0, 3, :, :])
plt.show()

# Decode random latents
with torch.no_grad():
    image = pipe.decode_latents(latents)

# Visualize initial decoded latents
plt.imshow(image[0,:,:,:])
plt.show()

# Prepare extra step kwargs
eta = 0.0
extra_step_kwargs = pipe.prepare_extra_step_kwargs(generator, eta)

# Denoising loop
num_warmup_steps = len(timesteps) - num_inference_steps * pipe.scheduler.order
with torch.no_grad():
    for i, t in enumerate(timesteps):
        # expand the latents if we are doing classifier free guidance
        latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
        latent_model_input = pipe.scheduler.scale_model_input(latent_model_input, t)

        # predict the noise residual
        # Inputs:
        #  - latents (64x64 or 96x96), t (timestep), hidden_states ()
        noise_pred = pipe.unet(latent_model_input, t, encoder_hidden_states=text_embeddings).sample

        # perform guidance
        if do_classifier_free_guidance:
#        if False:
            noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
            # UNet precicted noise in text and image embedding....the predicted noise is stepped by the difference between
            #   them scaled by the "guidance_scale" factor
            noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

            # compute the previous noisy sample x_t -> x_t-1
            # Steps the latents...impements diffusion algorithm (subtract oredicited noise...basically...depends a bit on size of timestep...I guess to make it stable...)
            # - moves latemts through atent space towards the manifold with valid images...bu...guided by the text prompt...
        latents = pipe.scheduler.step(noise_pred, t, latents, **extra_step_kwargs).prev_sample
        print(latents)

        # Decode current latents
        image = pipe.decode_latents(latents)

        # Save current image
        image = pipe.numpy_to_pil(image)
        image[0].save("/home/kampff/Downloads/steps/{0}.png".format(i))

        # Report progress
        print("Iteration {0}...".format(i))

# Report Done
print("Done")

#FIN