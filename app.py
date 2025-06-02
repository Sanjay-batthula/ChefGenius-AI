import streamlit as st
import requests
import random
import webbrowser
import pyttsx3

UPSTAGE_API_URL = "https://api.upstage.ai/v1/solar/chat/completions"
API_KEY = st.secrets["upstage_api_key"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_upstage(prompt, temperature=0.7, max_tokens=500):
    payload = {
        "model": "solar-1-mini-chat",
        "messages": [
            {"role": "system", "content": "You are a creative, fun and professional chef AI."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = requests.post(UPSTAGE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content'].strip()

def tts(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

st.set_page_config(page_title="🍳 ChefGenius AI", layout="wide")
st.title("🍳 ChefGenius: Recipe Wizard")

tabs = st.tabs([
    "👨‍🍳 Create Recipe", 
    "🎯 Step-by-Step Mode", 
    "📋 Shopping List", 
    "📊 Nutrition Info", 
    "🧊 What's in My Fridge?", 
    "📢 Voice & Video", 
    "🎲 Surprise Me"
])

# --- TAB 1: Recipe Generator ---
with tabs[0]:
    st.subheader("🧠 Recipe Generator")

    col1, col2 = st.columns(2)
    with col1:
        ingredients = st.text_area("Available Ingredients", "paneer, tortilla, tomatoes, garlic")
        cuisine_style = st.multiselect("Cuisine", ["Indian", "Mexican", "Italian", "Thai", "Japanese"], default=["Indian", "Mexican"])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        cooking_time = st.slider("Cooking Time (min)", 10, 120, 30)
    
    with col2:
        dietary_restrictions = st.multiselect("Dietary Needs", ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "None"], default=["None"])
        chef_style = st.radio("Chef Personality", ["Professional", "Funny", "Gordon Ramsay", "Chill Grandma"], index=0)
        substitute_request = st.checkbox("Suggest Ingredient Substitutes")

    if st.button("✨ Generate Recipe"):
        style = ", ".join(cuisine_style)
        diet = ", ".join(dietary_restrictions)
        tone_prompt = f"Respond in a {chef_style.lower()} tone."

        base_prompt = (
            f"{tone_prompt} Create a {style} recipe using: {ingredients}. "
            f"Time: {cooking_time} mins. Difficulty: {difficulty}. Dietary: {diet}. "
            f"Include prep time, cooking steps, and servings."
        )

        recipe = call_upstage(base_prompt)
        st.subheader("🍽️ Your Recipe")
        st.markdown(recipe)
        st.session_state.generated_recipe = recipe
        st.session_state.recipe_ingredients = ingredients

        if substitute_request:
            sub_prompt = f"Suggest 2-3 common substitutes for: {ingredients}."
            substitutes = call_upstage(sub_prompt)
            st.info(f"🔄 Substitution Tips:\n{substitutes}")

# --- TAB 2: Cook-Along Mode ---
with tabs[1]:
    st.subheader("🎯 Step-by-Step Cooking Assistant")
    if "generated_recipe" not in st.session_state:
        st.warning("Generate a recipe first.")
    else:
        steps = st.session_state.generated_recipe.split("\n")
        if "step_index" not in st.session_state:
            st.session_state.step_index = 0

        if st.button("➡️ Next Step"):
            st.session_state.step_index += 1

        step_idx = st.session_state.step_index
        if step_idx < len(steps):
            st.markdown(f"**Step {step_idx + 1}:** {steps[step_idx]}")
            if st.button("🔊 Read Aloud"):
                tts(steps[step_idx])
        else:
            st.success("Recipe complete! 🎉")

# --- TAB 3: Shopping List ---
with tabs[2]:
    st.subheader("📋 Auto Shopping List")
    if "recipe_ingredients" in st.session_state:
        ing_list = [i.strip().capitalize() for i in st.session_state.recipe_ingredients.split(",")]
        for item in ing_list:
            st.checkbox(item, value=False)
    else:
        st.warning("Generate a recipe to view the shopping list.")

# --- TAB 4: Nutrition Info ---
with tabs[3]:
    st.subheader("📊 Calorie Estimator")
    if "recipe_ingredients" in st.session_state:
        nutrition_prompt = f"Estimate calories, protein, carbs, fat, and fiber for a recipe using: {st.session_state.recipe_ingredients}."
        nutrition_data = call_upstage(nutrition_prompt)
        st.markdown(nutrition_data)
    else:
        st.warning("No data to show. Generate a recipe first.")

# --- TAB 5: What's in My Fridge ---
with tabs[4]:
    st.subheader("🧊 Fridge Mode")
    fridge_input = st.text_area("What's in your fridge?", "eggs, leftover rice, bell pepper")
    if st.button("🔍 Suggest Meals"):
        fridge_prompt = f"Suggest quick recipes I can make with: {fridge_input}"
        result = call_upstage(fridge_prompt)
        st.markdown(result)

# --- TAB 6: Voice Commands + Shorts Suggestion ---
with tabs[5]:
    st.subheader("🎥 Auto YouTube/Shorts + Voice")
    if "recipe_ingredients" in st.session_state:
        query = st.session_state.recipe_ingredients.replace(",", "+")
        video_link = f"https://www.youtube.com/results?search_query={query}+recipe"
        if st.button("▶️ Search YouTube/Shorts"):
            webbrowser.open_new_tab(video_link)
    st.caption("This opens a YouTube tab for related video recipes!")

# --- TAB 7: Surprise Me ---
with tabs[6]:
    st.subheader("🎲 Feeling Lucky?")
    if st.button("🎉 Surprise Me with a Random Recipe"):
        surprise_prompt = "Generate a random, wacky but tasty recipe. Include ingredients and steps."
        random_recipe = call_upstage(surprise_prompt)
        st.markdown(random_recipe)
        st.session_state.generated_recipe = random_recipe
        st.session_state.recipe_ingredients = "random ingredients"
