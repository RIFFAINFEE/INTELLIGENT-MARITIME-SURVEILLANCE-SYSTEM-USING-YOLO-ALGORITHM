export const BASE_URL = 'http://localhost:8001';
export const WS_URL = 'ws://localhost:8001/ws';

export const api = {
    // Camera APIs
    startCamera: async (data) => {
        const response = await fetch(`${BASE_URL}/camera/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return response.json();
    },

    stopCamera: async (id) => {
        const response = await fetch(`${BASE_URL}/camera/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, url: '', allowed_classes: [] }),
        });
        return response.json();
    },

    listCameras: async () => {
        const response = await fetch(`${BASE_URL}/camera/list`);
        return response.json();
    },

    // Stream APIs
    startStream: async (data) => {
        const response = await fetch(`${BASE_URL}/stream/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return response.json();
    },

    stopStream: async (id) => {
        const response = await fetch(`${BASE_URL}/stream/stop/${id}`, {
            method: 'POST',
        });
        return response.json();
    },

    listStreams: async () => {
        const response = await fetch(`${BASE_URL}/stream/list`);
        return response.json();
    },

    getPreviewUrl: (id) => `${BASE_URL}/stream/preview/${id}`,

    getPreviewWithZonesUrl: (id) => `${BASE_URL}/stream/preview_with_zones/${id}`,

    getYoloPreviewUrl: (id) => `${BASE_URL}/stream/yolo_preview/${id}`,

    getAlertImageUrl: (imagePath) => {
        if (!imagePath) return "";
        // 1. Handle Windows backslashes in image paths from backend
        let sanitizedPath = imagePath.replace(/\\/g, '/');

        // 2. Replace the 'alerts/' folder prefix with the new static URL prefix '/alert-snapshots/'
        // The backend stores paths like 'alerts/cam1/...' but serves them at '/alert-snapshots/cam1/...'
        if (sanitizedPath.startsWith('alerts/')) {
            sanitizedPath = sanitizedPath.replace('alerts/', 'alert-snapshots/');
        }

        return `${BASE_URL}/${sanitizedPath}`;
    },

    // Zone APIs
    createZone: async (data) => {
        const response = await fetch(`${BASE_URL}/zone/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return response.json();
    },

    listZones: async () => {
        const response = await fetch(`${BASE_URL}/zone/list`);
        return response.json();
    },

    deleteZone: async (id) => {
        const response = await fetch(`${BASE_URL}/zone/${id}`, {
            method: 'DELETE',
        });
        return response.json();
    },

    getZonesByCamera: async (cameraId) => {
        const response = await fetch(`${BASE_URL}/zone/camera/${cameraId}`);
        return response.json();
    },

    updateZone: async (id, data) => {
        const response = await fetch(`${BASE_URL}/zone/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return response.json();
    },

    // Alerts API
    getAlerts: async () => {
        const response = await fetch(`${BASE_URL}/alerts/`);
        return response.json();
    },

    getAlertsByCamera: async (cameraId) => {
        const response = await fetch(`${BASE_URL}/alerts/camera/${cameraId}`);
        return response.json();
    }
};
