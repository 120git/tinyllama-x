#!/bin/bash
# ai_terminal.sh - Embedded AI System in Terminal

source ~/ai-env/bin/activate

echo "======================================"
echo "      Welcome to Embedded AI Lab       "
echo "======================================"

while true; do
    echo ""
    echo "Select an AI task:"
    echo "1) Text Generation (GPT-2)"
    echo "2) Image Classification (ViT)"
    echo "3) Object Detection (DETR)"
    echo "4) Exit"
    read -p "Enter choice [1-4]: " choice

    case $choice in
        1)
            read -p "Enter prompt for text generation: " prompt
            python3 - <<EOF
from transformers import pipeline
generator = pipeline("text-generation", model="gpt2")
result = generator("$prompt", max_length=50, num_return_sequences=1)
print("\nGenerated Text:\n", result[0]['generated_text'])
EOF
            ;;
        2)
            read -p "Enter image URL for classification: " img_url
            python3 - <<EOF
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import requests
image = Image.open(requests.get("$img_url", stream=True).raw)
processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)
predicted_class_idx = outputs.logits.argmax(-1).item()
label = model.config.id2label[predicted_class_idx]
print("Predicted label:", label)
EOF
            ;;
        3)
            read -p "Enter image URL for object detection: " img_url
            python3 - <<EOF
from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image, ImageDraw
import requests, torch, os
image = Image.open(requests.get("$img_url", stream=True).raw)
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(outputs, target_sizes=target_sizes)[0]
draw = ImageDraw.Draw(image)
for score, label, box in zip(results['scores'], results['labels'], results['boxes']):
    if score > 0.8:
        box = [round(i,2) for i in box.tolist()]
        label_text = f"{model.config.id2label[label.item()]}: {round(score.item(),3)}"
        draw.rectangle(box, outline="red", width=3)
        draw.text((box[0], box[1]-10), label_text, fill="red")
os.makedirs(os.path.expanduser("~/output"), exist_ok=True)
output_path = os.path.expanduser("~/output/detected_image.jpg")
image.save(output_path)
print("Annotated image saved to:", output_path)
EOF
            ;;
        4)
            echo "Exiting Embedded AI Lab. Goodbye!"
            break
            ;;
        *)
            echo "Invalid choice. Try again."
            ;;
    esac
done
