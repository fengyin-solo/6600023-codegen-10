from fastapi import APIRouter, Query
from typing import List, Dict, Any

from app.models.schemas import (
    LeadName,
    ECGLead,
    ECGAnalysisRequest,
    ECGAnalysisResponse,
    RPeak,
    HRVMetrics,
    ArrhythmiaEvent,
    ArrhythmiaType,
    PresetScenario,
    PRESET_CONFIGS,
)
from app.services.ecg_service import (
    generate_ecg_signal,
    pan_tompkins_r_peak_detection,
    calculate_hrv,
    detect_arrhythmia,
    get_rhythm_diagnosis,
)

router = APIRouter()


@router.get("/leads", response_model=List[str])
async def get_available_leads():
    """Get list of available ECG leads."""
    return [lead.value for lead in LeadName]


@router.get("/presets", response_model=List[Dict[str, Any]])
async def get_preset_scenarios():
    """Get list of available ECG preset scenarios."""
    presets = []
    for scenario, config in PRESET_CONFIGS.items():
        presets.append({
            "id": scenario.value,
            "name": config["name"],
            "heart_rate": config["heart_rate"],
            "duration": config["duration"],
            "sampling_rate": config["sampling_rate"],
            "default_lead": config["default_lead"].value,
            "st_elevation_bias": config["st_elevation_bias"],
            "noise_level": config["noise_level"],
            "hrv_intensity": config["hrv_intensity"],
        })
    return presets


@router.post("/analyze", response_model=ECGAnalysisResponse)
async def analyze_ecg(request: ECGAnalysisRequest):
    """
    Generate and analyze ECG signal for a specified lead.
    
    Performs:
    1. PQRST waveform generation
    2. Pan-Tompkins R-peak detection
    3. HRV metrics calculation
    4. Arrhythmia detection and classification
    """
    lead_name = request.lead_name
    duration = request.duration
    sampling_rate = request.sampling_rate
    heart_rate = request.heart_rate
    st_elevation_bias = request.st_elevation_bias
    noise_level = request.noise_level
    hrv_intensity = request.hrv_intensity

    if request.preset_scenario and request.preset_scenario in PRESET_CONFIGS:
        preset_config = PRESET_CONFIGS[request.preset_scenario]
        if request.lead_name == LeadName.II:
            lead_name = preset_config["default_lead"]
        if request.duration == 10.0:
            duration = preset_config["duration"]
        if request.sampling_rate == 500:
            sampling_rate = preset_config["sampling_rate"]
        if request.heart_rate == 72.0:
            heart_rate = preset_config["heart_rate"]
        if request.st_elevation_bias == 0.0:
            st_elevation_bias = preset_config["st_elevation_bias"]
        if request.noise_level == 0.02:
            noise_level = preset_config["noise_level"]
        if request.hrv_intensity == 0.02:
            hrv_intensity = preset_config["hrv_intensity"]

    time_array, ecg_signal = generate_ecg_signal(
        lead_name=lead_name.value,
        duration=duration,
        sampling_rate=sampling_rate,
        heart_rate=heart_rate,
        noise_level=noise_level,
        st_elevation_bias=st_elevation_bias,
        hrv_intensity=hrv_intensity,
    )

    r_peaks_raw = pan_tompkins_r_peak_detection(ecg_signal, sampling_rate)
    r_peaks = [
        RPeak(index=rp["index"], time=rp["time"], amplitude=rp["amplitude"])
        for rp in r_peaks_raw
    ]

    hrv_raw = calculate_hrv(r_peaks_raw, sampling_rate)
    hrv = HRVMetrics(**hrv_raw)

    arrhythmia_raw = detect_arrhythmia(
        r_peaks_raw, hrv_raw, ecg_signal, sampling_rate
    )
    arrhythmia_events = []
    for evt in arrhythmia_raw:
        arrhythmia_events.append(
            ArrhythmiaEvent(
                event_type=ArrhythmiaType(evt["event_type"]),
                confidence=evt["confidence"],
                description=evt["description"],
                timestamp=evt["timestamp"],
            )
        )

    diagnosis = get_rhythm_diagnosis(arrhythmia_raw, hrv_raw)

    lead = ECGLead(
        lead_name=lead_name,
        sampling_rate=sampling_rate,
        duration=duration,
        samples=[round(float(s), 4) for s in ecg_signal],
        r_peaks=r_peaks,
    )

    return ECGAnalysisResponse(
        lead=lead,
        hrv=hrv,
        arrhythmia_events=arrhythmia_events,
        rhythm_diagnosis=diagnosis,
    )
