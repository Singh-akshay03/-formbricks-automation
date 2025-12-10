"""Generate realistic survey data using LLMs."""

import json
from typing import Dict, List, Any
from openai import OpenAI
from pathlib import Path


class DataGenerator:
    """Generate realistic survey and user data using OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """Initialize the data generator.

        Args:
            api_key: OpenAI API key
            model: Model to use for generation
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_surveys(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate realistic survey configurations.

        Args:
            count: Number of surveys to generate

        Returns:
            List of survey configurations
        """
        prompt = f"""Generate {count} realistic and diverse survey configurations for an experience management platform.

Each survey should have:
1. A clear name and purpose (e.g., Customer Satisfaction, Employee Onboarding, Product Feedback, NPS, Event Feedback)
2. 3-5 varied questions using different question types:
   - openText: Free-form text responses
   - multipleChoiceSingle: Single choice selection
   - multipleChoiceMulti: Multiple choice selection
   - nps: Net Promoter Score (0-10)
   - rating: Star or numeric rating

3. A welcoming welcome card
4. A thank you end screen

Return ONLY a JSON array of {count} survey objects with this structure:
[
  {{
    "name": "Survey Name",
    "type": "link",
    "status": "inProgress",
    "displayOption": "displayOnce",
    "questions": [
      {{
        "type": "openText",
        "headline": {{"default": "Question text?"}},
        "subheader": {{"default": "Additional context"}},
        "placeholder": {{"default": "Type your answer..."}},
        "inputType": "text",
        "required": true
      }},
      {{
        "type": "multipleChoiceSingle",
        "headline": {{"default": "Question text?"}},
        "required": true,
        "shuffleOption": "none",
        "choices": [
          {{"id": "choice-1", "label": {{"default": "Option 1"}}}},
          {{"id": "choice-2", "label": {{"default": "Option 2"}}}}
        ]
      }},
      {{
        "type": "nps",
        "headline": {{"default": "How likely are you to recommend us?"}},
        "lowerLabel": {{"default": "Not likely"}},
        "upperLabel": {{"default": "Very likely"}},
        "required": true
      }},
      {{
        "type": "rating",
        "headline": {{"default": "Rate your experience"}},
        "scale": "star",
        "range": 5,
        "required": true
      }}
    ],
    "welcomeCard": {{
      "enabled": true,
      "headline": {{"default": "Welcome!"}},
      "html": {{"default": "<p>Welcome message</p>"}},
      "showResponseCount": false,
      "timeToFinish": false
    }},
    "endings": [
      {{
        "type": "endScreen",
        "headline": {{"default": "Thank you!"}},
        "subheader": {{"default": "Thank you message"}},
        "buttonLabel": {{"default": "Close"}},
        "buttonLink": ""
      }}
    ],
    "hiddenFields": {{"enabled": false, "fieldIds": []}},
    "singleUse": {{"enabled": false, "isEncrypted": true}},
    "isVerifyEmailEnabled": false
  }}
]

Make surveys realistic and contextually appropriate. Use meaningful names, questions, and options."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a survey design expert. Generate realistic, well-structured surveys. Return only valid JSON, no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        return json.loads(content)

    def generate_users(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate realistic user profiles.

        Args:
            count: Number of users to generate

        Returns:
            List of user profiles
        """
        prompt = f"""Generate {count} realistic user profiles for a business software platform.

Each user should have:
1. A realistic full name
2. A professional email address
3. A role: either "manager" or "owner" (distribute evenly)

Return ONLY a JSON array of {count} user objects:
[
  {{
    "name": "John Smith",
    "email": "john.smith@company.com",
    "role": "manager"
  }}
]

Use diverse, realistic names and appropriate business email addresses. No additional text."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a data generator. Generate realistic user profiles. Return only valid JSON, no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        return json.loads(content)

    def generate_responses(self, survey: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        """Generate realistic responses for a survey.

        Args:
            survey: Survey configuration
            count: Number of responses to generate

        Returns:
            List of response data
        """
        # Prepare question context for the LLM
        questions_context = []
        for q in survey.get("questions", []):
            q_type = q.get("type")
            headline = q.get("headline", {}).get("default", "")
            q_id = q.get("id", "")

            context = {
                "id": q_id,
                "type": q_type,
                "headline": headline
            }

            if q_type in ["multipleChoiceSingle", "multipleChoiceMulti"]:
                choices = [c.get("label", {}).get("default", "") for c in q.get("choices", [])]
                context["choices"] = choices

            if q_type == "rating":
                context["range"] = q.get("range", 5)

            questions_context.append(context)

        prompt = f"""Generate {count} realistic survey response(s) for this survey: "{survey.get('name', 'Survey')}"

Questions:
{json.dumps(questions_context, indent=2)}

Return ONLY a JSON array of {count} response objects:
[
  {{
    "finished": true,
    "data": {{
      "question-id-1": "answer text",
      "question-id-2": 8,
      "question-id-3": ["choice1", "choice2"],
      "question-id-4": 5
    }},
    "meta": {{
      "source": "API",
      "url": "https://example.com"
    }}
  }}
]

Response format guidelines:
- openText: string answer
- multipleChoiceSingle: single choice string
- multipleChoiceMulti: array of choice strings
- nps: number 0-10
- rating: number based on range

Make responses realistic and contextually appropriate. Use the exact question IDs provided."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a survey respondent. Generate realistic, thoughtful survey responses. Return only valid JSON, no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        return json.loads(content)

    def save_to_file(self, data: Dict[str, Any], filepath: Path) -> None:
        """Save generated data to a JSON file.

        Args:
            data: Data to save
            filepath: Path to save the file
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
