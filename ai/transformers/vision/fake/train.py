import os
import numpy as np
import matplotlib.pyplot as plt
import torch
from torchvision import transforms
from torchsummary import summary
import cv2
from torch.nn.utils import clip_grad_norm_

# Locals libs
import model
import dataset
import loss
import optimizer

# Reimport
import importlib
importlib.reload(dataset)
importlib.reload(model)
importlib.reload(loss)
importlib.reload(optimizer)

# Get user name
username = os.getlogin()

# Specify paths
repo_path = '/home/' + username + '/NoBlackBoxes/repos/OtherBlackBoxes'
box_path = repo_path + '/boxes/ai/transformers/vision/fake'
output_path = box_path + '/_tmp'

# Specify transforms for inputs
preprocess = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Create datasets
train_dataset = dataset.custom(num_fakes=5000, transform=preprocess)
test_dataset = dataset.custom(num_fakes=1000, transform=preprocess)

# Create data loaders
train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=100, shuffle=True)
test_dataloader = torch.utils.data.DataLoader(test_dataset, batch_size=100, shuffle=True)

# Inspect dataset?
inspect = False
if inspect:
    train_features, train_targets = next(iter(train_dataloader))
    for i in range(9):
        plt.subplot(3,3,i+1)
        feature = train_features[i]
        target = np.squeeze(train_targets[i].numpy())
        feature = (feature + 2.0) / 4.0
        image = np.transpose(feature, (1,2,0))
        heatmap = cv2.resize(target, (224,224))
        plt.imshow(image, alpha=0.75)
        plt.imshow(heatmap, alpha=0.5)
    plt.show()

# Instantiate model
importlib.reload(model)
custom_model = model.custom()

# Set loss function
custom_loss = loss.custom_loss()

# Set optimizer
adam_optimizer = torch.optim.AdamW(custom_model.parameters(), lr=0.0001, betas=(0.9, 0.999), weight_decay=0.1)

# Layer-wise learning rate decay
#lr_mult = [cfg.optimizer['paramwise_cfg']['layer_decay_rate']] * cfg.optimizer['paramwise_cfg']['num_layers']
lr_mult = [0.75] * 12
custom_optimizer = optimizer.LayerDecayOptimizer(adam_optimizer, lr_mult)

# Get cpu or gpu device for training
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using {device} device")

# Move model to device
custom_model.to(device)
summary(custom_model, (3, 224, 224))

# Define training
def train(_dataloader, _model, _loss_function, _optimizer):
    size = len(_dataloader.dataset)
    _model.train()
    for batch, (X, y) in enumerate(_dataloader):
        X, y = X.to(device), y.to(device)

        # Compute prediction error
        pred = _model(X)
        loss = _loss_function(pred, y)
        print(" - range: {0:.6f} to {1:.6f}".format(pred[0].min(), pred[0].max()))

        # Backpropagation
        _optimizer.zero_grad()
        loss.backward()
        clip_grad_norm_(_model.parameters(), max_norm=1., norm_type=2)
        _optimizer.step()

        if batch % 2 == 0:
            loss, current = loss.item(), batch * len(X)
            pixel_loss = np.sqrt(loss) * 224.0
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}], pixel_loss: {pixel_loss:>5f}")

# Define testing
def test(_dataloader, _model, _loss_function):
    size = len(_dataloader.dataset)
    num_batches = len(_dataloader)
    _model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for X, y in _dataloader:
            X, y = X.to(device), y.to(device)
            pred = _model(X)
            test_loss += _loss_function(pred, y).item()
    test_loss /= num_batches
    pixel_loss = np.sqrt(test_loss) * 224.0
    print(f"Test Error: \n Avg loss: {test_loss:>8f}, pixel_loss: {pixel_loss:>5f}\n")

# TRAIN
epochs = 250
for t in range(epochs):
    print(f"Epoch {t+1}\n-------------------------------")
    train(train_dataloader, custom_model, custom_loss, custom_optimizer)
    test(test_dataloader, custom_model, custom_loss)
print("Done!")



# ------------------------------------------------------------------------
# Display image and label.
train_features, train_targets = next(iter(test_dataloader))
print(f"Feature batch shape: {train_features.size()}")
print(f"Targets batch shape: {train_targets.size()}")

# Let's run it
train_features_gpu = train_features.to(device)
outputs = custom_model(train_features_gpu)
outputs = outputs.cpu().detach().numpy()

# Examine predictions
plt.figure()
for i in range(9):
    plt.subplot(3,3,i+1)
    feature = train_features[i]
    target = np.squeeze(train_targets[i].numpy())
    feature = (feature + 2.0) / 4.0
    image = np.transpose(feature, (1,2,0))
    target_heatmap = cv2.resize(target, (224,224))
    output = np.squeeze(outputs[i])
    predicted_heatmap = cv2.resize(output, (224,224))
    plt.imshow(image, alpha=0.75)
    plt.imshow(predicted_heatmap, alpha=0.5)
    #plt.imshow(target_heatmap, alpha=0.5)
plt.savefig(output_path + '/result.png')
# ------------------------------------------------------------------------


# Save model
torch.save(custom_model.state_dict(), output_path + '/custom.pt')


# FIN