import axios from 'axios';

// Keep axios in case you want to switch back later
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Toggle this
const USE_MOCK = true;

// ---------------------- MOCK DATA ----------------------

const attackTypes = [
  "DoS",
  "Probe",
  "R2L",
  "U2R",
  "Normal"
];

export const predictConnection = async (data) => {

  if (!USE_MOCK) {
    // Put your real API code here later
  }

  const isAttack = Math.random() > 0.35;

  const confidence = Number((95 + Math.random() * 4.8).toFixed(2));

  return {
    status: isAttack ? "attack" : "normal",

    attackType: isAttack
      ? attackTypes[Math.floor(Math.random() * 4)]
      : undefined,

    confidence,

    attackProbabilities: isAttack
      ? {
          Normal: Number((Math.random() * 0.2).toFixed(2)),
          Attack: Number((0.8 + Math.random() * 0.2).toFixed(2)),
        }
      : {
          Normal: Number((0.8 + Math.random() * 0.2).toFixed(2)),
          Attack: Number((Math.random() * 0.2).toFixed(2)),
        },

    timestamp: new Date().toISOString(),

    processingTime: `${(20 + Math.random() * 60).toFixed(1)} ms`,
  };
};

export const getModelStatus = async () => {

  if (!USE_MOCK) {
    // Real request later
  }

  return {
    online: true,
    modelVersion: "RBF-SVM-PCA39",
    accuracy: 99.37,
    lastUpdated: new Date().toISOString(),
  };
};

export const getPredictionHistory = async () => {

  return [
    {
      status: "normal",
      confidence: 98.7,
      timestamp: "2026-08-03T09:10:00Z",
    },
    {
      status: "attack",
      attackType: "DoS",
      confidence: 99.12,
      timestamp: "2026-08-03T09:12:00Z",
    },
    {
      status: "attack",
      attackType: "Probe",
      confidence: 97.91,
      timestamp: "2026-08-03T09:15:00Z",
    },
    {
      status: "normal",
      confidence: 96.84,
      timestamp: "2026-08-03T09:18:00Z",
    },
    {
      status: "attack",
      attackType: "R2L",
      confidence: 98.56,
      timestamp: "2026-08-03T09:22:00Z",
    },
  ];
};

export default apiClient;