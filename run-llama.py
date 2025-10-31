from llama_cpp import Llama

llm = Llama(model_path="/home/xlost/models/TinyLlama-1.1B-Chat-v1.0/model.safetensors")

result = llm("Q: What is Linux?\nA:")
print(result["choices"][0]["text"])
