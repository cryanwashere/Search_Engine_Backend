'''
# Load iNaturalist model into memory
iNat_state_dict = torch.load('/home/Server_2/model_state_dict_finished.pth', map_location=torch.device('cpu'))
iNat_model = torchvision.models.vit_b_16()
iNat_model.heads = nn.Sequential(
    nn.Linear(in_features=iNat_model.heads[0].in_features, out_features = 10000)
)
iNat_model.load_state_dict(iNat_state_dict)
iNat_model.eval()
# I don't know if this is nescessary
del iNat_state_dict
print("loaded Naturify model")

# Load the iNaturalist categories
with open("categories.json","r") as f:
    iNat_categories = json.load(f)

# transform input into the Naturify model
iNat_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# inference the Naturify model on an image, and return a list of dictionary structures containing predictions for what species the image contains
def iNat_inference(inp):
    # inference the model (output logits)
    out = iNat_model(inp)

    # use softmax to convert the logits into probablities
    out = torch.softmax(out, dim=1)
    
    # find the top 5 most certain classes
    vals, idxs = torch.topk(out, 5, dim=1)

    # create the list of dictionary structures that contain the predictions
    predictions = list()
    for idx in idxs.squeeze():
        predictions.append({
            "species" : iNat_categories[idx],
            "score" : out.squeeze()[idx].item(),
        })
    return predictions
'''