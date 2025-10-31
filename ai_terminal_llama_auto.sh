#!/bin/bash
# ai_terminal_llama_auto.sh - Embedded AI Lab using LLaMA (auto backend)

source ~/ai-env/bin/activate

echo "======================================"
echo "      Welcome to Embedded AI Lab       "
echo "      (Text via LLaMA + Vision AI)    "
echo "======================================"

# Detect if llama-cpp-python is installed
if python3 -c "import llama_cpp" &> /dev/null; then
    USE_LLAMA_CPP=1
    echo "✅ Detected llama-cpp-python, will use CPU-optimized LLaMA"
else
    USE_LLAMA_CPP=0
    echo "⚠️ llama-cpp-python not found, will use PyTorch LLaMA"
fi

while true; do
    echo ""
    echo "Select an AI task:"
    echo "1) Text Generation (LLaMA)"
    echo "2) Image Classification (ViT)"
    echo "3) Object Detection (DETR)"
    echo "4) Exit"
    read -p "Enter choice [1-4]: " choice

    case $choice in
        1)
            read -p "Enter prompt for text generation: " prompt
            if [ "$USE_LLAMA_CPP" -eq 1 ]; then
                # llama-cpp-python
                python3 - <<EOF
from llama_cpp import Llama
model_path = "/path/to/llama-7B-q4.bin"
llm = Llama(model_path=model_path)
resp = llm("$prompt", max_tokens=100)
print("\nGenerated Text:\n", resp['choices'][0]['text'])
EOF
            else
                # PyTorch LLaMA fallback
                python3 - <<EOF
from transformers import LlamaForCausalLM, LlamaTokenizer
import torch
model_path = "/path/to/llama-model"
tokenizer = LlamaTokenizer.from_pretrained(model_path)
model = LlamaForCausalLM.from_pretrained(model_path)
inputs = tokenizer("$prompt", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
print("\nGenerated Text:\n", tokenizer.decode(outputs[0], skip_special_tokens=True))
EOF
            fi
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
