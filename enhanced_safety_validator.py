"""
Enhanced Safety Validator with Medical Knowledge Integration
Following the architecture guide's safety validation requirements
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import re

# Medical NLP and knowledge
import spacy
from transformers import pipeline

logger = logging.getLogger(__name__)

@dataclass
class PatientProfile:
    """Enhanced patient profile for safety validation"""
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    conditions: List[str] = None
    medications: List[str] = None
    allergies: List[str] = None
    kidney_function: Optional[str] = None  # normal, mild, moderate, severe
    liver_function: Optional[str] = None   # normal, mild, moderate, severe
    pregnancy_status: Optional[bool] = None

@dataclass
class DrugInteraction:
    """Drug interaction information"""
    drug1: str
    drug2: str
    interaction_type: str  # major, moderate, minor
    severity: str
    mechanism: str
    clinical_effect: str
    management: str

@dataclass
class Contraindication:
    """Contraindication information"""
    medication: str
    condition: str
    contraindication_type: str  # absolute, relative
    reason: str
    alternative_options: List[str]

@dataclass
class DosingAlert:
    """Dosing alert information"""
    medication: str
    alert_type: str  # overdose, underdose, frequency
    recommended_dose: str
    current_dose: str
    adjustment_reason: str

@dataclass
class ValidationResult:
    """Comprehensive validation result"""
    overall_safety_score: float  # 0-1, 1 being safest
    risk_level: str  # low, medium, high, critical
    drug_interactions: List[DrugInteraction]
    contraindications: List[Contraindication]
    dosing_alerts: List[DosingAlert]
    safety_warnings: List[str]
    recommendations: List[str]
    requires_monitoring: List[str]
    validation_timestamp: str

class MedicalKnowledgeBase:
    """Medical knowledge base for drug interactions and contraindications"""
    
    def __init__(self):
        self.drug_interactions = self._load_drug_interactions()
        self.contraindications = self._load_contraindications()
        self.dosing_guidelines = self._load_dosing_guidelines()
        
    def _load_drug_interactions(self) -> Dict[str, List[Dict]]:
        """Load drug interaction database"""
        # In production, this would load from a comprehensive database
        # For now, using common cardiovascular drug interactions
        return {
            "warfarin": [
                {
                    "interacting_drug": "aspirin",
                    "interaction_type": "major",
                    "severity": "high",
                    "mechanism": "additive anticoagulant effect",
                    "clinical_effect": "increased bleeding risk",
                    "management": "monitor INR closely, consider dose reduction"
                },
                {
                    "interacting_drug": "amiodarone",
                    "interaction_type": "major",
                    "severity": "high",
                    "mechanism": "CYP2C9 inhibition",
                    "clinical_effect": "increased warfarin levels",
                    "management": "reduce warfarin dose by 30-50%"
                }
            ],
            "digoxin": [
                {
                    "interacting_drug": "amiodarone",
                    "interaction_type": "major",
                    "severity": "high",
                    "mechanism": "P-glycoprotein inhibition",
                    "clinical_effect": "increased digoxin levels",
                    "management": "reduce digoxin dose by 50%"
                }
            ],
            "metoprolol": [
                {
                    "interacting_drug": "verapamil",
                    "interaction_type": "major",
                    "severity": "high",
                    "mechanism": "additive negative inotropic effects",
                    "clinical_effect": "severe bradycardia, heart block",
                    "management": "avoid combination or use with extreme caution"
                }
            ]
        }
    
    def _load_contraindications(self) -> Dict[str, List[Dict]]:
        """Load contraindication database"""
        return {
            "metoprolol": [
                {
                    "condition": "severe asthma",
                    "type": "absolute",
                    "reason": "beta-blockade can cause severe bronchospasm",
                    "alternatives": ["diltiazem", "verapamil"]
                },
                {
                    "condition": "heart block",
                    "type": "absolute",
                    "reason": "can worsen conduction abnormalities",
                    "alternatives": ["ACE inhibitors", "calcium channel blockers"]
                }
            ],
            "warfarin": [
                {
                    "condition": "active bleeding",
                    "type": "absolute",
                    "reason": "anticoagulation contraindicated with active bleeding",
                    "alternatives": ["mechanical hemostasis", "factor concentrates"]
                },
                {
                    "condition": "pregnancy",
                    "type": "absolute",
                    "reason": "teratogenic effects",
                    "alternatives": ["heparin", "LMWH"]
                }
            ],
            "ace_inhibitors": [
                {
                    "condition": "pregnancy",
                    "type": "absolute",
                    "reason": "teratogenic effects, fetal kidney damage",
                    "alternatives": ["methyldopa", "labetalol"]
                },
                {
                    "condition": "hyperkalemia",
                    "type": "relative",
                    "reason": "can worsen hyperkalemia",
                    "alternatives": ["calcium channel blockers", "diuretics"]
                }
            ]
        }
    
    def _load_dosing_guidelines(self) -> Dict[str, Dict]:
        """Load dosing guidelines"""
        return {
            "warfarin": {
                "initial_dose": "5-10 mg daily",
                "maintenance_dose": "2-10 mg daily",
                "target_inr": "2.0-3.0",
                "elderly_adjustment": "reduce initial dose by 50%",
                "renal_adjustment": "no adjustment needed",
                "hepatic_adjustment": "reduce dose, monitor closely"
            },
            "metoprolol": {
                "initial_dose": "25-50 mg twice daily",
                "maximum_dose": "200 mg twice daily",
                "heart_failure_dose": "12.5-25 mg twice daily initially",
                "elderly_adjustment": "start with lower doses",
                "renal_adjustment": "no adjustment needed",
                "hepatic_adjustment": "reduce dose in severe impairment"
            }
        }

class DrugExtractor:
    """Extract drug names and dosages from text"""
    
    def __init__(self):
        # Load medical NLP model
        try:
            self.nlp = spacy.load("en_core_sci_md")
        except OSError:
            # Fallback to basic model
            self.nlp = spacy.load("en_core_web_sm")
        
        # Common drug name patterns
        self.drug_patterns = [
            r'\b(metoprolol|atenolol|propranolol|carvedilol)\b',  # Beta blockers
            r'\b(lisinopril|enalapril|captopril|ramipril)\b',     # ACE inhibitors
            r'\b(amlodipine|nifedipine|diltiazem|verapamil)\b',   # Calcium channel blockers
            r'\b(warfarin|heparin|rivaroxaban|apixaban)\b',       # Anticoagulants
            r'\b(aspirin|clopidogrel|ticagrelor)\b',              # Antiplatelets
            r'\b(atorvastatin|simvastatin|rosuvastatin)\b',       # Statins
            r'\b(furosemide|hydrochlorothiazide|spironolactone)\b', # Diuretics
            r'\b(digoxin|amiodarone|flecainide)\b'                # Antiarrhythmics
        ]
        
        # Dosage patterns
        self.dose_pattern = r'(\d+(?:\.\d+)?)\s*(mg|g|mcg|units?)\s*(?:daily|twice daily|three times daily|q\d+h|bid|tid|qid)?'
    
    def extract_medications(self, text: str) -> List[Dict[str, Any]]:
        """Extract medications and dosages from text"""
        medications = []
        
        # Extract using regex patterns
        for pattern in self.drug_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                drug_name = match.group(1)
                
                # Look for dosage information near the drug name
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end]
                
                dose_match = re.search(self.dose_pattern, context, re.IGNORECASE)
                dose_info = dose_match.group(0) if dose_match else None
                
                medications.append({
                    "name": drug_name,
                    "dose": dose_info,
                    "context": context.strip()
                })
        
        # Use NLP for additional extraction
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["CHEMICAL", "DRUG"]:
                medications.append({
                    "name": ent.text.lower(),
                    "dose": None,
                    "context": ent.sent.text if ent.sent else ""
                })
        
        # Remove duplicates
        unique_meds = []
        seen_names = set()
        for med in medications:
            if med["name"] not in seen_names:
                unique_meds.append(med)
                seen_names.add(med["name"])
        
        return unique_meds

class EnhancedSafetyValidator:
    """Enhanced safety validator with comprehensive medical knowledge"""
    
    def __init__(self):
        self.knowledge_base = MedicalKnowledgeBase()
        self.drug_extractor = DrugExtractor()
        
        # Initialize medical classification model if available
        try:
            self.classifier = pipeline("text-classification", 
                                     model="emilyalsentzer/Bio_ClinicalBERT")
        except Exception:
            self.classifier = None
    
    async def validate_recommendation(self, 
                                    recommendation: str, 
                                    patient_profile: PatientProfile,
                                    check_interactions: bool = True,
                                    check_contraindications: bool = True) -> ValidationResult:
        """Comprehensive safety validation"""
        
        # Extract medications from recommendation
        extracted_meds = self.drug_extractor.extract_medications(recommendation)
        
        # Combine with patient medications
        all_medications = extracted_meds.copy()
        if patient_profile.medications:
            for med in patient_profile.medications:
                all_medications.append({"name": med.lower(), "dose": None, "context": "patient medication"})
        
        # Initialize validation components
        drug_interactions = []
        contraindications = []
        dosing_alerts = []
        safety_warnings = []
        recommendations = []
        requires_monitoring = []
        
        # Check drug interactions
        if check_interactions:
            drug_interactions = await self._check_drug_interactions(all_medications)
        
        # Check contraindications
        if check_contraindications:
            contraindications = await self._check_contraindications(extracted_meds, patient_profile)
        
        # Check dosing
        dosing_alerts = await self._check_dosing(extracted_meds, patient_profile)
        
        # Generate safety warnings and recommendations
        safety_warnings, recommendations, requires_monitoring = await self._generate_safety_guidance(
            drug_interactions, contraindications, dosing_alerts, patient_profile
        )
        
        # Calculate overall safety score
        safety_score = self._calculate_safety_score(drug_interactions, contraindications, dosing_alerts)
        
        # Determine risk level
        risk_level = self._determine_risk_level(safety_score, drug_interactions, contraindications)
        
        return ValidationResult(
            overall_safety_score=safety_score,
            risk_level=risk_level,
            drug_interactions=drug_interactions,
            contraindications=contraindications,
            dosing_alerts=dosing_alerts,
            safety_warnings=safety_warnings,
            recommendations=recommendations,
            requires_monitoring=requires_monitoring,
            validation_timestamp=datetime.now().isoformat()
        )
    
    async def _check_drug_interactions(self, medications: List[Dict]) -> List[DrugInteraction]:
        """Check for drug-drug interactions"""
        interactions = []
        
        med_names = [med["name"] for med in medications]
        
        for i, med1 in enumerate(med_names):
            for j, med2 in enumerate(med_names[i+1:], i+1):
                # Check both directions
                interaction = self._find_interaction(med1, med2)
                if interaction:
                    interactions.append(interaction)
        
        return interactions
    
    def _find_interaction(self, drug1: str, drug2: str) -> Optional[DrugInteraction]:
        """Find interaction between two drugs"""
        # Check drug1 -> drug2
        if drug1 in self.knowledge_base.drug_interactions:
            for interaction in self.knowledge_base.drug_interactions[drug1]:
                if interaction["interacting_drug"] == drug2:
                    return DrugInteraction(
                        drug1=drug1,
                        drug2=drug2,
                        interaction_type=interaction["interaction_type"],
                        severity=interaction["severity"],
                        mechanism=interaction["mechanism"],
                        clinical_effect=interaction["clinical_effect"],
                        management=interaction["management"]
                    )
        
        # Check drug2 -> drug1
        if drug2 in self.knowledge_base.drug_interactions:
            for interaction in self.knowledge_base.drug_interactions[drug2]:
                if interaction["interacting_drug"] == drug1:
                    return DrugInteraction(
                        drug1=drug2,
                        drug2=drug1,
                        interaction_type=interaction["interaction_type"],
                        severity=interaction["severity"],
                        mechanism=interaction["mechanism"],
                        clinical_effect=interaction["clinical_effect"],
                        management=interaction["management"]
                    )
        
        return None
    
    async def _check_contraindications(self, medications: List[Dict], patient_profile: PatientProfile) -> List[Contraindication]:
        """Check for contraindications based on patient conditions"""
        contraindications = []
        
        if not patient_profile.conditions:
            return contraindications
        
        for med in medications:
            med_name = med["name"]
            if med_name in self.knowledge_base.contraindications:
                for contraindication in self.knowledge_base.contraindications[med_name]:
                    # Check if patient has the contraindicated condition
                    for condition in patient_profile.conditions:
                        if condition.lower() in contraindication["condition"].lower():
                            contraindications.append(Contraindication(
                                medication=med_name,
                                condition=condition,
                                contraindication_type=contraindication["type"],
                                reason=contraindication["reason"],
                                alternative_options=contraindication["alternatives"]
                            ))
        
        return contraindications
    
    async def _check_dosing(self, medications: List[Dict], patient_profile: PatientProfile) -> List[DosingAlert]:
        """Check dosing appropriateness"""
        dosing_alerts = []
        
        for med in medications:
            med_name = med["name"]
            current_dose = med.get("dose")
            
            if not current_dose or med_name not in self.knowledge_base.dosing_guidelines:
                continue
            
            guidelines = self.knowledge_base.dosing_guidelines[med_name]
            
            # Check for elderly patients
            if patient_profile.age and patient_profile.age >= 65:
                if "elderly_adjustment" in guidelines:
                    dosing_alerts.append(DosingAlert(
                        medication=med_name,
                        alert_type="elderly_adjustment",
                        recommended_dose=guidelines["elderly_adjustment"],
                        current_dose=current_dose,
                        adjustment_reason="Age-related dose adjustment recommended"
                    ))
            
            # Check for renal impairment
            if patient_profile.kidney_function and patient_profile.kidney_function != "normal":
                if "renal_adjustment" in guidelines and "no adjustment" not in guidelines["renal_adjustment"]:
                    dosing_alerts.append(DosingAlert(
                        medication=med_name,
                        alert_type="renal_adjustment",
                        recommended_dose=guidelines["renal_adjustment"],
                        current_dose=current_dose,
                        adjustment_reason=f"Renal function: {patient_profile.kidney_function}"
                    ))
        
        return dosing_alerts
    
    async def _generate_safety_guidance(self, 
                                       drug_interactions: List[DrugInteraction],
                                       contraindications: List[Contraindication],
                                       dosing_alerts: List[DosingAlert],
                                       patient_profile: PatientProfile) -> Tuple[List[str], List[str], List[str]]:
        """Generate safety warnings, recommendations, and monitoring requirements"""
        
        safety_warnings = []
        recommendations = []
        requires_monitoring = []
        
        # Process drug interactions
        for interaction in drug_interactions:
            if interaction.severity == "high":
                safety_warnings.append(
                    f"HIGH RISK: {interaction.drug1} + {interaction.drug2} - {interaction.clinical_effect}"
                )
                recommendations.append(interaction.management)
                
                if "monitor" in interaction.management.lower():
                    requires_monitoring.append(f"Monitor for {interaction.clinical_effect}")
        
        # Process contraindications
        for contraindication in contraindications:
            if contraindication.contraindication_type == "absolute":
                safety_warnings.append(
                    f"ABSOLUTE CONTRAINDICATION: {contraindication.medication} in {contraindication.condition}"
                )
                recommendations.append(
                    f"Consider alternatives: {', '.join(contraindication.alternative_options)}"
                )
            else:
                safety_warnings.append(
                    f"RELATIVE CONTRAINDICATION: {contraindication.medication} in {contraindication.condition}"
                )
        
        # Process dosing alerts
        for alert in dosing_alerts:
            safety_warnings.append(
                f"DOSING ALERT: {alert.medication} - {alert.adjustment_reason}"
            )
            recommendations.append(
                f"Consider dose adjustment for {alert.medication}: {alert.recommended_dose}"
            )
        
        # Add general monitoring based on patient profile
        if patient_profile.age and patient_profile.age >= 65:
            requires_monitoring.append("Enhanced monitoring for elderly patient")
        
        if patient_profile.kidney_function and patient_profile.kidney_function != "normal":
            requires_monitoring.append("Monitor renal function")
        
        if patient_profile.liver_function and patient_profile.liver_function != "normal":
            requires_monitoring.append("Monitor hepatic function")
        
        return safety_warnings, recommendations, requires_monitoring
    
    def _calculate_safety_score(self, 
                               drug_interactions: List[DrugInteraction],
                               contraindications: List[Contraindication],
                               dosing_alerts: List[DosingAlert]) -> float:
        """Calculate overall safety score (0-1, higher is safer)"""
        
        base_score = 1.0
        
        # Deduct for drug interactions
        for interaction in drug_interactions:
            if interaction.severity == "high":
                base_score -= 0.3
            elif interaction.severity == "moderate":
                base_score -= 0.15
            else:
                base_score -= 0.05
        
        # Deduct for contraindications
        for contraindication in contraindications:
            if contraindication.contraindication_type == "absolute":
                base_score -= 0.4
            else:
                base_score -= 0.2
        
        # Deduct for dosing issues
        for alert in dosing_alerts:
            base_score -= 0.1
        
        return max(0.0, base_score)
    
    def _determine_risk_level(self, 
                             safety_score: float,
                             drug_interactions: List[DrugInteraction],
                             contraindications: List[Contraindication]) -> str:
        """Determine overall risk level"""
        
        # Check for critical issues
        has_absolute_contraindication = any(
            c.contraindication_type == "absolute" for c in contraindications
        )
        has_high_severity_interaction = any(
            i.severity == "high" for i in drug_interactions
        )
        
        if has_absolute_contraindication or safety_score < 0.3:
            return "critical"
        elif has_high_severity_interaction or safety_score < 0.6:
            return "high"
        elif safety_score < 0.8:
            return "medium"
        else:
            return "low"

# Example usage
async def main():
    """Example usage of enhanced safety validator"""
    validator = EnhancedSafetyValidator()
    
    # Example patient profile
    patient = PatientProfile(
        age=75,
        gender="male",
        conditions=["atrial fibrillation", "heart failure"],
        medications=["warfarin 5mg daily", "metoprolol 50mg twice daily"],
        allergies=["penicillin"]
    )
    
    # Example recommendation
    recommendation = "Start amiodarone 200mg daily for rhythm control"
    
    # Validate safety
    result = await validator.validate_recommendation(recommendation, patient)
    
    print(f"Safety Score: {result.overall_safety_score}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Interactions: {len(result.drug_interactions)}")
    print(f"Contraindications: {len(result.contraindications)}")

if __name__ == "__main__":
    asyncio.run(main())
