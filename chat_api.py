from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 모델과 토크나이저 불러오기 (작은 모델)
model_name = "gpt2"  # CPU에서도 실행 가능한 가벼운 모델
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 채팅 히스토리
chat_history = []

def chat(user_input):
    global chat_history
    chat_history.append(f"User: {user_input}")
    prompt = "\n".join(chat_history) + "\nAI:"

    # 입력 토큰화
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.7)
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # AI 응답만 추출
    reply_text = reply.split("AI:")[-1].strip()
    chat_history.append(f"AI: {reply_text}")
    return reply_text

# 채팅 시작
print("CPU GPT 채팅 시작! 종료하려면 'exit' 입력")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    response = chat(user_input)
    print("AI:", response)
