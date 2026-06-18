export interface ECGLead {
  leadName: string;
  samplingRate: number;
  duration: number;
  samples: number[];
  rPeaks: RPeak[];
}

export interface RPeak {
  index: number;
  time: number;
  amplitude: number;
}

export interface HRVData {
  heartRate: number;
  sdnn: number;
  rmssd: number;
  pnn50: number;
  nnIntervals: number[];
}

export interface ArrhythmiaEvent {
  eventType: 'normal' | 'tachycardia' | 'bradycardia' | 'st_elevation' | 'atrial_fibrillation' | 'premature_ventricular_contraction';
  confidence: number;
  description: string;
  timestamp: number;
}

export interface ECGAnalysisResponse {
  lead: ECGLead;
  hrv: HRVData;
  arrhythmiaEvents: ArrhythmiaEvent[];
  rhythmDiagnosis: string;
}

export interface ECGAnalysisRequest {
  leadName: string;
  duration: number;
  samplingRate: number;
  heartRate: number;
}

export const LEAD_NAMES: string[] = [
  'I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'
];

export type PresetScenario = 'resting' | 'post_exercise' | 'nighttime';

export interface ECGPreset {
  id: PresetScenario;
  name: string;
  description: string;
  icon: string;
  color: string;
  heartRate: number;
  heartRateMin: number;
  heartRateMax: number;
  duration: number;
  samplingRate: number;
  defaultLead: string;
  stElevationBias: number;
  noiseLevel: number;
  hrvIntensity: number;
}

export const ECG_PRESETS: Record<PresetScenario, ECGPreset> = {
  resting: {
    id: 'resting',
    name: '静息状态',
    description: '常规静息心电图检查，适用于日常体检和门诊筛查',
    icon: 'chair',
    color: 'emerald',
    heartRate: 72,
    heartRateMin: 60,
    heartRateMax: 100,
    duration: 10,
    samplingRate: 500,
    defaultLead: 'II',
    stElevationBias: 0.0,
    noiseLevel: 0.02,
    hrvIntensity: 0.02,
  },
  post_exercise: {
    id: 'post_exercise',
    name: '运动后监测',
    description: '运动负荷试验后监测，评估心肌缺血和心率恢复情况',
    icon: 'activity',
    color: 'orange',
    heartRate: 125,
    heartRateMin: 100,
    heartRateMax: 170,
    duration: 15,
    samplingRate: 500,
    defaultLead: 'V4',
    stElevationBias: 0.05,
    noiseLevel: 0.035,
    hrvIntensity: 0.04,
  },
  nighttime: {
    id: 'nighttime',
    name: '夜间监测',
    description: '睡眠期间长时间心电监测，检测夜间心律失常和心率变异性',
    icon: 'moon',
    color: 'indigo',
    heartRate: 58,
    heartRateMin: 40,
    heartRateMax: 80,
    duration: 30,
    samplingRate: 250,
    defaultLead: 'II',
    stElevationBias: 0.0,
    noiseLevel: 0.01,
    hrvIntensity: 0.05,
  },
};
