from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "skt/kogpt2-base-v2"  # 한국어 CPU 모델 추천
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to("cpu")

def chat(user_input):
    prompt = f"<usr>{user_input}</usr>"
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    outputs = model.generate(**inputs, max_new_tokens=100)
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return reply

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    print("AI:", chat(user_input))
