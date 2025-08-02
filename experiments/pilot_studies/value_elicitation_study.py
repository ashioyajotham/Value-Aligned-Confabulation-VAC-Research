"""
Pilot Study: Value Elicitation for VAC Research

This module implements the pilot study for collecting human values and preferences
regarding when confabulation is acceptable in LLM outputs.
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

# Relative imports
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.evaluation.benchmarks.medical_scenarios import MedicalScenarios
#from src.evaluation.benchmarks.creative_tasks import CreativeScenarios
#from src.evaluation.benchmarks.educational_content import EducationalScenarios
from src.evaluation.vac_evaluator import Domain, EvaluationContext


@dataclass
class ValueElicitationResponse:
    """Response from a participant in the value elicitation study."""
    participant_id: str
    scenario_id: str
    domain: str
    response_a: str
    response_b: str
    preference: str  # "A", "B", "No preference"
    confidence: float  # 1-5 scale
    reasoning: str
    acceptability_rating: Dict[str, float]  # Rating for each response
    demographic_info: Dict[str, Any]
    timestamp: datetime


class ValueElicitationStudy:
    """
    Pilot study for eliciting human values regarding confabulation acceptability.
    
    This study presents participants with scenarios and different types of responses
    to understand when confabulation is considered acceptable vs. harmful.
    """
    
    def __init__(self):
        """Initialize the value elicitation study."""
        self.medical_scenarios = MedicalScenarios()
        # Note: Creative and Educational scenarios would be implemented similarly
        self.participants = []
        self.responses = []
        self.study_config = self._load_study_config()
        
    def _load_study_config(self) -> Dict[str, Any]:
        """Load study configuration."""
        return {
            "target_participants": 100,
            "scenarios_per_participant": 10,
            "domains_to_test": ["medical", "creative", "educational", "personal_advice"],
            "response_types": ["truthful", "confabulated_harmful", "confabulated_beneficial"],
            "demographic_questions": [
                "age_range", "education_level", "cultural_background", 
                "ai_familiarity", "domain_expertise"
            ],
            "acceptability_scale": {
                "1": "Completely unacceptable",
                "2": "Mostly unacceptable", 
                "3": "Neutral",
                "4": "Mostly acceptable",
                "5": "Completely acceptable"
            }
        }
    
    def generate_study_session(self, participant_id: str) -> Dict[str, Any]:
        """Generate a study session for a participant."""
        session = {
            "participant_id": participant_id,
            "session_id": str(uuid.uuid4()),
            "start_time": datetime.now(),
            "scenarios": [],
            "instructions": self._get_study_instructions(),
            "demographic_survey": self._get_demographic_survey()
        }
        
        # Select scenarios across different domains and risk levels
        selected_scenarios = self._select_scenarios_for_session()
        
        for scenario in selected_scenarios:
            # Generate different response types for comparison
            response_pairs = self._generate_response_pairs(scenario)
            
            session["scenarios"].append({
                "scenario": scenario,
                "response_pairs": response_pairs,
                "questions": self._generate_scenario_questions(scenario)
            })
        
        return session
    
    def _get_study_instructions(self) -> str:
        """Get instructions for study participants."""
        return """
        # Value-Aligned Confabulation Study Instructions
        
        Thank you for participating in this research study. We are investigating when AI responses that are not strictly factual might still be helpful or acceptable.
        
        ## What you'll be doing:
        1. Read various scenarios (questions or requests)
        2. Compare different AI responses to each scenario
        3. Indicate which response you prefer and why
        4. Rate how acceptable each response is
        
        ## Key concepts:
        - **Factual Response**: Strictly accurate information
        - **Confabulation**: Response that may not be strictly factual but could be helpful
        - **Harmful Confabulation**: Inaccurate information that could cause harm
        - **Beneficial Confabulation**: Inaccurate information that serves a good purpose
        
        ## What we're looking for:
        - Your genuine preferences and values
        - When you think it's okay for AI to be less than perfectly accurate
        - When accuracy is absolutely critical
        - How context affects your judgment
        
        Please answer honestly based on your own values and preferences.
        """
    
    def _get_demographic_survey(self) -> List[Dict[str, Any]]:
        """Get demographic survey questions."""
        return [
            {
                "question": "What is your age range?",
                "type": "multiple_choice",
                "options": ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
            },
            {
                "question": "What is your highest level of education?",
                "type": "multiple_choice",
                "options": ["High school", "Some college", "Bachelor's degree", "Graduate degree", "Other"]
            },
            {
                "question": "What is your cultural background?",
                "type": "open_text",
                "optional": True
            },
            {
                "question": "How familiar are you with AI systems?",
                "type": "scale",
                "scale": "1-5",
                "labels": {"1": "Not familiar", "5": "Very familiar"}
            },
            {
                "question": "Do you have professional expertise in any of these areas?",
                "type": "multiple_select",
                "options": ["Medicine/Healthcare", "Education", "Creative fields", "Technology", "Other", "None"]
            },
            {
                "question": "How often do you use AI assistants?",
                "type": "multiple_choice",
                "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"]
            }
        ]
    
    def _select_scenarios_for_session(self) -> List[Any]:
        """Select scenarios for a study session."""
        scenarios = []
        
        # Get medical scenarios across different risk levels
        medical_scenarios = self.medical_scenarios.scenarios
        
        # Select scenarios by risk level for balanced coverage
        risk_levels = ["critical", "high", "medium", "low"]
        scenarios_per_risk = 2
        
        for risk_level in risk_levels:
            risk_scenarios = [s for s in medical_scenarios if s.risk_level == risk_level]
            if risk_scenarios:
                selected = random.sample(risk_scenarios, min(scenarios_per_risk, len(risk_scenarios)))
                scenarios.extend(selected)
        
        # Add scenarios from other domains (placeholder for now)
        # In full implementation, would include creative, educational, etc.
        
        return scenarios[:self.study_config["scenarios_per_participant"]]
    
    def _generate_response_pairs(self, scenario: Any) -> List[Dict[str, Any]]:
        """Generate response pairs for comparison."""
        pairs = []
        
        # Create truthful vs beneficial confabulation pair
        if scenario.beneficial_confabulation_examples:
            pairs.append({
                "pair_id": str(uuid.uuid4()),
                "type": "truthful_vs_beneficial",
                "response_a": {
                    "text": scenario.ground_truth,
                    "type": "truthful",
                    "explanation": "Factually accurate response"
                },
                "response_b": {
                    "text": random.choice(scenario.beneficial_confabulation_examples),
                    "type": "beneficial_confabulation",
                    "explanation": "Response that may speculate but aims to be helpful"
                }
            })
        
        # Create truthful vs harmful confabulation pair
        if scenario.harmful_confabulation_examples:
            pairs.append({
                "pair_id": str(uuid.uuid4()),
                "type": "truthful_vs_harmful",
                "response_a": {
                    "text": scenario.ground_truth,
                    "type": "truthful",
                    "explanation": "Factually accurate response"
                },
                "response_b": {
                    "text": random.choice(scenario.harmful_confabulation_examples),
                    "type": "harmful_confabulation",
                    "explanation": "Response that contains potentially harmful speculation"
                }
            })
        
        # Create beneficial vs harmful confabulation pair
        if (scenario.beneficial_confabulation_examples and 
            scenario.harmful_confabulation_examples):
            pairs.append({
                "pair_id": str(uuid.uuid4()),
                "type": "beneficial_vs_harmful",
                "response_a": {
                    "text": random.choice(scenario.beneficial_confabulation_examples),
                    "type": "beneficial_confabulation",
                    "explanation": "Response that may speculate but aims to be helpful"
                },
                "response_b": {
                    "text": random.choice(scenario.harmful_confabulation_examples),
                    "type": "harmful_confabulation",
                    "explanation": "Response that contains potentially harmful speculation"
                }
            })
        
        return pairs
    
    def _generate_scenario_questions(self, scenario: Any) -> List[Dict[str, Any]]:
        """Generate questions for each scenario."""
        return [
            {
                "question": "Which response do you prefer?",
                "type": "multiple_choice",
                "options": ["Response A", "Response B", "No preference"],
                "required": True
            },
            {
                "question": "How confident are you in this preference?",
                "type": "scale",
                "scale": "1-5",
                "labels": {"1": "Not confident", "5": "Very confident"},
                "required": True
            },
            {
                "question": "Please explain your reasoning:",
                "type": "open_text",
                "required": True
            },
            {
                "question": "Rate the acceptability of Response A:",
                "type": "scale",
                "scale": "1-5",
                "labels": self.study_config["acceptability_scale"],
                "required": True
            },
            {
                "question": "Rate the acceptability of Response B:",
                "type": "scale",
                "scale": "1-5",
                "labels": self.study_config["acceptability_scale"],
                "required": True
            },
            {
                "question": "In this type of situation, how important is it for AI to be completely accurate?",
                "type": "scale",
                "scale": "1-5",
                "labels": {"1": "Not important", "5": "Extremely important"},
                "required": True
            },
            {
                "question": "Would your answer change if you knew the AI was uncertain about its response?",
                "type": "multiple_choice",
                "options": ["Yes, I'd be more accepting", "Yes, I'd be less accepting", "No, it wouldn't change"],
                "required": False
            }
        ]
    
    def collect_response(self, participant_response: Dict[str, Any]) -> ValueElicitationResponse:
        """Process and store a participant response."""
        response = ValueElicitationResponse(
            participant_id=participant_response["participant_id"],
            scenario_id=participant_response["scenario_id"],
            domain=participant_response["domain"],
            response_a=participant_response["response_a"],
            response_b=participant_response["response_b"],
            preference=participant_response["preference"],
            confidence=participant_response["confidence"],
            reasoning=participant_response["reasoning"],
            acceptability_rating=participant_response["acceptability_rating"],
            demographic_info=participant_response["demographic_info"],
            timestamp=datetime.now()
        )
        
        self.responses.append(response)
        return response
    
    def analyze_responses(self) -> Dict[str, Any]:
        """Analyze collected responses for insights."""
        if not self.responses:
            return {"error": "No responses to analyze"}
        
        analysis = {
            "total_responses": len(self.responses),
            "participant_count": len(set(r.participant_id for r in self.responses)),
            "domain_breakdown": {},
            "preference_patterns": {},
            "acceptability_analysis": {},
            "demographic_insights": {}
        }
        
        # Domain breakdown
        for domain in self.study_config["domains_to_test"]:
            domain_responses = [r for r in self.responses if r.domain == domain]
            if domain_responses:
                analysis["domain_breakdown"][domain] = {
                    "response_count": len(domain_responses),
                    "avg_confidence": sum(r.confidence for r in domain_responses) / len(domain_responses),
                    "preference_distribution": self._analyze_preferences(domain_responses)
                }
        
        # Preference patterns
        analysis["preference_patterns"] = self._analyze_preference_patterns()
        
        # Acceptability analysis
        analysis["acceptability_analysis"] = self._analyze_acceptability()
        
        # Demographic insights
        analysis["demographic_insights"] = self._analyze_demographics()
        
        return analysis
    
    def _analyze_preferences(self, responses: List[ValueElicitationResponse]) -> Dict[str, Any]:
        """Analyze preference patterns in responses."""
        preferences = {"A": 0, "B": 0, "No preference": 0}
        
        for response in responses:
            preferences[response.preference] += 1
        
        total = len(responses)
        return {
            "counts": preferences,
            "percentages": {k: v/total*100 for k, v in preferences.items()}
        }
    
    def _analyze_preference_patterns(self) -> Dict[str, Any]:
        """Analyze overall preference patterns."""
        patterns = {}
        
        # Group responses by response type pairs
        type_pairs = {}
        for response in self.responses:
            # This would need more detailed tracking of response types
            pair_key = "response_comparison"  # Placeholder
            if pair_key not in type_pairs:
                type_pairs[pair_key] = []
            type_pairs[pair_key].append(response)
        
        # Analyze patterns for each type of comparison
        for pair_type, pair_responses in type_pairs.items():
            patterns[pair_type] = self._analyze_preferences(pair_responses)
        
        return patterns
    
    def _analyze_acceptability(self) -> Dict[str, Any]:
        """Analyze acceptability ratings."""
        acceptability_data = {
            "response_a_ratings": [],
            "response_b_ratings": [],
            "overall_stats": {}
        }
        
        for response in self.responses:
            acceptability_data["response_a_ratings"].append(
                response.acceptability_rating.get("response_a", 0)
            )
            acceptability_data["response_b_ratings"].append(
                response.acceptability_rating.get("response_b", 0)
            )
        
        # Calculate statistics
        if acceptability_data["response_a_ratings"]:
            acceptability_data["overall_stats"]["response_a"] = {
                "mean": sum(acceptability_data["response_a_ratings"]) / len(acceptability_data["response_a_ratings"]),
                "median": sorted(acceptability_data["response_a_ratings"])[len(acceptability_data["response_a_ratings"])//2]
            }
        
        if acceptability_data["response_b_ratings"]:
            acceptability_data["overall_stats"]["response_b"] = {
                "mean": sum(acceptability_data["response_b_ratings"]) / len(acceptability_data["response_b_ratings"]),
                "median": sorted(acceptability_data["response_b_ratings"])[len(acceptability_data["response_b_ratings"])//2]
            }
        
        return acceptability_data
    
    def _analyze_demographics(self) -> Dict[str, Any]:
        """Analyze demographic patterns in responses."""
        demographics = {}
        
        # Group responses by demographic categories
        for response in self.responses:
            demo_info = response.demographic_info
            
            for demo_key, demo_value in demo_info.items():
                if demo_key not in demographics:
                    demographics[demo_key] = {}
                
                if demo_value not in demographics[demo_key]:
                    demographics[demo_key][demo_value] = []
                
                demographics[demo_key][demo_value].append(response)
        
        # Analyze patterns within each demographic group
        demographic_patterns = {}
        for demo_key, demo_groups in demographics.items():
            demographic_patterns[demo_key] = {}
            
            for demo_value, group_responses in demo_groups.items():
                demographic_patterns[demo_key][demo_value] = {
                    "count": len(group_responses),
                    "avg_confidence": sum(r.confidence for r in group_responses) / len(group_responses) if group_responses else 0,
                    "preference_distribution": self._analyze_preferences(group_responses)
                }
        
        return demographic_patterns
    
    def export_study_data(self, filepath: str) -> None:
        """Export study data to JSON file."""
        export_data = {
            "study_metadata": {
                "total_participants": len(set(r.participant_id for r in self.responses)),
                "total_responses": len(self.responses),
                "export_timestamp": datetime.now().isoformat(),
                "study_config": self.study_config
            },
            "responses": [asdict(response) for response in self.responses],
            "analysis": self.analyze_responses()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def generate_study_report(self) -> str:
        """Generate a human-readable study report."""
        analysis = self.analyze_responses()
        
        report = f"""
        # Value Elicitation Study Report
        
        ## Study Overview
        - Total Participants: {analysis.get('participant_count', 0)}
        - Total Responses: {analysis.get('total_responses', 0)}
        - Study Period: {datetime.now().strftime('%Y-%m-%d')}
        
        ## Key Findings
        
        ### Domain-Specific Patterns
        """
        
        for domain, data in analysis.get("domain_breakdown", {}).items():
            report += f"""
        #### {domain.title()} Domain
        - Response Count: {data['response_count']}
        - Average Confidence: {data['avg_confidence']:.2f}
        - Preference Distribution: {data['preference_distribution']['percentages']}
        """
        
        report += """
        ### Acceptability Analysis
        """
        
        acceptability = analysis.get("acceptability_analysis", {})
        if "overall_stats" in acceptability:
            for response_type, stats in acceptability["overall_stats"].items():
                report += f"""
        - {response_type}: Mean = {stats['mean']:.2f}, Median = {stats['median']:.2f}
        """
        
        report += """
        ### Demographic Insights
        """
        
        for demo_category, demo_data in analysis.get("demographic_insights", {}).items():
            report += f"""
        #### {demo_category.title()}
        """
            for demo_value, stats in demo_data.items():
                report += f"""
        - {demo_value}: {stats['count']} responses, Avg confidence: {stats['avg_confidence']:.2f}
        """
        
        return report


def run_pilot_study() -> ValueElicitationStudy:
    """Run the pilot value elicitation study."""
    study = ValueElicitationStudy()
    
    print("Value Elicitation Pilot Study")
    print("=" * 40)
    print(f"Target participants: {study.study_config['target_participants']}")
    print(f"Scenarios per participant: {study.study_config['scenarios_per_participant']}")
    print(f"Domains to test: {study.study_config['domains_to_test']}")
    
    # In a real implementation, this would integrate with a web interface
    # For now, we'll just set up the framework
    
    return study


if __name__ == "__main__":
    # Example usage
    study = run_pilot_study()
    
    # Generate example session
    example_session = study.generate_study_session("participant_001")
    
    print("\nExample Study Session Structure:")
    print(f"Session ID: {example_session['session_id']}")
    print(f"Number of scenarios: {len(example_session['scenarios'])}")
    
    if example_session['scenarios']:
        first_scenario = example_session['scenarios'][0]
        print(f"\nFirst scenario: {first_scenario['scenario'].prompt}")
        print(f"Number of response pairs: {len(first_scenario['response_pairs'])}")
        print(f"Number of questions: {len(first_scenario['questions'])}")
    
    # Show instructions
    print("\nStudy Instructions Preview:")
    print(example_session['instructions'][:500] + "...")
