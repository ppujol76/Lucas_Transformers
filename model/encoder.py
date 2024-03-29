from einops import rearrange
import torchvision.models as models
import torch.nn as nn


class Encoder_VGG16(nn.Module):
    def __init__(self):
        super(Encoder_VGG16, self).__init__()

        print("Extracting feature vectors from the image")
        pretrained_model = models.vgg16(pretrained=True)
        self.conv_base = pretrained_model.features

        # Freeze All layers as they will be used for inference
        for param in self.conv_base.parameters():
            param.requires_grad = False

    def forward(self, x):
        # For an image size of (224x224) --> x dims (batch_size, 3, 244 , 244)
        features = self.conv_base(x)
        # For an image size of (224x224) --> features dims (batch_size, feat_maps=512, H=7 , W=7)
        features = rearrange(
            features,
            'batch_size feature_maps height width -> batch_size (height width) feature_maps',
            height=7,
            width=7,
            feature_maps=512
        )
        # For an image size of (224x224) --> features dims (batch_size, 7x7=49, 512)
        return features


class Encoder_ResNet50(nn.Module):
    def __init__(self):
        super(Encoder_ResNet50, self).__init__()
        pretrained_model = models.resnet50(pretrained=True)

        modules = list(pretrained_model.children())[:-2]
        self.conv_base = nn.Sequential(*modules)

        # Freeze All layers as they will be used for inference
        for param in self.conv_base.parameters():
            param.requires_grad = False

        # Flaten layer that flatten the dimensions 2 and 3 (H and W of the feature maps respectively)
        self.flat = nn.Flatten(2, 3)

    def forward(self, x):
        # For an image size of (224x224) --> x dims (batch_size, 3, H=224 , W=224)
        features = self.conv_base(x)
        # For an image size of (224x224) --> features dims (batch_size, feat_maps=2048, H=7 , W=7)
        features = self.flat(features)
        # For an image size of (224x224) --> features dims  (batch_size, feat_maps=2048, 7x7=49)
        return features


class Encoder_DenseNet(nn.Module):
    def __init__(self):
        super(Encoder_DenseNet, self).__init__()
        pretrained_model = models.densenet161(pretrained=True)
        self.conv_base = pretrained_model.features

        # Freeze All layers as they will be used for inference
        for param in self.conv_base.parameters():
            param.requires_grad = False

        # Flaten layer that flatten the dimensions 2 and 3 (H and W of the feature maps respectively)
        self.flat = nn.Flatten(2, 3)

        # We apply here a ReLU
        self.relu = nn.ReLU()

    def forward(self, x):
        # (batch_size, feat_maps=512, H=7 , W=7) or (batch_size, 512, 14 , 14)
        features = self.conv_base(x)
        # (batch_size, 512, 7x7=49) or (batch_size, 512, 14x14=196)
        features = self.flat(features)
        # (batch_size, 49, 512) or (batch_size, 196, 512)
        return self.relu(features)
