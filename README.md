
# 🌍 EcoChange Helper
![Logo](logo.png)

**Exposing the invisible inequality in the air we breathe.**

---

## 🚩 The Problem: "Invisible Inequality"
Climate change is often discussed as a global, distant threat, but its most immediate impact is local and unequal. Most people don't realize that due to poor urban planning and industrial placement, the air in a lower-income neighborhood can be significantly more toxic than in a wealthy suburb just a few kilometers away. This data is usually buried in complex government spreadsheets that the general public cannot access or understand.

## 💡 The Solution
EcoChange Helper is a diagnostic tool that translates raw environmental telemetry into a "Human Reality Check." By entering a city, users get an immediate report on their local air toxicity and a personalized carbon impact score. Instead of just showing numbers, the app uses **Generative AI** to explain the biological cost of that air and predicts a localized "2030 Brutal Truth" for that specific city.

## 🚀 Impact
* **Public Awareness:** Moves environmental data out of the classroom and into the hands of everyday citizens.
* **Health Advocacy:** Highlights PM2.5 and Ozone risks that directly correlate to respiratory and cardiovascular health.
* **Accountability:** By showing the "Inequality Gap," the app provides a visual argument for better urban greening and pollution control in neglected areas.

## ⚙️ How It Works
1. **Data Retrieval:** The app uses a **Geocoding API** to find coordinates and the **Open-Meteo API** to pull live PM2.5 and Ozone levels.
2. **Personal Calculation:** A Flask backend processes user input (transport, diet, energy) to calculate a daily CO2 equivalent.
3. **AI Narrative Engine:** **Google Gemini 1.5-Flash** analyzes the raw air quality data and the user's score to generate a gritty, 3-sentence forecast of what life in that city will look like by 2030 if nothing changes.
4. **Dynamic UI:** The results are rendered in a high-impact dashboard designed for clarity and urgency.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Framework:** Flask
* **AI:** Google Gemini API
* **APIs:** Open-Meteo (Air Quality), Geocoding
* **Environment:** Python-Dotenv for secure API key management
* **Frontend:** HTML5, CSS3

---

## 🏃 Setup & Installation
1. Clone the repo: `git clone https://github.com/your-username/EcoChange-Helper.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Add your `GOOGLE_API_KEY` to a `.env` file.
4. Run the app: `python app.py`

**Built for the 2030 AI Challenge | March 2026**