import React, { useState, useEffect, useRef } from 'react';
import {
  Ship, Shield, Camera, LayoutDashboard,
  Bell, Search,
  Activity, Database, Power, Plus, Trash2, Edit2
} from 'lucide-react';
import { api, WS_URL } from './services/api';
import ZoneEditor from './components/ZoneEditor';

const YOLO_CLASSES = [
  "person", "bicycle", "car", "motorcycle", "bus", "truck", "boat", "bird", "ship"
];

const getPlaceName = (lat, lon) => {
  if (lat === undefined || lon === undefined) return "Chennai Coastal";
  if (lat >= 13.00 && lat < 13.07) return "Marina Beach / Santhome Coastal";
  if (lat >= 13.07 && lat < 13.13) return "Chennai Port / Royapuram Area";
  if (lat >= 13.13 && lat < 13.17) return "Kasimedu / Thiruvottiyur Coastal";
  if (lat >= 13.17 && lat <= 13.20) return "Ennore Port / Coastal Range";
  return "Chennai Coastal Area";
};

const playAlertSound = () => {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;

    const audioCtx = new AudioContext();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // A5 note
    oscillator.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.5); // Slide down

    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.5);
  } catch (err) {
    console.warn("Audio Context blocked or not supported", err);
  }
};

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [previewMode, setPreviewMode] = useState('zones'); // 'raw', 'zones', 'yolo'
  const [cameras, setCameras] = useState([]);
  const [runningCameras, setRunningCameras] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [zones, setZones] = useState([]);
  const [selectedClasses, setSelectedClasses] = useState(["ship", "boat", "car", "person"]); // Default labels
  const [showAddCamera, setShowAddCamera] = useState(false);
  const [editingZoneCam, setEditingZoneCam] = useState(null);
  const [isSystemLive, setIsSystemLive] = useState(false);

  // Form State
  const [newCamId, setNewCamId] = useState('');
  const [newCamUrl, setNewCamUrl] = useState('');

  const ws = useRef(null);

  // Initialize Data & WebSocket
  useEffect(() => {
    fetchInitialData();
    connectWebSocket();

    return () => {
      if (ws.current) {
        console.log("[WS] Cleaning up connection");
        const socket = ws.current;
        ws.current = null; // Clear the ref first to prevent onclose from retrying
        socket.close();
      }
    };
  }, []);

  const fetchInitialData = async () => {
    try {
      const cams = await api.listCameras();
      setCameras(cams || []);

      const streams = await api.listStreams();
      setRunningCameras(streams.streams || []);

      const initialAlerts = await api.getAlerts();
      setAlerts(initialAlerts.alerts || []);

      const allZones = await api.listZones();
      setZones(allZones || []);

      setIsSystemLive(true);
    } catch (err) {
      console.error("Failed to fetch initial data", err);
      setIsSystemLive(false);
    }
  };

  const connectWebSocket = () => {
    if (ws.current && (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    console.log("[WS] Connecting to:", WS_URL);
    const socket = new WebSocket(WS_URL);
    ws.current = socket;

    socket.onopen = () => {
      console.log("[WS] Connected to backend");
      setIsSystemLive(true);
    };

    socket.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      console.log("[WS] New Alert:", alert);
      setAlerts(prev => [alert, ...prev.slice(0, 19)]);

      // Play ding sound
      playAlertSound();
    };

    socket.onclose = (event) => {
      // Only retry if this specific socket is still the active one in the ref
      if (ws.current === socket) {
        console.log("[WS] Disconnected, retrying...", event.reason);
        setIsSystemLive(false);
        ws.current = null;
        setTimeout(() => {
          connectWebSocket();
        }, 3000);
      } else {
        console.log("[WS] Closed (intentional or replaced)");
      }
    };

    socket.onerror = (err) => {
      console.error("[WS] Error:", err);
    };
  };

  const handleSaveZone = async (zoneData) => {
    try {
      await api.createZone(zoneData);
      setEditingZoneCam(null);
      fetchInitialData();
    } catch (err) {
      alert("Failed to save zone.");
    }
  };

  const handleDeleteZone = async (id) => {
    if (window.confirm("Delete this zone?")) {
      await api.deleteZone(id);
      fetchInitialData();
    }
  };

  const handleStartCamera = async () => {
    if (!newCamId || !newCamUrl) return;

    try {
      // Start stream automatically (this also initializes the camera in the new backend)
      await api.startStream({
        id: newCamId,
        url: newCamUrl,
        allowed_classes: selectedClasses
      });

      setShowAddCamera(false);
      fetchInitialData(); // Refresh lists
      setNewCamId('');
      setNewCamUrl('');
    } catch (err) {
      alert("Failed to start camera. Check backend logs.");
    }
  };

  const handleStopCamera = async (id) => {
    try {
      await api.stopStream(id);
      fetchInitialData();
    } catch (err) {
      console.error("Failed to stop camera", err);
    }
  };

  const toggleClass = (id) => {
    setSelectedClasses(prev =>
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    );
  };

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <Ship size={24} color="var(--text-primary)" />
          <span>MARINETIME AI</span>
        </div>

        <nav>
          <div
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={20} />
            Dashboard
          </div>
          <div
            className={`nav-item ${activeTab === 'cameras' ? 'active' : ''}`}
            onClick={() => setActiveTab('cameras')}
          >
            <Camera size={20} />
            Cameras
          </div>
          <div
            className={`nav-item ${activeTab === 'alerts' ? 'active' : ''}`}
            onClick={() => setActiveTab('alerts')}
          >
            <Bell size={20} />
            Alerts
          </div>
          <div
            className={`nav-item ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            <Shield size={20} />
            Security Zones
          </div>
          <div
            className={`nav-item ${activeTab === 'yolo' ? 'active' : ''}`}
            onClick={() => setActiveTab('yolo')}
          >
            <Activity size={20} />
            YOLO Detection
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>
              {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
            </h1>
            <div
              className="status-indicator"
              style={{ backgroundColor: isSystemLive ? '#10b981' : '#ef4444' }}
            ></div>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              {isSystemLive ? 'System Online' : 'Connecting...'}
            </span>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', backgroundColor: 'var(--bg-secondary)', padding: '0.25rem', borderRadius: '0.5rem' }}>
            {['raw', 'zones', 'yolo'].map(mode => (
              <button
                key={mode}
                className="btn"
                style={{
                  padding: '0.25rem 0.75rem',
                  fontSize: '0.75rem',
                  backgroundColor: previewMode === mode ? 'var(--bg-primary)' : 'transparent',
                  boxShadow: previewMode === mode ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  fontWeight: previewMode === mode ? 600 : 400
                }}
                onClick={() => setPreviewMode(mode)}
              >
                {mode.toUpperCase()}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              onClick={() => setShowAddCamera(true)}
            >
              <Plus size={18} />
              Add Camera
            </button>
          </div>
        </header>

        <div className="content-area">
          {activeTab === 'dashboard' && (
            <div className="camera-grid">
              {runningCameras.length > 0 ? (
                runningCameras.map(camObj => {
                  const camId = typeof camObj === 'string' ? camObj : (camObj.camera_id || 'unknown'); // Handle both object and string for safety
                  return (
                    <div key={String(camId)} className="card">
                      <div className="card-header">
                        <span style={{ fontWeight: 600 }}>{String(camId)}</span>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <button
                            onClick={() => setEditingZoneCam(camId)}
                            className="btn"
                            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', backgroundColor: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                          >
                            <Shield size={14} /> Zone
                          </button>
                          <Activity size={16} color="#10b981" />
                          <button
                            onClick={() => handleStopCamera(camId)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex' }}
                          >
                            <Power size={16} />
                          </button>
                        </div>
                      </div>
                      <div className="video-container">
                        <img
                          src={
                            previewMode === 'yolo' ? api.getYoloPreviewUrl(camId) :
                              previewMode === 'zones' ? api.getPreviewWithZonesUrl(camId) :
                                api.getPreviewUrl(camId)
                          }
                          alt={String(camId)}
                          style={{ width: '100%', height: '100%', display: 'block' }}
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                        <div style={{ display: 'none', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column', gap: '1rem' }}>
                          <Camera size={48} color="#3f3f46" />
                          <span style={{ color: '#71717a', fontSize: '0.875rem' }}>Loading Stream...</span>
                        </div>
                      </div>
                    </div>
                  )
                })
              ) : (
                <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                  <Camera size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                  <p>No active camera streams. Click "Add Camera" to start.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'cameras' && (
            <div className="card" style={{ padding: '0' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)' }}>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '1rem 1.5rem' }}>Camera ID</th>
                    <th style={{ textAlign: 'left', padding: '1rem 1.5rem' }}>Status</th>
                    <th style={{ textAlign: 'right', padding: '1rem 1.5rem' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {cameras.map(camObj => {
                    const camId = typeof camObj === 'string' ? camObj : camObj.camera_id;
                    const isRunning = runningCameras.some(c => (c.camera_id || c) === camId);
                    return (
                      <tr key={String(camId)} style={{ borderBottom: '1px solid var(--border)' }}>
                        <td style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>{String(camId)}</td>
                        <td style={{ padding: '1rem 1.5rem' }}>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '1rem',
                            fontSize: '0.75rem',
                            backgroundColor: isRunning ? '#dcfce7' : '#f4f4f5',
                            color: isRunning ? '#166534' : '#71717a'
                          }}>
                            {isRunning ? 'Running' : 'Offline'}
                          </span>
                        </td>
                        <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                          <button
                            onClick={() => isRunning ? handleStopCamera(camId) : api.startStream({ id: camId })}
                            className="btn"
                            style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem', backgroundColor: 'var(--bg-secondary)' }}
                          >
                            {isRunning ? 'Stop' : 'Start'}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div className="alerts-view">
              <div className="filter-header" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem', backgroundColor: 'var(--bg-secondary)', padding: '1rem', borderRadius: '0.5rem' }}>
                <Search size={18} color="var(--text-secondary)" />
                <span style={{ fontWeight: 600 }}>Filter by Camera:</span>
                <select
                  className="form-input"
                  style={{ width: 'auto', padding: '0.4rem 2rem 0.4rem 1rem' }}
                  onChange={async (e) => {
                    const camId = e.target.value;
                    try {
                      if (camId === 'all') {
                        const all = await api.getAlerts();
                        setAlerts(all.alerts || []);
                      } else {
                        const filtered = await api.getAlertsByCamera(camId);
                        setAlerts(filtered.alerts || []);
                      }
                    } catch (err) {
                      console.error("Failed to filter alerts", err);
                    }
                  }}
                >
                  <option value="all">All Cameras</option>
                  {cameras.map(camObj => {
                    const id = typeof camObj === 'string' ? camObj : camObj.camera_id;
                    return <option key={String(id)} value={String(id)}>{String(id)}</option>;
                  })}
                </select>
                <div style={{ marginLeft: 'auto', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                  Total Alerts: {alerts.length}
                </div>
              </div>

              <div className="camera-grid">
                {alerts.length > 0 ? (
                  alerts.map((alert, i) => (
                    <div key={i} className="card">
                      <div className="card-header">
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                          <span style={{ fontWeight: 600 }}>Camera: {String(alert.camera_id?.camera_id || alert.camera_id)}</span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            {alert.timestamp ? new Date(alert.timestamp * 1000).toLocaleString() : 'N/A'}
                          </span>
                        </div>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: '1rem',
                          fontSize: '0.75rem',
                          backgroundColor: '#fee2e2',
                          color: '#991b1b',
                          fontWeight: 600
                        }}>
                          Capture #{alert.object_id}
                        </span>
                      </div>
                      <div className="video-container">
                        <img
                          src={api.getAlertImageUrl(alert.image)}
                          alt="Alert Snapshot"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                        <div style={{ display: 'none', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column', gap: '1rem' }}>
                          <Camera size={48} color="#3f3f46" />
                          <span style={{ color: '#71717a', fontSize: '0.875rem' }}>Image Not Found</span>
                        </div>
                      </div>
                      <div style={{ padding: '1rem', borderTop: '1px solid var(--border)' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Shield size={16} color="var(--text-secondary)" />
                            <span style={{ fontSize: '0.875rem' }}>Zone: <strong>{String(alert.zone_id || 'Global')}</strong></span>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#3b82f6', fontSize: '0.8rem', fontWeight: 600 }}>
                            <Ship size={14} />
                            <span>{getPlaceName(alert.lat, alert.lon)}</span>
                          </div>
                          {(alert.lat !== undefined && alert.lon !== undefined) && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                              <Activity size={14} />
                              <span>Lat: <strong>{alert.lat?.toFixed(6)}</strong></span>
                              <span>Long: <strong>{alert.lon?.toFixed(6)}</strong></span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                    <Bell size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                    <p>No alerts found matching the criteria.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="card" style={{ padding: '0' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ backgroundColor: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)' }}>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '1rem 1.5rem' }}>Zone Name</th>
                    <th style={{ textAlign: 'left', padding: '1rem 1.5rem' }}>Camera</th>
                    <th style={{ textAlign: 'left', padding: '1rem 1.5rem' }}>Points</th>
                    <th style={{ textAlign: 'right', padding: '1rem 1.5rem' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {zones.map(zone => (
                    <tr key={zone.id} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>{zone.name}</td>
                      <td style={{ padding: '1rem 1.5rem' }}>{zone.camera_id?.camera_id || zone.camera_id}</td>
                      <td style={{ padding: '1rem 1.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        {zone.points.length} points
                      </td>
                      <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                        <button
                          onClick={() => handleDeleteZone(zone.id)}
                          className="btn"
                          style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem', backgroundColor: '#fee2e2', color: '#991b1b' }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {zones.length === 0 && (
                    <tr>
                      <td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        No zones defined. Open a camera to draw one.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'yolo' && (
            <div className="camera-grid">
              {runningCameras.length > 0 ? (
                runningCameras.map(camObj => {
                  const camId = typeof camObj === 'string' ? camObj : (camObj.camera_id || 'unknown');
                  return (
                    <div key={String(camId)} className="card">
                      <div className="card-header">
                        <span style={{ fontWeight: 600 }}>{String(camId)} - YOLO DETECT</span>
                      </div>
                      <div className="video-container">
                        <img
                          src={api.getYoloPreviewUrl(camId)}
                          alt={String(camId)}
                          style={{ width: '100%', height: '100%', display: 'block' }}
                        />
                      </div>
                    </div>
                  );
                })
              ) : (
                <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
                  <Activity size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                  <p>No active streams to monitor YOLO detections.</p>
                </div>
              )}
            </div>
          )}

          {showAddCamera && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
              <div className="card" style={{ width: '500px', padding: '2rem' }}>
                <h2 style={{ marginBottom: '1.5rem' }}>Configure New Camera</h2>
                <div className="form-group">
                  <label>Camera ID</label>
                  <input
                    className="form-input"
                    placeholder="e.g. cam1"
                    value={newCamId}
                    onChange={(e) => setNewCamId(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>RTSP URL</label>
                  <input
                    className="form-input"
                    placeholder="rtsp://localhost:8554/..."
                    value={newCamUrl}
                    onChange={(e) => setNewCamUrl(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Allowed Objects (YOLO Classes)</label>
                  <div className="multi-select">
                    {YOLO_CLASSES.map(cls => (
                      <label key={cls} className="checkbox-item">
                        <input
                          type="checkbox"
                          checked={selectedClasses.includes(cls)}
                          onChange={() => toggleClass(cls)}
                        />
                        {cls.charAt(0).toUpperCase() + cls.slice(1)}
                      </label>
                    ))}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                  <button className="btn btn-primary" onClick={handleStartCamera}>Start Camera</button>
                  <button
                    className="btn"
                    style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border)' }}
                    onClick={() => setShowAddCamera(false)}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
          {editingZoneCam && (
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: '2rem' }}>
              <ZoneEditor
                cameraId={editingZoneCam}
                previewUrl={api.getPreviewWithZonesUrl(editingZoneCam)}
                onSave={handleSaveZone}
                onCancel={() => setEditingZoneCam(null)}
              />
            </div>
          )}
        </div>
      </main>

      {/* Alert Feed */}
      <aside className="alert-panel">
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', fontWeight: 700 }}>
          Live Alert Feed
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 0' }}>
          {alerts.length > 0 ? (
            alerts.map((alert, i) => (
              <div key={i} className="alert-item" style={{
                padding: '1rem',
                borderBottom: '1px solid var(--border)',
                transition: 'background-color 0.2s'
              }}>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <div style={{ position: 'relative' }}>
                    {alert.image ? (
                      <img
                        src={api.getAlertImageUrl(alert.image)}
                        alt="Alert"
                        style={{ width: '100px', height: '75px', objectFit: 'cover', borderRadius: '6px', backgroundColor: '#000', border: '1px solid var(--border)' }}
                      />
                    ) : (
                      <div style={{ width: '100px', height: '75px', backgroundColor: 'var(--bg-secondary)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Camera size={20} color="var(--text-secondary)" />
                      </div>
                    )}
                    <div style={{
                      position: 'absolute',
                      bottom: '4px',
                      right: '4px',
                      backgroundColor: 'rgba(0,0,0,0.6)',
                      color: 'white',
                      fontSize: '0.65rem',
                      padding: '2px 4px',
                      borderRadius: '3px'
                    }}>
                      {alert.camera_id?.camera_id || alert.camera_id}
                    </div>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
                      <span style={{
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        color: alert.type === 'zone_crossing' ? '#ef4444' : '#f59e0b'
                      }}>
                        {alert.event || (alert.type === 'zone_presence' ? 'PRESENCE' : 'ALERT')}
                      </span>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                        {alert.timestamp ? new Date(alert.timestamp * 1000).toLocaleTimeString() : 'Just now'}
                      </span>
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {String(alert.object || 'Object')} #{alert.object_id}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                      <div style={{ color: '#3b82f6', fontWeight: 600, fontSize: '0.7rem' }}>{getPlaceName(alert.lat, alert.lon)}</div>
                      <div>Zone: <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{String(alert.zone_id || 'Global')}</span></div>
                      {(alert.lat !== undefined && alert.lon !== undefined) && (
                        <div style={{ color: 'var(--text-primary)', fontWeight: 500, display: 'flex', gap: '0.5rem' }}>
                          <span>L: {alert.lat?.toFixed(4)}</span>
                          <span>G: {alert.lon?.toFixed(4)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              No recent alerts
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}

export default App;
