# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: .codex-smoke.spec.js >> complete primary prototype flow without browser errors
- Location: .codex-smoke.spec.js:5:1

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  - 1
+ Received  + 3

- Array []
+ Array [
+   "Failed to load resource: the server responded with a status of 404 (File not found)",
+ ]
```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - generic [ref=e3]: MediCare AI · App Prototype
    - generic [ref=e4]:
      - button "☀️ Light mode" [ref=e5] [cursor=pointer]
      - button "↺ Restart" [ref=e6] [cursor=pointer]
  - generic [ref=e8]:
    - generic [ref=e10]:
      - generic [ref=e11]: 9:41
      - generic [ref=e12]: 🔋
    - generic [ref=e16]:
      - generic:
        - generic:
          - generic:
            - generic: Good afternoon
            - generic: How are you feeling?
          - generic: G
        - generic: 🔒 On-device & private — nothing leaves your phone
        - generic:
          - img
          - generic: Start a Symptom Check
          - generic: Takes about 2 minutes
          - generic:
            - img
        - generic:
          - generic:
            - generic: "10"
            - generic: Conditions
          - generic:
            - generic: "4"
            - generic: Symptoms tracked
          - generic:
            - generic: <1s
            - generic: Avg. response
        - generic:
          - generic:
            - generic: Health History & Trends
            - generic:
              - generic: Clear All
              - img
          - generic:
            - generic:
              - generic:
                - generic:
                  - generic: Other
                  - generic: High risk
                - generic: Jun 27 08:59 PM · 65% confidence
                - generic: "Symptoms: fever, chest pain"
                - generic: Delete
        - generic:
          - generic: Daily tip
          - generic: 💧 Most adults need 7–8 hours of sleep for healthy blood pressure regulation.
      - generic:
        - generic:
          - generic: Find Care
          - generic: Nearby Clinics & Doctors
        - generic:
          - img
          - generic: 📍 Showing 3 clinics near you
        - generic:
          - generic:
            - generic:
              - text: General Clinic
              - generic: MediCare Central Clinic
            - generic:
              - generic: ⭐ 4.8
              - generic: 0.4 miles away
          - generic:
            - text: 👩‍⚕️ Dr. Sarah Jenkins · Specialist
            - generic: "🕒 Next slot: Today, 3:30 PM"
          - button "Book Appointment"
        - generic:
          - generic: All nearby clinics
          - generic:
            - generic:
              - generic:
                - generic:
                  - generic: MediCare Central Clinic
                  - generic: General Clinic · 0.4 miles
                - generic: ⭐ 4.8
            - generic:
              - generic:
                - generic:
                  - generic: Downtown Health Hub
                  - generic: Cardiology & Family Care · 1.2 miles
                - generic: ⭐ 4.9
            - generic:
              - generic:
                - generic:
                  - generic: Metro Urgent Care
                  - generic: Urgent Care Center · 2.5 miles
                - generic: ⭐ 4.6
      - generic:
        - generic:
          - generic: About
          - generic: How MediCare AI works
        - generic:
          - generic:
            - generic: "1"
            - generic:
              - generic: Enter symptoms & vitals
              - generic: Age, gender, the symptoms you're feeling, blood pressure and cholesterol level.
          - generic:
            - generic: "2"
            - generic:
              - generic: An AI model analyzes patterns
              - generic: Choose Random Forest, Gradient Boosting, or Logistic Regression — each trained on the same clinical dataset.
          - generic:
            - generic: "3"
            - generic:
              - generic: Get a risk-ranked result
              - generic: A predicted condition, confidence score, risk level, and tailored medicine & lifestyle advice.
        - generic:
          - generic: Current model
          - generic: Random Forest Classifier
          - generic: Benchmarked for informational purposes only — this is not a clinical diagnostic accuracy claim.
        - generic:
          - generic: Conditions we can recognize
          - generic:
            - generic: Hypertension
            - generic: Diabetes
            - generic: Asthma
            - generic: Stroke
            - generic: Migraine
            - generic: Bronchitis
            - generic: Influenza
            - generic: Osteoporosis
            - generic: Pneumonia
            - generic: Common Cold
            - generic: Depression
            - generic: Anxiety Disorders
            - generic: Other
        - generic:
          - generic: Frequently asked
          - generic:
            - generic:
              - text: Is this a substitute for a doctor?
              - img
          - generic:
            - generic:
              - text: Is my data stored?
              - img
          - generic:
            - generic:
              - text: Which AI models can I choose from?
              - img
        - generic:
          - generic:
            - generic: Contact & Support
            - img
        - generic: ⚠️ MediCare AI is an informational tool, not a certified medical device. In an emergency, contact local emergency services immediately.
      - generic [ref=e17]:
        - generic [ref=e18]:
          - generic [ref=e19]: Settings
          - generic [ref=e20]: Your preferences
        - generic [ref=e21]:
          - generic [ref=e22]: Appearance
          - generic [ref=e25]:
            - generic [ref=e26]: Dark mode
            - generic [ref=e27]: Easier on the eyes at night
        - generic [ref=e30]:
          - generic [ref=e31]: Privacy & data
          - generic [ref=e32]:
            - generic [ref=e33]: MediCare AI does not upload or store your symptom data on any server. Everything stays on this device, for this session only.
            - button "Clear session data" [ref=e34] [cursor=pointer]
        - generic [ref=e35]:
          - generic [ref=e36]: Support
          - generic [ref=e37]:
            - generic [ref=e38] [cursor=pointer]:
              - generic [ref=e39]: Help & Contact
              - img [ref=e40]
            - generic [ref=e42] [cursor=pointer]:
              - generic [ref=e43]: Rate MediCare AI
              - img [ref=e44]
        - generic [ref=e46]:
          - generic [ref=e47]: About app
          - generic [ref=e48]:
            - generic [ref=e49] [cursor=pointer]:
              - generic [ref=e50]: Terms of Service
              - img [ref=e51]
            - generic [ref=e53] [cursor=pointer]:
              - generic [ref=e54]: Privacy Policy
              - img [ref=e55]
            - generic [ref=e57]:
              - generic [ref=e58]: Version
              - generic [ref=e59]: 1.0.0 (2026.06)
      - generic:
        - generic:
          - generic: ⚕️
          - generic: MediCare AI
          - generic: Clarity for your symptoms, in seconds.
          - generic:
            - generic:
              - img
              - img
          - button "Get started"
      - generic:
        - generic:
          - generic: 🩺
          - generic: Before you begin
          - paragraph: MediCare AI uses machine learning to offer preliminary health information based on the symptoms and vitals you enter. It is not a medical device and does not provide a clinical diagnosis.
          - paragraph: Always consult a licensed healthcare professional for medical concerns or before starting any medication. In an emergency, contact local emergency services immediately.
          - generic:
            - generic: ✓
            - generic: I understand and agree to the Terms of Service and Privacy Policy.
          - generic: 🔒 Your symptom data stays on your device — we don't store it on our servers.
          - button "Get Started"
      - generic:
        - generic:
          - generic:
            - img
          - generic: Vitals & Model
        - generic:
          - generic:
            - generic: Let's start with the basics
            - paragraph: This helps personalize your result.
            - generic:
              - generic: Age
              - generic:
                - button "−"
                - generic:
                  - generic: "30"
                  - generic: years old
                - button "+"
            - generic:
              - generic: Gender
              - generic:
                - button "Female"
                - button "Male"
          - generic:
            - generic: Which symptoms are you experiencing?
            - paragraph: Select all that apply.
            - generic: Core ML Model Inputs
            - generic:
              - generic:
                - generic: 🤒
                - text: Fever
                - generic: ✓
              - generic:
                - generic: 😷
                - text: Cough
              - generic:
                - generic: 😴
                - text: Fatigue
              - generic:
                - generic: 🫁
                - text: Difficulty Breathing
            - generic: Other Tracked Symptoms
            - generic:
              - generic:
                - generic: 🤕
                - text: Headache
              - generic:
                - generic: 💔
                - text: Chest Pain
                - generic: ✓
              - generic:
                - generic: 🗣️
                - text: Sore Throat
              - generic:
                - generic: 🤢
                - text: Nausea
          - generic:
            - generic: A few clinical details
            - generic:
              - generic: Blood pressure
              - generic:
                - button "Low"
                - button "Normal"
                - button "High"
            - generic:
              - generic: Cholesterol level
              - generic:
                - button "Low"
                - button "Normal"
                - button "High"
            - generic:
              - generic: "Heart rate: 75 bpm"
              - generic:
                - slider: "75"
            - generic:
              - generic: "Weight & Height (BMI: 24.2)"
              - generic:
                - generic:
                  - generic: Weight (kg)
                  - generic:
                    - button "−"
                    - generic: "70"
                    - button "+"
                - generic:
                  - generic: Height (cm)
                  - generic:
                    - button "−"
                    - generic: "170"
                    - button "+"
            - generic:
              - generic: AI model
              - generic:
                - generic:
                  - generic:
                    - generic: Random Forest
                    - generic: Recommended
                  - generic: Best overall accuracy across symptom combinations.
                - generic:
                  - generic:
                    - generic: Gradient Boosting
                  - generic: Strong on complex, layered symptom patterns.
                - generic:
                  - generic:
                    - generic: Logistic Regression
                  - generic: Fast and easy to interpret.
        - generic:
          - generic:
            - button "Back"
            - button "Analyze Symptoms"
      - generic:
        - generic:
          - generic:
            - generic:
              - img
              - img
          - generic: Analyzing your symptoms…
          - generic: Running Random Forest model · 13 features scaled & preprocessed
      - generic:
        - generic:
          - generic:
            - img
          - generic: Your Results
        - generic:
          - generic:
            - generic:
              - generic: Top match
              - generic:
                - generic: High risk
            - generic: Other
            - generic:
              - generic:
                - generic: 65%
                - generic: model confidence
          - generic:
            - generic: Possible conditions
            - generic:
              - generic:
                - generic: "1"
                - generic: Other
                - generic: 65.3%
              - generic:
                - generic: "2"
                - generic: Stroke
                - generic: 38.1%
              - generic:
                - generic: "3"
                - generic: Influenza
                - generic: 12.0%
              - generic:
                - generic: "4"
                - generic: Asthma
                - generic: 11.0%
              - generic:
                - generic: "5"
                - generic: Migraine
                - generic: 3.7%
          - generic: ⚠️ This is not a medical diagnosis. Consult a healthcare professional.
        - generic:
          - button "View Medicines & Advice"
          - button "📍 Find Nearby Clinics"
          - button "Start a new check"
      - generic:
        - generic:
          - generic:
            - img
          - generic: Medicines & Advice
        - generic:
          - generic:
            - generic: Other
            - generic:
              - generic: High risk
          - generic:
            - generic: Recommended medicines
            - generic:
              - generic:
                - generic: ⚕️
                - generic:
                  - generic: Consult doctor for specific treatment
          - generic:
            - generic: Advice & lifestyle
            - generic:
              - generic: 📞 Schedule appointment with healthcare provider
              - generic: "🌡️ MONITOR: Track your symptoms closely"
              - generic: "📝 LOG: Keep a diary of any new or worsening symptoms"
        - generic:
          - text: ⚠️ Always consult a licensed healthcare professional before starting any medication.
          - generic:
            - button "Back to results"
            - button "New check"
      - generic:
        - generic:
          - generic:
            - img
          - generic: Book Consultation
        - generic:
          - generic:
            - text: General Clinic
            - generic: MediCare Central Clinic
            - generic: "👨‍⚕️ Doctor: Dr. Sarah Jenkins"
          - generic:
            - generic: Select Date & Time
            - generic:
              - button "Today"
              - button "Tomorrow"
            - generic:
              - button "9:30 AM"
              - button "11:00 AM"
              - button "2:00 PM"
              - button "4:30 PM"
          - generic:
            - generic: Reason for Visit
            - textbox "e.g. Heart health consultation"
        - generic:
          - button "Confirm Appointment"
    - generic [ref=e60]:
      - button "Home" [ref=e61] [cursor=pointer]:
        - img [ref=e62]
        - text: Home
      - button "Check" [ref=e65] [cursor=pointer]:
        - img [ref=e66]
        - text: Check
      - button "Care" [ref=e69] [cursor=pointer]:
        - img [ref=e70]
        - text: Care
      - button "About" [ref=e73] [cursor=pointer]:
        - img [ref=e74]
        - text: About
      - button "Settings" [ref=e77] [cursor=pointer]:
        - img [ref=e78]
        - text: Settings
  - generic [ref=e81]: "How to explore: Tap “Get started” → accept the disclaimer → tap the card or the Check tab to run a symptom check. Try different ages, symptoms, blood pressure, and cholesterol combinations. Watch the risk level and predicted condition change in real time. The demo runs the exact RandomForest classification probabilities precomputed from the project's trained scikit-learn models and retrieves clinical suggestions from `medicine_db.json`. Use the buttons above the phone to switch themes or restart the simulation."
```

# Test source

```ts
  1  | const { test, expect } = require('@playwright/test');
  2  | 
  3  | test.use({ channel: 'chrome', viewport: { width: 390, height: 844 } });
  4  | 
  5  | test('complete primary prototype flow without browser errors', async ({ page }) => {
  6  |   const errors = [];
  7  |   page.on('pageerror', error => errors.push(error.message));
  8  |   page.on('console', message => {
  9  |     if (message.type() === 'error') errors.push(message.text());
  10 |   });
  11 | 
  12 |   await page.goto('http://127.0.0.1:8765/medicare-ai-mobile-app-prototype.html');
  13 |   await expect(page.locator('#overlay-splash')).toHaveClass(/active/);
  14 |   await page.locator('#splashContinueBtn').click();
  15 |   await expect(page.locator('#onbContinueBtn')).toBeDisabled();
  16 |   await page.locator('#consentRow').click();
  17 |   await expect(page.locator('#onbContinueBtn')).toBeEnabled();
  18 |   await page.locator('#onbContinueBtn').click();
  19 | 
  20 |   await page.locator('#homeCtaCard').click();
  21 |   await expect(page.locator('#overlay-wizard')).toHaveClass(/active/);
  22 |   await page.locator('#wizardNextBtn').click();
  23 |   await page.locator('[data-symptom="fever"]').click();
  24 |   await page.locator('[data-symptom="chest_pain"]').click();
  25 |   await page.locator('#wizardNextBtn').click();
  26 |   await page.locator('[data-group="bp"] button[data-val="high"]').click();
  27 |   await page.locator('#wizardNextBtn').click();
  28 | 
  29 |   await expect(page.locator('#overlay-results')).toHaveClass(/active/, { timeout: 4000 });
  30 |   await expect(page.locator('#resultDisease')).not.toHaveText('');
  31 |   await expect(page.locator('#diffList .diff-row')).toHaveCount(5);
  32 |   await expect(page.locator('#resultsFindCareBtn')).toBeVisible();
  33 |   await page.locator('#viewMedsBtn').click();
  34 |   await expect(page.locator('#medsList .med-card')).not.toHaveCount(0);
  35 |   await page.locator('#medsBackToResultsBtn').click();
  36 |   await page.locator('#resultsCloseBtn').click();
  37 |   await expect(page.locator('#historyTimeline .history-row')).toHaveCount(1);
  38 | 
  39 |   await page.locator('.nav-item[data-tab="care"]').click();
  40 |   await page.locator('#clinicsList .clinic-row').first().click();
  41 |   await page.locator('#openBookModalBtn').click();
  42 |   await page.locator('#bookDaySegmented button[data-val="tomorrow"]').click();
  43 |   await page.locator('#bookSlotsGrid .slot-btn').nth(1).click();
  44 |   await page.locator('#confirmBookingBtn').click();
  45 |   await expect(page.locator('#appointmentsCard')).toBeVisible();
  46 |   await page.locator('#cancelApptBtn').click();
  47 |   await expect(page.locator('#appointmentsCard')).toBeHidden();
  48 | 
  49 |   console.log(await page.evaluate(() => JSON.stringify((() => {
  50 |     const nav = document.querySelector('.nav-item[data-tab="settings"]');
  51 |     const rect = nav.getBoundingClientRect();
  52 |     return {
  53 |       overlays: [...document.querySelectorAll('.overlay')].map(el => ({ id: el.id, className: el.className, rect: el.getBoundingClientRect().toJSON() })),
  54 |       navRect: rect.toJSON(),
  55 |       hitStack: document.elementsFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2).map(el => `${el.id || el.className || el.tagName}`)
  56 |     };
  57 |   })())));
  58 |   await page.locator('.nav-item[data-tab="settings"]').click();
  59 |   await page.locator('#darkToggle').click();
  60 |   await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  61 | 
> 62 |   expect(errors).toEqual([]);
     |                  ^ Error: expect(received).toEqual(expected) // deep equality
  63 | });
  64 | 
  65 | test('survives malformed saved browser data', async ({ page }) => {
  66 |   const errors = [];
  67 |   page.on('pageerror', error => errors.push(error.message));
  68 |   await page.goto('http://127.0.0.1:8765/medicare-ai-mobile-app-prototype.html');
  69 |   await page.evaluate(() => {
  70 |     localStorage.setItem('medicare_history', '{}');
  71 |     localStorage.setItem('medicare_appointments', 'null');
  72 |   });
  73 |   await page.reload();
  74 |   expect(errors).toEqual([]);
  75 | });
  76 | 
```