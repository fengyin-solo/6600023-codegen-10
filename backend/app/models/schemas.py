from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class LeadName(str, Enum):
    I = "I"
    II = "II"
    III = "III"
    aVR = "aVR"
    aVL = "aVL"
    aVF = "aVF"
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V5 = "V5"
    V6 = "V6"


class ArrhythmiaType(str, Enum):
    NORMAL = "normal"
    TACHYCARDIA = "tachycardia"
    BRADYCARDIA = "bradycardia"
    ST_ELEVATION = "st_elevation"
    AFIB = "atrial_fibrillation"
    PVC = "premature_ventricular_contraction"


class PresetScenario(str, Enum):
    RESTING = "resting"
    POST_EXERCISE = "post_exercise"
    NIGHTTIME = "nighttime"


PRESET_CONFIGS = {
    PresetScenario.RESTING: {
        "name": "静息状态",
        "heart_rate": 72.0,
        "duration": 10.0,
        "sampling_rate": 500,
        "default_lead": LeadName.II,
        "st_elevation_bias": 0.0,
        "noise_level": 0.02,
        "hrv_intensity": 0.02,
    },
    PresetScenario.POST_EXERCISE: {
        "name": "运动后监测",
        "heart_rate": 125.0,
        "duration": 15.0,
        "sampling_rate": 500,
        "default_lead": LeadName.V4,
        "st_elevation_bias": 0.05,
        "noise_level": 0.035,
        "hrv_intensity": 0.04,
    },
    PresetScenario.NIGHTTIME: {
        "name": "夜间监测",
        "heart_rate": 58.0,
        "duration": 30.0,
        "sampling_rate": 250,
        "default_lead": LeadName.II,
        "st_elevation_bias": 0.0,
        "noise_level": 0.01,
        "hrv_intensity": 0.05,
    },
}


class RPeak(BaseModel):
    index: int = Field(..., description="Sample index of R-peak")
    time: float = Field(..., description="Time in seconds")
    amplitude: float = Field(..., description="Amplitude in mV")


class HRVMetrics(BaseModel):
    heart_rate: float = Field(..., description="Heart rate in BPM")
    sdnn: float = Field(..., description="Standard deviation of NN intervals (ms)")
    rmssd: float = Field(..., description="Root mean square of successive differences (ms)")
    pnn50: float = Field(..., description="Percentage of successive differences > 50ms")
    nn_intervals: List[float] = Field(default_factory=list, description="NN intervals in ms")


class ArrhythmiaEvent(BaseModel):
    event_type: ArrhythmiaType = Field(..., description="Type of arrhythmia detected")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    description: str = Field(..., description="Human-readable description")
    timestamp: float = Field(..., description="Event timestamp in seconds")


class ECGLead(BaseModel):
    lead_name: LeadName = Field(..., description="ECG lead name")
    sampling_rate: int = Field(default=500, description="Sampling rate in Hz")
    duration: float = Field(default=10.0, description="Duration in seconds")
    samples: List[float] = Field(default_factory=list, description="ECG samples in mV")
    r_peaks: List[RPeak] = Field(default_factory=list, description="Detected R-peaks")


class ECGAnalysisRequest(BaseModel):
    lead_name: LeadName = Field(default=LeadName.II, description="ECG lead to analyze")
    duration: float = Field(default=10.0, ge=1.0, le=120.0, description="Duration in seconds")
    sampling_rate: int = Field(default=500, ge=100, le=1000, description="Sampling rate in Hz")
    heart_rate: float = Field(default=72.0, ge=30, le=200, description="Simulated heart rate BPM")
    preset_scenario: PresetScenario | None = Field(default=None, description="Preset scenario ID")
    st_elevation_bias: float = Field(default=0.0, ge=0.0, le=0.3, description="ST-elevation bias in mV")
    noise_level: float = Field(default=0.02, ge=0.0, le=0.1, description="Noise amplitude level")
    hrv_intensity: float = Field(default=0.02, ge=0.0, le=0.1, description="HRV variation intensity")


class ECGAnalysisResponse(BaseModel):
    lead: ECGLead = Field(..., description="ECG lead data")
    hrv: HRVMetrics = Field(..., description="HRV analysis results")
    arrhythmia_events: List[ArrhythmiaEvent] = Field(default_factory=list, description="Detected arrhythmia events")
    rhythm_diagnosis: str = Field(..., description="Overall rhythm diagnosis")
