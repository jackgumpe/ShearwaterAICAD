import google.generativeai as genai

genai.configure(api_key='AIzaSyCVJEoaQk2wuwEEMBYOADdx4P2EZQHvHDg')

print("Available Gemini Models:")
for m in genai.list_models():
    # Only list models that support generateContent
    if "generateContent" in m.supported_generation_methods:
        print(f"- {m.name}")