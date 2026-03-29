import React, { useState, useEffect, useRef } from 'react';
import { Stage, Layer, Line, Circle, Text } from 'react-konva';

const YOLO_CLASSES = ["person", "car", "motorcycle", "bus", "truck", "boat", "bird", "ship"];

const ZoneEditor = ({ cameraId, previewUrl, onSave, onCancel }) => {
    const [points, setPoints] = useState([]);
    const [isClosed, setIsClosed] = useState(false);
    const [zoneName, setZoneName] = useState('restricted_area');
    const [allowedClasses, setAllowedClasses] = useState(["ship", "boat"]);
    const containerRef = useRef(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    useEffect(() => {
        if (containerRef.current) {
            const { offsetWidth } = containerRef.current;
            // We force 16:9 for consistent normalization
            setDimensions({ width: offsetWidth, height: offsetWidth * 9 / 16 });
        }
    }, []);

    const handleCanvasClick = (e) => {
        if (isClosed) return;

        const stage = e.target.getStage();
        const point = stage.getPointerPosition();

        // Check if clicking near first point to close
        if (points.length >= 3) {
            const firstPoint = points[0];
            const dist = Math.sqrt(
                Math.pow(point.x - firstPoint[0], 2) + Math.pow(point.y - firstPoint[1], 2)
            );
            if (dist < 15) {
                setIsClosed(true);
                return;
            }
        }

        setPoints([...points, [point.x, point.y]]);
    };

    const handlePointDrag = (index, e) => {
        const newPoints = [...points];
        newPoints[index] = [e.target.x(), e.target.y()];
        setPoints(newPoints);
    };

    const handleSave = () => {
        if (!isClosed || points.length < 3) {
            alert("Please draw a closed polygon with at least 3 points.");
            return;
        }

        const zoneId = `zone_${Date.now()}`;

        // Normalize points (0.0 to 1.0)
        const normalizedPoints = points.map(p => [
            parseFloat((p[0] / dimensions.width).toFixed(4)),
            parseFloat((p[1] / dimensions.height).toFixed(4))
        ]);

        onSave({
            id: zoneId,
            camera_id: cameraId,
            name: zoneName,
            points: normalizedPoints,
            allowed_classes: allowedClasses
        });
    };

    const reset = () => {
        setPoints([]);
        setIsClosed(false);
    };

    const toggleClass = (cls) => {
        setAllowedClasses(prev =>
            prev.includes(cls) ? prev.filter(c => c !== cls) : [...prev, cls]
        );
    };

    // Flatten points for Konva Line [x1, y1, x2, y2...]
    const flattenedPoints = points.reduce((acc, curr) => [...acc, ...curr], []);

    return (
        <div className="card" style={{ maxWidth: '800px', width: '100%', margin: '0 auto', maxHeight: '95vh', overflowY: 'auto' }}>
            <div className="card-header">
                <span style={{ fontWeight: 600 }}>Zone Editor - {cameraId}</span>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                    Click to add points. Click first point to close.
                </div>
            </div>

            <div
                ref={containerRef}
                style={{
                    position: 'relative',
                    width: '100%',
                    aspectRatio: '16/9',
                    backgroundColor: '#000',
                    cursor: isClosed ? 'default' : 'crosshair'
                }}
            >
                <img
                    src={previewUrl}
                    alt="Preview"
                    style={{ width: '100%', height: '100%', position: 'absolute', opacity: 1.0 }}
                />

                <Stage
                    width={dimensions.width}
                    height={dimensions.height}
                    onClick={handleCanvasClick}
                    style={{ position: 'absolute', top: 0, left: 0 }}
                >
                    <Layer>
                        <Line
                            points={flattenedPoints}
                            stroke="#2563eb"
                            strokeWidth={3}
                            fill="rgba(37, 99, 235, 0.2)"
                            closed={isClosed}
                        />

                        {points.map((p, i) => (
                            <Circle
                                key={i}
                                x={p[0]}
                                y={p[1]}
                                radius={i === 0 && !isClosed ? 8 : 5}
                                fill={i === 0 && !isClosed ? "#ef4444" : "#2563eb"}
                                draggable={isClosed}
                                onDragMove={(e) => handlePointDrag(i, e)}
                                stroke="#fff"
                                strokeWidth={2}
                            />
                        ))}

                        {isClosed && (
                            <Text
                                x={points[0][0]}
                                y={points[0][1] - 25}
                                text={zoneName}
                                fill="#fff"
                                fontSize={14}
                                fontStyle="bold"
                            />
                        )}
                    </Layer>
                </Stage>
            </div>

            <div style={{ padding: '1.5rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                    <div className="form-group">
                        <label>Zone Name</label>
                        <input
                            className="form-input"
                            value={zoneName}
                            onChange={(e) => setZoneName(e.target.value)}
                            disabled={!isClosed}
                        />
                    </div>

                    <div className="form-group">
                        <label>Detection Objects</label>
                        <div className="multi-select" style={{ maxHeight: '100px', overflowY: 'auto', border: '1px solid var(--border)', padding: '0.5rem', borderRadius: '0.375rem' }}>
                            {YOLO_CLASSES.map(cls => (
                                <label key={cls} className="checkbox-item" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                                    <input
                                        type="checkbox"
                                        checked={allowedClasses.includes(cls)}
                                        onChange={() => toggleClass(cls)}
                                    />
                                    {cls.charAt(0).toUpperCase() + cls.slice(1)}
                                </label>
                            ))}
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                        className="btn btn-primary"
                        onClick={handleSave}
                        disabled={!isClosed}
                    >
                        Save Zone
                    </button>
                    <button
                        className="btn"
                        style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border)' }}
                        onClick={reset}
                    >
                        Reset
                    </button>
                    <button
                        className="btn"
                        style={{ backgroundColor: 'transparent', color: 'var(--text-secondary)' }}
                        onClick={onCancel}
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ZoneEditor;
