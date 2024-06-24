import torch
import torchvision
from torch import nn


class NaturifyModelInferencer:
    def __init__(self):

        naturify_state_dict = torch.load('/home/cameron/Search_Engine/index_v1/classification_models/naturify_state_dict.pth', map_location=torch.device('cpu'))
        self.naturify_model = torchvision.models.vit_b_16()
        self.naturify_model.heads = nn.Sequential(
            nn.Linear(in_features=self.naturify_model.heads[0].in_features, out_features = 10000)
        )
        self.naturify_model.load_state_dict(naturify_state_dict)
        self.naturify_model.eval()
        # I don't know if this is nescessary
        del naturify_state_dict
        print("loaded Naturify model")

        # Load the categories
        with open("categories.json","r") as f:
            self.categories = json.load(f)

        # transform input into the Naturify model
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    # inference the Naturify model on an image, and return a list of dictionary structures containing predictions for what species the image contains
    def inference(self, image):
        image = torch.tensor(image)
        image = self.transform(image)

        # inference the model (output logits)
        out = self.naturify_model(image)

        # use softmax to convert the logits into probablities
        out = torch.softmax(out, dim=1)
        
        # find the top 5 most certain classes
        vals, idxs = torch.topk(out, 5, dim=1)

        # create the list of dictionary structures that contain the predictions
        predictions = list()
        for idx in idxs.squeeze():
            predictions.append({
                "species" : self.categories[idx],
                "score" : out.squeeze()[idx].item(),
            })
        return predictions
